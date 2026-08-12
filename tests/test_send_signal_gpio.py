import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))


class FakeGPIO(types.ModuleType):
    BCM = "BCM"
    OUT = "OUT"
    LOW = 0
    HIGH = 1

    def __init__(self):
        super().__init__("RPi.GPIO")
        self.outputs = []
        self.failures = []

    def setmode(self, _mode):
        return None

    def setup(self, pin, mode, initial=None):
        self.outputs.append((pin, initial))

    def output(self, pin, value):
        self.outputs.append((pin, value))
        if self.failures and self.failures[0] == (len(self.outputs), value):
            self.failures.pop(0)
            raise RuntimeError("gpio failure")


fake_gpio = FakeGPIO()
rpi_package = types.ModuleType("RPi")
rpi_package.GPIO = fake_gpio
sys.modules["RPi"] = rpi_package
sys.modules["RPi.GPIO"] = fake_gpio

import sendSignalGPIO


class SendSignalGPIOTests(unittest.TestCase):
    def setUp(self):
        fake_gpio.outputs.clear()
        fake_gpio.failures.clear()
        sendSignalGPIO.gpio_listener_pause.clear()

    def test_plan_rounds_up_to_avoid_undercredit(self):
        with patch.object(
            sendSignalGPIO.rwPulseCoinValue,
            "readPulseCharacteristics",
            return_value=(0.25, 100, 400),
        ):
            plan = sendSignalGPIO.build_pulse_plan("1.49")

        self.assertEqual(plan.number_of_pulses, 6)
        self.assertEqual(plan.expected_duration_seconds, 3)

    def test_success_returns_completed_count_and_finishes_low(self):
        plan = sendSignalGPIO.PulsePlan(2, 100, 400)
        with patch.object(sendSignalGPIO.time, "sleep"), patch.object(
            sendSignalGPIO.time,
            "monotonic",
            side_effect=(10, 11),
        ):
            result = sendSignalGPIO.sendOutputSignal("0.50", plan=plan)

        self.assertEqual(result.expected_pulses, 2)
        self.assertEqual(result.completed_pulses, 2)
        self.assertEqual(result.retried_pulses, 0)
        self.assertEqual(fake_gpio.outputs[-1], (sendSignalGPIO.PULSE_OUTPUT_PIN, 0))
        self.assertFalse(sendSignalGPIO.gpio_listener_pause.is_set())

    def test_uncertain_pulse_is_retried_once(self):
        plan = sendSignalGPIO.PulsePlan(1, 100, 400)
        original_output = fake_gpio.output
        high_calls = 0

        def fail_first_high(pin, value):
            nonlocal high_calls
            fake_gpio.outputs.append((pin, value))
            if value == fake_gpio.HIGH:
                high_calls += 1
                if high_calls == 1:
                    raise RuntimeError("uncertain high")

        fake_gpio.output = fail_first_high
        try:
            with patch.object(sendSignalGPIO.time, "sleep"), patch.object(
                sendSignalGPIO.time,
                "monotonic",
                side_effect=(10, 11),
            ):
                result = sendSignalGPIO.sendOutputSignal("0.25", plan=plan)
        finally:
            fake_gpio.output = original_output

        self.assertEqual(result.completed_pulses, 1)
        self.assertEqual(result.retried_pulses, 1)
        self.assertEqual(fake_gpio.outputs[-1], (sendSignalGPIO.PULSE_OUTPUT_PIN, 0))

    def test_second_failure_stops_and_forces_low(self):
        plan = sendSignalGPIO.PulsePlan(2, 100, 400)
        original_output = fake_gpio.output

        def always_fail_high(pin, value):
            fake_gpio.outputs.append((pin, value))
            if value == fake_gpio.HIGH:
                raise RuntimeError("persistent failure")

        fake_gpio.output = always_fail_high
        try:
            with patch.object(sendSignalGPIO.time, "sleep"):
                with self.assertRaises(sendSignalGPIO.PulseDeliveryError) as raised:
                    sendSignalGPIO.sendOutputSignal("0.50", plan=plan)
        finally:
            fake_gpio.output = original_output

        self.assertEqual(raised.exception.expected_pulses, 2)
        self.assertEqual(raised.exception.completed_pulses, 0)
        self.assertEqual(raised.exception.retried_pulses, 1)
        self.assertEqual(fake_gpio.outputs[-1], (sendSignalGPIO.PULSE_OUTPUT_PIN, 0))
        self.assertFalse(sendSignalGPIO.gpio_listener_pause.is_set())

    def test_interval_failure_preserves_completed_pulse_count(self):
        plan = sendSignalGPIO.PulsePlan(2, 100, 400)
        with patch.object(
            sendSignalGPIO.time,
            "sleep",
            side_effect=(None, RuntimeError("sleep interrupted")),
        ):
            with self.assertRaises(sendSignalGPIO.PulseDeliveryError) as raised:
                sendSignalGPIO.sendOutputSignal("0.50", plan=plan)

        self.assertEqual(raised.exception.completed_pulses, 1)
        self.assertEqual(fake_gpio.outputs[-1], (sendSignalGPIO.PULSE_OUTPUT_PIN, 0))

    def test_setup_failure_still_attempts_to_force_output_low(self):
        plan = sendSignalGPIO.PulsePlan(1, 100, 400)
        with patch.object(
            fake_gpio,
            "setup",
            side_effect=RuntimeError("setup failure"),
        ), patch.object(fake_gpio, "output", wraps=fake_gpio.output) as output:
            with self.assertRaises(sendSignalGPIO.PulseDeliveryError):
                sendSignalGPIO.sendOutputSignal("0.25", plan=plan)

        output.assert_called_with(sendSignalGPIO.PULSE_OUTPUT_PIN, fake_gpio.LOW)
        self.assertFalse(sendSignalGPIO.gpio_listener_pause.is_set())


if __name__ == "__main__":
    unittest.main()
