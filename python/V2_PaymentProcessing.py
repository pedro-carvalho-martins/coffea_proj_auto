def launchPaymentProcessing(price, paymentMethod):

    # calculate factorial to simulate processing time
    time.sleep(5)
    print(factorial(50))

import time
def factorial(n):
    print(n)
    if n != 1:
        return n * factorial(n-1)
    else:
        return 1
