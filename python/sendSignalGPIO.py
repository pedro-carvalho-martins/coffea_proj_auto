import RPi.GPIO as GPIO
import time
import rwPulseCoinValue

from shared_resource import gpio_lock, gpio_listener_pause


PULSE_OUTPUT_PIN = 26

def sendOutputSignal(price):
    print("SCRIPT TO SEND SIGNAL CALL")
    print(price)

    # pulse_coin_value = 0.25 # Old implementation - constant value of pulse coin
    # msPulse = 50 and msBetweenPulses = 200 ocasionally fails -> do not use
    # msPulse = 100 and msBetweenPulses = 400 works perfectly but is a bit too slow
    # test with msPulse = 80 and msBetweenPulses = 300?
    pulse_coin_value, msPulse, msBetweenPulses = rwPulseCoinValue.readPulseCharacteristics()

    number_of_pulses = round(price/pulse_coin_value)

    # New implementation in case pulse value is higher than price step
    if price % pulse_coin_value > 0.1 and number_of_pulses < price/pulse_coin_value :
        number_of_pulses = number_of_pulses + 1

    gpio_listener_pause.set()

    try:
        with gpio_lock:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PULSE_OUTPUT_PIN, GPIO.OUT, initial=GPIO.LOW)

            for i in range(number_of_pulses):
                GPIO.output(PULSE_OUTPUT_PIN, GPIO.HIGH)
                time.sleep(msPulse/1000)
                GPIO.output(PULSE_OUTPUT_PIN, GPIO.LOW)
                time.sleep(msBetweenPulses/1000)

                print("pulsetest")
    finally:
        gpio_listener_pause.clear()

    print("End of GPIO pulse")
