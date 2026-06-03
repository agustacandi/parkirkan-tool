from gpiozero import Servo
from time import sleep

from config import SERVO_GPIO

servo = Servo(SERVO_GPIO)


def open_gate():

    print("OPENING GATE...")

    servo.max()

    sleep(2)

    servo.min()

    print("GATE CLOSED")