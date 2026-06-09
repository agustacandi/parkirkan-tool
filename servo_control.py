# from gpiozero import Servo
# from time import sleep
#
# from config import SERVO_GPIO
#
# servo = Servo(SERVO_GPIO)
#
#
# def open_gate():
#
#     print("OPENING GATE...")
#
#     servo.max()
#
#     sleep(2)
#
#     servo.min()
#
#     print("GATE CLOSED")

from gpiozero import AngularServo
from time import sleep

servo = AngularServo(
    18,
    min_angle=0,
    max_angle=90
)


def open_gate():
    servo.angle = 90
    sleep(3)

    servo.angle = 0
    sleep(1)