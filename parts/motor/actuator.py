from gpiozero import Motor
from time import sleep, time

# DRI0041 motor driver pins (BCM numbering)
ENABLE_PIN = 17
FORWARD_PIN = 27
BACKWARD_PIN = 22
PWM_FREQUENCY = 70  # Hz, gpiozero default is 100 Hz


def make_motor() -> Motor:
    motor = Motor(forward=FORWARD_PIN, backward=BACKWARD_PIN, enable=ENABLE_PIN)
    motor.forward_device.frequency = PWM_FREQUENCY
    motor.backward_device.frequency = PWM_FREQUENCY
    return motor


def spin_motor_forward_and_backwards():
    # The Pi drives the DRI0041's inputs; the driver powers the motor.
    # enable is held high, speed is set with PWM on the forward/backward pins.
    motor: Motor = make_motor()
    end_time = time() + 4  # run for 4 seconds
    try:
        while time() < end_time:
            motor.forward()
            sleep(1)
            motor.backward()
            sleep(1)
    finally:
        motor.stop()
        motor.close()


def keyboard_control():
    """Hold w to drive forward, hold s to drive backward, release to stop.
    q quits. Based on the gpiozero curses Robot example."""
    import curses

    motor = make_motor()

    actions = {
        ord("w"): motor.forward, ord("W"): motor.forward,
        ord("s"): motor.backward, ord("S"): motor.backward,
    }

    def main(window):
        window.addstr("Hold w = forward, hold s = backward, q = quit\n")
        next_key = None
        while True:
            curses.halfdelay(1)
            if next_key is None:
                key = window.getch()
            else:
                key = next_key
                next_key = None
            if key in (ord("q"), ord("Q")):
                break
            if key != -1:
                # KEY PRESSED
                action = actions.get(key)
                if action is not None:
                    action()
                    window.addstr(1, 0, "forward " if action == motor.forward else "backward")
                    window.refresh()
                # The keyboard's auto-repeat keeps sending the key while it is
                # held. The first repeat comes only after the repeat delay
                # (up to ~0.6 s on the Pi desktop), later ones every ~30-50 ms.
                curses.halfdelay(7)  # wait for the first repeat
                next_key = window.getch()
                curses.halfdelay(2)  # then for the following repeats
                while next_key == key:  # still held
                    next_key = window.getch()
                # KEY RELEASED
                motor.stop()
                window.addstr(1, 0, "stopped ")
                window.refresh()

    try:
        curses.wrapper(main)
    finally:
        motor.stop()
        motor.close()


if __name__ == "__main__":
    keyboard_control()


# ---------------------------------------------------------------------------
# New DriverMotor version (PWM on ENA, like DFRobot DRI0042_Test.ino).
# Commented out; uncomment and remove the code above to use it.
# ---------------------------------------------------------------------------
# from gpiozero import DigitalOutputDevice, PWMOutputDevice
# from time import sleep
#
# # DFRobot DRI0042 motor driver pins (BCM numbering)
# ENA_PIN = 17  # speed (PWM)
# IN1_PIN = 27  # direction
# IN2_PIN = 22  # direction
#
#
# class DriverMotor:
#     """One motor channel of the DRI0042, driven like DFRobot's example:
#     IN1/IN2 set the direction, PWM on ENA sets the speed."""
#
#     def __init__(self, in1=IN1_PIN, in2=IN2_PIN, ena=ENA_PIN):
#         self.in1 = DigitalOutputDevice(in1)
#         self.in2 = DigitalOutputDevice(in2)
#         # ~1 kHz, close to Arduino's analogWrite on pin 6
#         self.ena = PWMOutputDevice(ena, frequency=1000)
#
#     def forward(self, speed: float = 1.0) -> None:
#         """speed 0.0-1.0 (Arduino's analogWrite 0-255 divided by 255)."""
#         self.in1.on()
#         self.in2.off()
#         self.ena.value = speed
#
#     def backward(self, speed: float = 1.0) -> None:
#         self.in1.off()
#         self.in2.on()
#         self.ena.value = speed
#
#     def brake(self) -> None:
#         """IN1 = IN2 = LOW, like Motor1_Brake()."""
#         self.in1.off()
#         self.in2.off()
#
#     @property
#     def value(self) -> float:
#         """-1.0 (full backward) .. 1.0 (full forward), 0 = stopped."""
#         if self.in1.value and not self.in2.value:
#             return self.ena.value
#         if self.in2.value and not self.in1.value:
#             return -self.ena.value
#         return 0.0
#
#     @value.setter
#     def value(self, speed: float) -> None:
#         if speed > 0:
#             self.forward(speed)
#         elif speed < 0:
#             self.backward(-speed)
#         else:
#             self.brake()
#
#     def close(self) -> None:
#         self.brake()
#         for dev in (self.in1, self.in2, self.ena):
#             dev.close()
#
#
# def pulse(motor: DriverMotor, speed: float, duration: float, ramp: float = 0.5, steps: int = 20) -> None:
#     """Run the motor at `speed` for `duration` seconds.
#
#     speed: -1.0 (full backward) .. 1.0 (full forward), 0 = stopped.
#     ramp:  seconds to ramp from the current speed to `speed`. A soft start
#            avoids the big inrush current that can trip the supply/driver.
#     """
#     if not -1 <= speed <= 1:
#         raise ValueError("speed must be between -1 and 1")
#     start = motor.value
#     for i in range(1, steps + 1):
#         motor.value = start + (speed - start) * i / steps
#         sleep(ramp / steps)
#     sleep(duration)
#
#
# def dfrobot_test():
#     """Python version of DFRobot's DRI0042_Test.ino loop (one motor)."""
#     motor = DriverMotor()
#     speed = 200 / 255  # analogWrite(ENA, 200)
#     try:
#         while True:
#             motor.brake()
#             sleep(0.1)
#             motor.forward(speed)
#             sleep(1)
#             motor.brake()
#             sleep(0.1)
#             motor.backward(speed)
#             sleep(1)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         motor.close()
#
#
# def forward_5s():
#     """Full speed forward for 5 seconds, then brake."""
#     motor = DriverMotor()
#     try:
#         motor.forward(1.0)
#         sleep(5)
#     finally:
#         motor.close()
#
#
# def soft_start_test():
#     """Compare a hard start with a soft start (ramped) start.
#
#     If the motor stops during the hard start but keeps running during the
#     soft start, the inrush current at start-up is tripping the supply/driver.
#     """
#     motor = DriverMotor()
#     try:
#         print("1) HARD start: full speed immediately, 5 s")
#         motor.forward(1.0)
#         sleep(5)
#         motor.brake()
#         print("   stopped, waiting 3 s")
#         sleep(3)
#
#         print("2) SOFT start: ramp to full speed over 2 s, then hold 5 s")
#         pulse(motor, 1.0, 5, ramp=2)
#         print("   done")
#     finally:
#         motor.close()
#
#
# if __name__ == "__main__":
#     soft_start_test()
