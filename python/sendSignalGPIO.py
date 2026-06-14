import RPi.GPIO as GPIO
import time
import rwPulseCoinValue
from shared_resource import gpio_lock

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

    with gpio_lock:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(26, GPIO.LOW)

        try:
            for i in range(number_of_pulses):
                GPIO.output(26, GPIO.HIGH)
                time.sleep(msPulse/1000)
                GPIO.output(26, GPIO.LOW)
                time.sleep(msBetweenPulses/1000)

                print("pulsetest")
        finally:
            # Leave the output in a known state even if the pulse loop is interrupted.
            GPIO.output(26, GPIO.LOW)

    print("End of GPIO pulse")
    
    
