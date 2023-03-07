import RPi.GPIO as GPIO
import time

def sendOutputSignal(price):
    
    print("SCRIPT TO SEND SIGNAL CALL")
    print(price)
    
    pulse_coin_value = 0.25
    
    number_of_pulses = round(price/pulse_coin_value)
    
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
    
    
