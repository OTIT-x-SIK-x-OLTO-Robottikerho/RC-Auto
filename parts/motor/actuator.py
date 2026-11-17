from gpiozero import Motor
from time import sleep, time

# DRI0041 motor driver pins (BCM numbering)
ENABLE_PIN = 17
FORWARD_PIN = 27
BACKWARD_PIN = 22


def pulse(motor: Motor, speed: float, duration: float, ramp: float = 0.5, steps: int = 20) -> None:
    """Run the motor at `speed` for `duration` seconds.

    speed: -1.0 (full backward) .. 1.0 (full forward), 0 = stopped.
           Sets the PWM duty cycle on the forward/backward pin.
    ramp:  seconds to ramp from the current speed to `speed`. A soft start
           avoids the big inrush current that can trip the supply/driver.
    """
    if not -1 <= speed <= 1:
        raise ValueError("speed must be between -1 and 1")
    start = motor.value
    for i in range(1, steps + 1):
        motor.value = start + (speed - start) * i / steps
        sleep(ramp / steps)
    sleep(duration)


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
            sleep(20)
           # motor.backward()
            #print("backwards")
            #sleep(5)
    finally:
        motor.stop()
        motor.close()


def pulse_demo():
    motor = Motor(forward=FORWARD_PIN, backward=BACKWARD_PIN, enable=ENABLE_PIN)
    try:
        pulse(motor, 1, 5)      # full speed forward for 5 s
        pulse(motor, 0, 0)      # ramp down to stop
    finally:
        motor.stop()
        motor.close()


if __name__ == "__main__":
    pulse_demo()
