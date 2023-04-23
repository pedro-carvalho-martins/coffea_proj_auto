import RPi.GPIO as GPIO
import time

def listenGPIO():
    
    print("SCRIPT TO LISTEN TO INHIBIT AND SETTINGS GPIO SIGNAL")

    GPIO.setmode(GPIO.BCM)

    # INHIBIT SIGNAL INPUT
    GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD.DOWN)

    # SETTINGS SIGNAL INPUT
    GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD.DOWN)

    # VOLTAGE SOURCE FOR SETTINGS SIGNAL INPUT
    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.HIGH)

    listener_outcome = "no"

    while True:
        if(GPIO.input(20)==1):
            print('settings pressionado')
            listener_outcome = "settings"
            break

        elif(GPIO.input(16)==1):
            print('inhibit acionado')
            listener_outcome = "inhibit"
            break

        else:
            print('no signal detected')
        time.sleep(1)
        
    GPIO.cleanup()
        
    print("End of listener")
    print(listener_outcome)
    return listener_outcome
    
    
