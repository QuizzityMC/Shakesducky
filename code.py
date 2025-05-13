import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

INITIAL_WAIT = 2.0
DINO_PAGE_LOAD_WAIT = 2.0
START_DELAY = 0.5
JUMP_INTERVAL = 0.7
DEATH_RESTART_DELAY = 2.0
TRIGGER_NEW_TAB_WAIT = 1.5
TRIGGER_URL_LOAD_AND_DISPLAY_WAIT = 15.0
CLOSE_TAB_DELAY = 0.5
PLAY_TIME = 10.0
LED_BLINK_COUNT = 3
LED_BLINK_DELAY = 0.2

TRIGGER_BUTTON_PIN = board.GP25
LED_PIN = board.GP23

DINO_URL = "https://chrome-dino-game.github.io/"
INVASION_URL = "https://quizzitymc.github.io/picohacker/dinosaurinvasion.html"

def setup_digital_input(pin):
    try:
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        print(f"Successfully set up input on pin: {pin}")
        return button
    except Exception as e:
        print(f"!!! ERROR SETTING UP INPUT on pin {pin}: {e}")
        return None

def setup_digital_output(pin):
    try:
        led = digitalio.DigitalInOut(pin)
        led.direction = digitalio.Direction.OUTPUT
        led.value = False
        print(f"Successfully set up output on pin: {pin}")
        return led
    except Exception as e:
        print(f"!!! ERROR SETTING UP OUTPUT on pin {pin}: {e}")
        return None

def blink_led(led, count, delay):
    if led:
        for _ in range(count):
            led.value = True
            time.sleep(delay)
            led.value = False
            time.sleep(delay)

def open_url_in_new_tab(kbd, layout, url, wait_time):
    print("Opening new tab (Ctrl+T)...")
    kbd.press(Keycode.CONTROL, Keycode.T)
    kbd.release_all()
    time.sleep(1.0)
    print(f"Typing URL: {url}")
    layout.write(url)
    time.sleep(0.5)
    print("Pressing Enter to load URL...")
    kbd.press(Keycode.ENTER)
    kbd.release_all()
    print(f"Waiting {wait_time}s for page to load...")
    time.sleep(wait_time)

def game_loop(kbd, layout, trigger_button, led):
    keep_running = True
    trigger_activated = False

    while keep_running:
        if led:
            led.value = True

        print("Pressing SPACE to start/restart Dino...")
        kbd.press(Keycode.SPACE)
        kbd.release_all()
        time.sleep(START_DELAY)

        start_play_time = time.monotonic()
        while time.monotonic() - start_play_time < PLAY_TIME:
            if trigger_button and not trigger_button.value:
                print(f"Trigger button on Pico (Pin {TRIGGER_BUTTON_PIN}) PRESSED!")
                trigger_activated = True
                keep_running = False
                break

            print("Dino Jump! (Space)")
            kbd.press(Keycode.SPACE)
            kbd.release_all()
            time.sleep(JUMP_INTERVAL)

        if not keep_running:
            break

        print(f"Assuming Dino death, waiting {DEATH_RESTART_DELAY}s to restart...")
        if led:
            led.value = False
        time.sleep(DEATH_RESTART_DELAY)

    return trigger_activated

def main():
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)

    trigger_button = setup_digital_input(TRIGGER_BUTTON_PIN)
    led = setup_digital_output(LED_PIN)

    print(f"Waiting {INITIAL_WAIT}s for device recognition...")
    time.sleep(INITIAL_WAIT)

    try:
        open_url_in_new_tab(kbd, layout, DINO_URL, DINO_PAGE_LOAD_WAIT)

        if trigger_button:
            print(f"Starting game loop. Press the button connected to {TRIGGER_BUTTON_PIN} on the Pico to trigger sequence.")
        else:
            print("Starting game loop. (Trigger button setup failed, sequence cannot be triggered).")

        trigger_activated = game_loop(kbd, layout, trigger_button, led)

        if trigger_activated:
            print("Trigger sequence initiated: Opening Invasion HTML page...")
            blink_led(led, LED_BLINK_COUNT, LED_BLINK_DELAY)
            open_url_in_new_tab(kbd, layout, INVASION_URL, TRIGGER_URL_LOAD_AND_DISPLAY_WAIT)

            print("Sending Ctrl+W to close the current tab...")
            kbd.press(Keycode.CONTROL, Keycode.W)
            kbd.release_all()
            time.sleep(CLOSE_TAB_DELAY)

            print("Tab close command sent. Script task complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        blink_led(led, 15, 0.08)
    finally:
        kbd.release_all()
        if led:
            led.value = False
        print("Script end. All keys released.")

if __name__ == "__main__":
    main()