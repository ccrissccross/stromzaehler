import RPi.GPIO as gpio

from typing import Final


class S0interface:

    def __init__(self) -> None:
        # nutze Pin-Nummern-Bezeichnung des Broadcom-Chips (BCM-mode)
        gpio.setmode(gpio.BCM)
        # Pin konfigurieren:
        # BCM-Pin 2 (SDA -> I2C) hat einen Pull-Up-Widerstand eingebaut
        self.PIN_NUMBER: Final[int] = 2
        gpio.setup(self.PIN_NUMBER, gpio.IN)
    
    def wasteSignal(self) -> None:
        """
        'Waste' a Signal. Recommended before ever calling self.waitForSignal().
        This enables you to have 'clean' time-intervals between Signals.
        """
        self.waitForSignal()
    
    def waitForSignal(self) -> None:
        """
        Blocking method which waits until S0-interface receives an impulse/signal.
        """
        # I2C Pins schalten gegen Masse, also auf fallende Flanke warten
        gpio.wait_for_edge(self.PIN_NUMBER, gpio.FALLING)
