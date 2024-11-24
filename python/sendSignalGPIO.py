import RPi.GPIO as GPIO
import time
import rwPulseCoinValue

def sendOutputSignal(price):
    
    print("SCRIPT TO SEND SIGNAL CALL")
    print(price)
    
    # pulse_coin_value = 0.25 # Old implementation - constant value of pulse coin
    pulse_coin_value = rwPulseCoinValue.readPulseCoinValue()
    
    number_of_pulses = round(price/pulse_coin_value)

    # New implementation in case pulse value is higher than price step
    if price % pulse_coin_value > 0.1 and number_of_pulses < price/pulse_coin_value :
        number_of_pulses = number_of_pulses + 1

    # msPulse = 50 and msBetweenPulses = 200 ocasionally fails -> do not use
    # msPulse = 100 and msBetweenPulses = 400 works perfectly but is a bit too slow
    # test with msPulse = 80 and msBetweenPulses = 300?

    msPulse = 100
    msBetweenPulses = 400
    
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    
    for i in range(number_of_pulses):
        
        GPIO.output(26, GPIO.HIGH)
        time.sleep(msPulse/1000)
        GPIO.output(26, GPIO.LOW)
        time.sleep(msBetweenPulses/1000)
        
        print("pulsetest")
        
    GPIO.cleanup()
        
    print("End of GPIO pulse")
    
    
