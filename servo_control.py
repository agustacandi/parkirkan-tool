from gpiozero import AngularServo
from time import sleep

servo = AngularServo(
    18,
    min_angle=0,
    max_angle=90,
    initial_angle=None,
)


def open_gate():
    servo.angle = 90
    sleep(3)

    servo.angle = 0
    sleep(1)
