from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
import sys
import time

import RPi.GPIO as GPIO

import rwPulseCoinValue
from shared_resource import gpio_lock, gpio_listener_pause


PULSE_OUTPUT_PIN = 26
MAX_RETRIES_PER_PULSE = 1


@dataclass(frozen=True)
class PulsePlan:
    number_of_pulses: int
    pulse_duration_ms: float
    pulse_interval_ms: float

    @property
    def expected_duration_seconds(self):
        return self.number_of_pulses * (
            self.pulse_duration_ms + self.pulse_interval_ms
        ) / 1000


@dataclass(frozen=True)
class PulseDeliveryResult:
    expected_pulses: int
    completed_pulses: int
    retried_pulses: int
    elapsed_seconds: float


class PulseDeliveryError(RuntimeError):
    def __init__(self, message, expected_pulses, completed_pulses, retried_pulses):
        super().__init__(message)
        self.expected_pulses = expected_pulses
        self.completed_pulses = completed_pulses
        self.retried_pulses = retried_pulses


def _money_to_centavos(value, label):
    try:
        normalized = Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{label} invalido") from exc
    centavos = int(normalized * 100)
    if centavos <= 0:
        raise ValueError(f"{label} deve ser maior que zero")
    return centavos


def build_pulse_plan(price):
    pulse_coin_value, pulse_duration_ms, pulse_interval_ms = (
        rwPulseCoinValue.readPulseCharacteristics()
    )
    price_centavos = _money_to_centavos(price, "Valor da venda")
    pulse_centavos = _money_to_centavos(pulse_coin_value, "Valor do pulso")
    number_of_pulses = int(
        (Decimal(price_centavos) / Decimal(pulse_centavos)).to_integral_value(
            rounding=ROUND_CEILING
        )
    )
    pulse_duration_ms = float(pulse_duration_ms)
    pulse_interval_ms = float(pulse_interval_ms)
    if pulse_duration_ms <= 0 or pulse_interval_ms <= 0:
        raise ValueError("Duracao e intervalo dos pulsos devem ser maiores que zero")
    return PulsePlan(number_of_pulses, pulse_duration_ms, pulse_interval_ms)


def _force_output_low():
    GPIO.output(PULSE_OUTPUT_PIN, GPIO.LOW)


def sendOutputSignal(price, plan=None):
    plan = plan or build_pulse_plan(price)
    completed_pulses = 0
    retried_pulses = 0
    started_at = time.monotonic()
    gpio_listener_pause.set()

    try:
        with gpio_lock:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(PULSE_OUTPUT_PIN, GPIO.OUT, initial=GPIO.LOW)

                for pulse_index in range(plan.number_of_pulses):
                    for attempt in range(MAX_RETRIES_PER_PULSE + 1):
                        try:
                            GPIO.output(PULSE_OUTPUT_PIN, GPIO.HIGH)
                            time.sleep(plan.pulse_duration_ms / 1000)
                            GPIO.output(PULSE_OUTPUT_PIN, GPIO.LOW)
                            completed_pulses += 1
                            break
                        except Exception as exc:
                            try:
                                _force_output_low()
                            except Exception:
                                pass
                            if attempt >= MAX_RETRIES_PER_PULSE:
                                raise PulseDeliveryError(
                                    f"Falha ao transmitir o pulso {pulse_index + 1}",
                                    plan.number_of_pulses,
                                    completed_pulses,
                                    retried_pulses,
                                ) from exc
                            retried_pulses += 1
                            time.sleep(plan.pulse_interval_ms / 1000)

                    time.sleep(plan.pulse_interval_ms / 1000)
            finally:
                active_error = sys.exc_info()[0] is not None
                try:
                    _force_output_low()
                except Exception as cleanup_error:
                    if not active_error:
                        raise PulseDeliveryError(
                            "Nao foi possivel garantir o nivel baixo da saida de pulso",
                            plan.number_of_pulses,
                            completed_pulses,
                            retried_pulses,
                        ) from cleanup_error
    except PulseDeliveryError:
        raise
    except Exception as exc:
        raise PulseDeliveryError(
            "Falha durante a sequencia de pulsos",
            plan.number_of_pulses,
            completed_pulses,
            retried_pulses,
        ) from exc
    finally:
        gpio_listener_pause.clear()

    return PulseDeliveryResult(
        expected_pulses=plan.number_of_pulses,
        completed_pulses=completed_pulses,
        retried_pulses=retried_pulses,
        elapsed_seconds=max(0, time.monotonic() - started_at),
    )
