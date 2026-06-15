import os
os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"

from gpiozero import AngularServo
from time import sleep

from config import SERVO_GPIO

def open_gate():
    servo = AngularServo(
        SERVO_GPIO,
        min_angle=0,
        max_angle=90,
        initial_angle=None,
    )

    servo.angle = 90
    sleep(3)

    servo.angle = 0
    sleep(1)

    servo.detach()
    servo.close()
