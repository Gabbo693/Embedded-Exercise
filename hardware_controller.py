"""
Hardware Abstraction Layer
Handles GPIO, buttons, and LEDs with graceful fallback for non-Pi systems
"""
print("Importing: threading")
import threading
print("Importing: time")
import time
print("Importing: Callable, Optional, Dict, List")
from typing import Callable, Optional, Dict, List
print("Importing: dataclass, field")
from dataclasses import dataclass, field
print("Importing: Enum")
from enum import Enum


class LEDColor(Enum):
    """LED color states"""
    GREEN = "green"
    RED = "red"
    OFF = "off"


@dataclass
class ButtonEvent:
    """Event emitted when a button is pressed"""
    button_name: str
    pressed_at: float = field(default_factory=time.time)


class HardwareController:
    """
    Abstract hardware controller with Raspberry Pi GPIO support.
    Falls back to simulation when GPIO is unavailable.
    """
    
    def __init__(self, use_real_gpio: bool = True):
        self.use_real_gpio = use_real_gpio
        self.gpio = None
        self._led_state: Dict[LEDColor, bool] = {
            LEDColor.GREEN: False,
            LEDColor.RED: False,
        }
        self._button_callbacks: Dict[str, Callable[[ButtonEvent], None]] = {}
        self._button_threads: Dict[str, threading.Thread] = {}
        self._running = True
        
        # GPIO Pin configuration (Raspberry Pi BCM numbering)
        self.PIN_CONFIG = {
            "button_start": 17,
            "button_left": 27,
            "button_right": 22,
            "button_pause": 23,
            "led_green": 24,
            "led_red": 25,
        }
        
        # Initialize GPIO if available and requested
        if use_real_gpio:
            self._init_gpio()
    
    def _init_gpio(self) -> None:
        """Initialize GPIO for Raspberry Pi"""
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
            self.gpio.setmode(GPIO.BCM)
            self.gpio.setwarnings(False)
            
            # Setup output pins (LEDs)
            for pin_name in ["led_green", "led_red"]:
                pin = self.PIN_CONFIG[pin_name]
                self.gpio.setup(pin, GPIO.OUT)
                self.gpio.output(pin, GPIO.LOW)
            
            # Setup input pins (buttons) with pull-up
            for pin_name in ["button_start", "button_left", "button_right", "button_pause"]:
                pin = self.PIN_CONFIG[pin_name]
                self.gpio.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            print("✓ GPIO initialized successfully (Raspberry Pi)")
            self.use_real_gpio = True
        except (ImportError, RuntimeError) as e:
            print(f"⚠ GPIO not available: {e}")
            print("  Using simulated GPIO (keyboard fallback available)")
            self.gpio = None
            self.use_real_gpio = False
    
    def set_led(self, color: LEDColor, on: bool) -> None:
        """Control an LED
        
        Args:
            color: LED color (GREEN or RED)
            on: True to turn on, False to turn off
        """
        self._led_state[color] = on
        
        if not self.use_real_gpio or self.gpio is None:
            state_char = "🟢" if color == LEDColor.GREEN and on else "🔴" if color == LEDColor.RED and on else "⚫"
            print(f"  LED {color.value}: {state_char} {'ON' if on else 'OFF'}")
            return
        
        pin_map = {
            LEDColor.GREEN: self.PIN_CONFIG["led_green"],
            LEDColor.RED: self.PIN_CONFIG["led_red"],
        }
        
        if color in pin_map:
            pin = pin_map[color]
            self.gpio.output(pin, self.gpio.HIGH if on else self.gpio.LOW)
    
    def flash_led(self, color: LEDColor, duration: float = 0.5, count: int = 1) -> None:
        """Flash an LED
        
        Args:
            color: LED color
            duration: On-time duration in seconds
            count: Number of flashes
        """
        def _flash():
            for _ in range(count):
                self.set_led(color, True)
                time.sleep(duration / 2)
                self.set_led(color, False)
                if count > 1:
                    time.sleep(duration / 2)
        
        thread = threading.Thread(target=_flash, daemon=True)
        thread.start()
    
    def register_button_callback(self, button_name: str, 
                                callback: Callable[[ButtonEvent], None]) -> None:
        """Register a callback for button press events
        
        Args:
            button_name: Button name (start, left, right, pause)
            callback: Function to call on button press
        """
        self._button_callbacks[button_name] = callback
        
        if not self.use_real_gpio:
            print(f"  Button registered: {button_name} (simulated mode)")
            return
        
        # Start monitoring thread for this button
        if button_name not in self._button_threads:
            thread = threading.Thread(
                target=self._button_monitor_thread,
                args=(button_name,),
                daemon=True
            )
            self._button_threads[button_name] = thread
            thread.start()
    
    def _button_monitor_thread(self, button_name: str) -> None:
        """Monitor a button in a separate thread
        
        Args:
            button_name: Button name to monitor
        """
        if not self.gpio or button_name not in self.PIN_CONFIG:
            return
        
        pin = self.PIN_CONFIG[button_name]
        last_press_time = 0.0
        debounce_ms = 50  # Debounce threshold
        
        while self._running:
            try:
                if self.gpio.input(pin) == self.gpio.LOW:  # Button pressed (active low)
                    current_time = time.time() * 1000
                    if current_time - last_press_time > debounce_ms:
                        event = ButtonEvent(button_name=button_name)
                        if button_name in self._button_callbacks:
                            self._button_callbacks[button_name](event)
                        last_press_time = current_time
                    time.sleep(0.01)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Error monitoring button {button_name}: {e}")
                time.sleep(0.1)
    
    def simulate_button_press(self, button_name: str) -> None:
        """Simulate a button press (for testing without hardware)
        
        Args:
            button_name: Button to simulate
        """
        event = ButtonEvent(button_name=button_name)
        if button_name in self._button_callbacks:
            self._button_callbacks[button_name](event)
    
    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        self._running = False
        
        if self.use_real_gpio and self.gpio:
            try:
                self.gpio.cleanup()
                print("✓ GPIO cleaned up")
            except Exception as e:
                print(f"Error during GPIO cleanup: {e}")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass
