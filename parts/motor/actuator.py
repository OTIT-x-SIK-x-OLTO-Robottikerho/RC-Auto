from gpiozero import Motor
from time import sleep, time

# DRI0041 motor driver pins (BCM numbering)
ENABLE_PIN = 17
FORWARD_PIN = 27
BACKWARD_PIN = 22


def spin_motor_forward_and_backwards():
    # The Pi drives the DRI0041's inputs; the driver powers the motor.
    # enable is held high, speed is set with PWM on the forward/backward pins.
    motor: Motor = Motor(forward=FORWARD_PIN, backward=BACKWARD_PIN, enable=ENABLE_PIN)
    end_time = time() + 20  # run for 20 seconds (2 forward/backward cycles)
    try:
        while time() < end_time:
            # direction switches immediately, no stop() in between
            motor.forward()
            print("forward")
            sleep(5)
            motor.backward()
            print("backwards")
            sleep(5)
    finally:
        motor.stop()
        motor.close()


if __name__ == "__main__":
    spin_motor_forward_and_backwards()
