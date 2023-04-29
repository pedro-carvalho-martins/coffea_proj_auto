import RPi.GPIO as GPIO
import time

def listenGPIO():
    
    print("SCRIPT TO LISTEN TO INHIBIT AND SETTINGS GPIO SIGNAL")

    GPIO.setmode(GPIO.BCM)

    # INHIBIT SIGNAL INPUT
    GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    # SETTINGS SIGNAL INPUT
    GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

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


def inhibitEndListenGPIO():
    print("SCRIPT TO DETECT WHEN INHIBIT SIGNAL IS OVER")

    GPIO.setmode(GPIO.BCM)

    # INHIBIT SIGNAL INPUT
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    inhibit_end_listener_outcome = "no"

    while True:
        if (GPIO.input(16) == 0):
            print('inhibit ends')
            inhibit_end_listener_outcome = "inhibit ends"
            break

    GPIO.cleanup()

    print("End of listener")
    print(inhibit_end_listener_outcome)
    return inhibit_end_listener_outcome

