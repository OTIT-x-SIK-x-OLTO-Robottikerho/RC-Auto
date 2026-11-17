from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep

# DFRobot DRI0042 motor driver pins (BCM numbering)
ENA_PIN = 17  # speed (PWM)
IN1_PIN = 27  # direction
IN2_PIN = 22  # direction


class DriverMotor:
    """One motor channel of the DRI0042, driven like DFRobot's example:
    IN1/IN2 set the direction, PWM on ENA sets the speed."""

    def __init__(self, in1=IN1_PIN, in2=IN2_PIN, ena=ENA_PIN):
        self.in1 = DigitalOutputDevice(in1)
        self.in2 = DigitalOutputDevice(in2)
        # ~1 kHz, close to Arduino's analogWrite on pin 6
        self.ena = PWMOutputDevice(ena, frequency=1000)

    def forward(self, speed: float = 1.0) -> None:
        """speed 0.0-1.0 (Arduino's analogWrite 0-255 divided by 255)."""
        self.in1.on()
        self.in2.off()
        self.ena.value = speed

    def backward(self, speed: float = 1.0) -> None:
        self.in1.off()
        self.in2.on()
        self.ena.value = speed

    def brake(self) -> None:
        """IN1 = IN2 = LOW, like Motor1_Brake()."""
        self.in1.off()
        self.in2.off()

    @property
    def value(self) -> float:
        """-1.0 (full backward) .. 1.0 (full forward), 0 = stopped."""
        if self.in1.value and not self.in2.value:
            return self.ena.value
        if self.in2.value and not self.in1.value:
            return -self.ena.value
        return 0.0

    @value.setter
    def value(self, speed: float) -> None:
        if speed > 0:
            self.forward(speed)
        elif speed < 0:
            self.backward(-speed)
        else:
            self.brake()

    def close(self) -> None:
        self.brake()
        for dev in (self.in1, self.in2, self.ena):
            dev.close()


def pulse(motor: DriverMotor, speed: float, duration: float, ramp: float = 0.5, steps: int = 20) -> None:
    """Run the motor at `speed` for `duration` seconds.

    speed: -1.0 (full backward) .. 1.0 (full forward), 0 = stopped.
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


def dfrobot_test():
    """Python version of DFRobot's DRI0042_Test.ino loop (one motor)."""
    motor = DriverMotor()
    speed = 200 / 255  # analogWrite(ENA, 200)
    try:
        while True:
            motor.brake()
            sleep(0.1)
            motor.forward(speed)
            sleep(1)
            motor.brake()
            sleep(0.1)
            motor.backward(speed)
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        motor.close()


def forward_5s():
    """Full speed forward for 5 seconds, then brake."""
    motor = DriverMotor()
    try:
        motor.forward(1.0)
        sleep(5)
    finally:
        motor.close()


if __name__ == "__main__":
    forward_5s()
