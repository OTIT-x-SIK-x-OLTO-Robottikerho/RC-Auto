from gpiozero import Motor
from time import sleep, time


def spin_motor_forward_and_backwards():
    motor : Motor = Motor(forward=4, backward= 14);
    end_time = time() + 4  # run for 4 seconds
    while time() < end_time:
        motor.forward()
        sleep(1)
        motor.backward()
        sleep(1)
    motor.stop()
