import RPi.GPIO as GPIO
import time
import cwiid
import threading
from multiprocessing import Process
import sys

buttonPin = {"left": 16, "behind": 21, "right": 12}
prev_state = {"left": 1, "behind": 1, "right": 1}
led = Led(11)

busy = False
stop = False
leftmotor = [2, 3, 4, 17]
rightmotor = [27, 22, 10, 9]

halfstep_seq_left = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1]
]
halfstep_seq_right = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

button_delay = 0.1
state_button = {"up": "released", "down": "released", "right": "released", "left": "released"}

wii = None
control = True


def setup():
    global buttonPin
    GPIO.setup(buttonPin["left"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonPin["behind"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonPin["right"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

def setup_motor():
    for pin in leftmotor:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    for pin in rightmotor:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)


def button_left():
    event = False
    # read the current button states
    # the curr_state can be '0' (if button pressed) or '1' (if button released)
    curr_state_left = GPIO.input(buttonPin["left"])

    if curr_state_left != prev_state["left"]:  # state changed from '1' to '0' or from '0' to '1'
        if curr_state_left == 1:  # button changed from pressed ('0') to released ('1')
            event = False
        else:  # button changed from released ('1') to pressed ('0')
            event = True
        prev_state["left"] = curr_state_left  # store current state
    time.sleep(0.02)
    return event


def button_behind():
    event = False
    # read the current button states
    # the curr_state can be '0' (if button pressed) or '1' (if button released)
    curr_state_behind = GPIO.input(buttonPin["behind"])

    if curr_state_behind != prev_state["behind"]:  # state changed from '1' to '0' or from '0' to '1'
        if curr_state_behind == 1:  # button changed from pressed ('0') to released ('1')
            event = True
        else:  # button changed from released ('1') to pressed ('0')
            event = False
        prev_state["behind"] = curr_state_behind  # store current state
    time.sleep(0.02)
    return event


def button_right():
    event = False
    # read the current button states
    # the curr_state can be '0' (if button pressed) or '1' (if button released)
    curr_state_right = GPIO.input(buttonPin["right"])

    if curr_state_right != prev_state["right"]:  # state changed from '1' to '0' or from '0' to '1'
        if curr_state_right == 1:  # button changed from pressed ('0') to released ('1')
            event = False
        else:  # button changed from released ('1') to pressed ('0')
            event = True
        prev_state["right"] = curr_state_right  # store current state
    time.sleep(0.02)
    return event


def setcontrol(boolean):
    global control
    control = boolean


def forward():
    global stop
    globals()["busy"] = True
    for i in range(64):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_left[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_right[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def backward():
    global stop
    globals()["busy"] = True
    for i in range(512):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_right[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_left[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def backward_little():
    global stop
    globals()["busy"] = True
    for i in range(128):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_right[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_left[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def left():
    global stop
    globals()["busy"] = True
    for i in range(400):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_right[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_right[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def right():
    global stop
    globals()["busy"] = True
    for i in range(400):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_left[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_left[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def left_little():
    global stop
    globals()["busy"] = True
    for i in range(256):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_right[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_right[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def right_little():
    global stop
    globals()["busy"] = True
    for i in range(256):
        if stop:
            stop = False
            break
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(leftmotor[pin], halfstep_seq_left[halfstep][pin])
                GPIO.output(rightmotor[pin], halfstep_seq_left[halfstep][pin])
            time.sleep(0.001)
    globals()["busy"] = False


def action_left():
    print("OH NOO you hit something, moving back and right")
    backward() # .backward()
    right() # .right()


def action_right():
    print("OH NOO you hit something, moving back and left")
    backward() # .backward()
    left() # .left()


def action_behind():
    # led.balloonPoppedLED(True) and .balloonPopped()
    driving = True
    print("The balloon is popped NOOOOO")
    should_break = False
    while not button_left() or not button_right():
        print("Retreating......")
        forward()
        while button_left():
            backward_little()
            right_little()
            should_break = True
            break
        while button_right():
            backward_little()
            left_little()
            should_break = True
            break
        if should_break:
            # led.balloonPoppedLED(False)
            driving = False
            break
    return driving


def wiistart():
    global wii
    print('Press 1 + 2 on your Wii Remote now ...')
    time.sleep(1)

    # Connect to the Wii Remote. If it times out
    # then quit.
    try:
        wii = cwiid.Wiimote()
    except RuntimeError:
        print("Error opening wiimote connection")
        quit()

    print('Wii Remote connected...\n')
    print('Press some buttons!\n')
    print('Press PLUS and MINUS together to disconnect and quit.\n')

    wii.rpt_mode = cwiid.RPT_BTN


def wii_buttons():
    global stop
    buttons = wii.state['buttons']

    # If Plus and Minus buttons pressed
    # together then rumble and quit.
    if buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0:
        print('\nClosing connection ...')
        wii.rumble = 1
        time.sleep(1)
        wii.rumble = 0
        exit(wii)

    # Check if other buttons are pressed by
    # doing a bitwise AND of the buttons number
    # and the predefined constant for that button.
    if buttons & cwiid.BTN_LEFT:
        current_state_button = "pressed"
        if state_button["left"] != current_state_button:
            setcontrol(False)
            stop = True
            time.sleep(0.03)
            left()
            setcontrol(True)
            print('Left pressed')
            time.sleep(button_delay)
        # state_button["left"] = current_state_button

    if buttons & cwiid.BTN_RIGHT:
        current_state_button = "pressed"
        if state_button["right"] != current_state_button:
            setcontrol(False)
            stop = True
            time.sleep(0.03)
            right()
            setcontrol(True)
            print('Right pressed')
            time.sleep(button_delay)
        # state_button["right"] = current_state_button

    if buttons & cwiid.BTN_UP:
        current_state_button = "pressed"
        if state_button["up"] != current_state_button:
            setcontrol(False)
            stop = True
            time.sleep(0.03)
            forward()
            setcontrol(True)
            print('Up pressed')
            time.sleep(button_delay)
        # state_button["up"] = current_state_button

    if buttons & cwiid.BTN_DOWN:
        current_state_button = "pressed"
        if state_button["down"] != current_state_button:
            setcontrol(False)
            stop = True
            time.sleep(0.03)
            backward()
            setcontrol(True)
            print('Down pressed')
            time.sleep(button_delay)
        # state_button["up"] = current_state_button

    if buttons & cwiid.BTN_MINUS:
        print('Minus Button pressed')
        time.sleep(button_delay)

    if buttons & cwiid.BTN_PLUS:
        print('Plus Button pressed')
        time.sleep(button_delay)


def wiimote():
    while True:
        wii_buttons()
        time.sleep(0.02)

def ledFlash(pin):
    GPIO.setup(pin,GPIO.OUT)
    while True:
        GPIO.output(pin,True)
        time.sleep(10)
        GPIO.output(pin,False)
        time.sleep(10)
        
def ledBlink(pin):
    GPIO.setup(pin,GPIO.OUT)
    while True:
        GPIO.output(pin,True)
        time.sleep(0.1)
        GPIO.output(pin,False)
        time.sleep(0.1)
def leduit(pin):
    GPIO.setup(pin,GPIO.OUT)
    while True:
        GPIO.output(pin,False)
         time.sleep(0.2)

def main():
    global control
    global busy
    global stop
    global wiiremote
    driving = True

    GPIO.setmode(GPIO.BCM)
    setup()
    setup_motor()

    p1 = Process(target=ledFlash(11))
    p1.start()

    wiistart()
    wiiremote = threading.Thread(target=wiimote, args=())
    wiiremote.daemon = True
    wiiremote.start()

    while driving:
        while control:
            if button_left():
                if control:
                    action_left()
                    ledBlink().start()
            elif button_behind():
                if control:
                    driving = action_behind()
                    ledFlash().start() = False
                    break
            elif button_right():
                if control:
                    action_right()
                    ledBlink().start()
            else:
                if control:
                    print("Vroem....")
                    forward() 
                    ledFlash().start()
        else:
            time.sleep(0.1)
    GPIO.cleanup()


if __name__ == "__main__":
    main()
