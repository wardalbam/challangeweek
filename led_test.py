#
import RPi as GPIO
import time
GPIO.setmode(GPIO.BCM)
pin = 11


def led_flash():
    GPIO.setup(pin,GPIO.OUT)
    while True:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(10)
        GPIO.output(pin. GPIO.LOW)
        time.sleep(1)
def main():
    led_flash()
        
        
        

    
