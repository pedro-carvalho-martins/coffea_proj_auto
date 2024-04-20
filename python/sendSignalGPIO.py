import RPi.GPIO as GPIO
import time

def sendOutputSignal(price):
    
    print("SCRIPT TO SEND SIGNAL CALL")
    print(price)
    
    pulse_coin_value = 0.25
    
    number_of_pulses = round(price/pulse_coin_value)

    # msPulse = 50 and msBetweenPulses = 200 ocasionally fails -> do not use
    # msPulse = 100 and msBetweenPulses = 400 works perfectly but is a bit too slow
    # testing with msPulse = 80 and msBetweenPulses = 300:

    msPulse = 80
    msBetweenPulses = 300
    
    
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
    
    
