import RPi.GPIO as GPIO
import time

from shared_resource import gpio_lock, gpio_listener_pause


LISTENER_INPUT_INHIBIT = 16
LISTENER_INPUT_SETTINGS = 20
LISTENER_SETTINGS_VCC = 21
_listener_gpio_initialized = False


def _ensure_listener_gpio_initialized():
    global _listener_gpio_initialized

    if _listener_gpio_initialized:
        return

    print("SCRIPT TO LISTEN TO INHIBIT AND SETTINGS GPIO SIGNAL")
    GPIO.setmode(GPIO.BCM)

    # INHIBIT SIGNAL INPUT
    GPIO.setup(LISTENER_INPUT_INHIBIT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # SETTINGS SIGNAL INPUT
    GPIO.setup(LISTENER_INPUT_SETTINGS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # VOLTAGE SOURCE FOR SETTINGS SIGNAL INPUT
    GPIO.setup(LISTENER_SETTINGS_VCC, GPIO.OUT)
    GPIO.output(LISTENER_SETTINGS_VCC, GPIO.HIGH)

    _listener_gpio_initialized = True


def pollListenerSignal():
    if gpio_listener_pause.is_set():
        return "paused"

    with gpio_lock:
        _ensure_listener_gpio_initialized()

        if GPIO.input(LISTENER_INPUT_SETTINGS) == 1:
            print('settings pressionado')
            return "settings"

        if GPIO.input(LISTENER_INPUT_INHIBIT) == 1:
            print('inhibit acionado')
            return "inhibit"

    return "no"


def listenGPIO():
    while True:
        listener_outcome = pollListenerSignal()

        if listener_outcome != "no":
            print("End of listener")
            print(listener_outcome)
            return listener_outcome

        print('no signal detected')
        time.sleep(1)


def inhibitEndListenGPIO():
    print("SCRIPT TO DETECT WHEN INHIBIT SIGNAL IS OVER")

    inhibit_end_listener_outcome = "no"

    while True:
        time.sleep(3)
        with gpio_lock:
            _ensure_listener_gpio_initialized()
            inhibit_is_active = GPIO.input(LISTENER_INPUT_INHIBIT) == 1

        if inhibit_is_active:
            print('continue inhibit')
        else:
            inhibit_end_listener_outcome = "inhibit ends"
            break

    print("End of listener")
    print(inhibit_end_listener_outcome)
    return inhibit_end_listener_outcome

