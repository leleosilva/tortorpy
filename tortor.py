import pathlib
import sys
import threading
import time

from datetime import datetime
from mss import mss
from pynput import keyboard

PATHFILE = "./screenshots/" # Path where the screenshots will be saved. It can be changed

# Hotkeys to start, pause or quit the program. They can be changed
START_HOTKEY = '<alt>+s'
PAUSE_HOTKEY = '<alt>+p'
QUIT_HOTKEY = '<alt>+q'

TIME_BETWEEN_SCREENSHOTS = 3.5 # Time between each take_screenshot() call. It can be changed

# Class ScreenshotThread extends threading.Thread
class ScreenshotThread(threading.Thread):
    
    """ Constructor of ScreenshotThread """
    def __init__(self):
        threading.Thread.__init__(self)
        self.paused = threading.Event()
        self.stopped = threading.Event()
        self.screenshots_saved = 0
        self.sct = mss()

    """ Initializes the execution of ScreenshotThread, doing necessary verifications """
    def initialize(self):
        if not self.is_alive():
            print("Starting program...")
            check_if_directory_exists()
            self.start()
      
    """
    Method overridden from threading.Thread, and called after starting the ScreenshotThread thread.
    It calls take_screenshot() as long as the instance is not paused nor stopped.
    """
    def run(self):
        while not self.stopped.is_set():
            if not self.paused.wait(TIME_BETWEEN_SCREENSHOTS):
                self.take_screenshot()

    """ Takes screenshots and save them on PATHFILE """
    def take_screenshot(self):
        screenshot_name = self.generate_screenshot_name()
        pathfile = PATHFILE + screenshot_name

        self.sct.shot(output=pathfile)
        self.screenshots_saved += 1

        print(f"\nSaving screenshot {screenshot_name}")
        print(f"Screenshot saved on path {pathfile}")

    """ Generates a name for the screenshot based on the current date and time """
    def generate_screenshot_name(self):
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"{now_str}.png"
        return screenshot_name 
    
    """
    Sets the 'stopped' internal flag event object to true and makes the main process wait until the
    thread terminates, exiting the program accordingly.
    """
    def exit(self):
        if self.is_alive():
            self.stop()
            self.join()
        print(self.number_of_screenshots())
        exit_program()

    """ Sets the internal flag of the 'paused' event object to true """
    def pause(self):
        self.paused.set()
    
    """ Sets the internal flag of the 'paused' event object to false """
    def resume(self):
        self.paused.clear()

    """ Checks if the instance should pause or resume based on its internal 'paused' flag """
    def pause_or_resume(self):
        if self.is_alive():
            if self.paused.is_set():
                print("\nProgram resumed.")
                self.resume()
            else:
                self.pause()
                
                print(f"\nProgram paused. {self.number_of_screenshots_until_now()}")
                print("Press 'p' to resume it or 'q' to quit the program.")

    """ Sets the internal flag of the 'stopped' event object to true """
    def stop(self):
        self.stopped.set()
    
    """" Returns the number of screenshots saved on PATHFILE up to the moment when the program is paused """
    def number_of_screenshots_until_now(self):
        till_now_str = ""
        if self.screenshots_saved == 0:
            till_now_str = "No screenshots were saved yet."
        elif self.screenshots_saved == 1:
            till_now_str = f"{self.screenshots_saved} screenshot was saved so far."
        elif self.screenshots_saved > 1:
            till_now_str = f"{self.screenshots_saved} screenshots were saved so far."
        return till_now_str
    
    """ Returns the number of screenshots saved on PATHFILE while the program was running """
    def number_of_screenshots(self):
        saved_str = ""
        if self.screenshots_saved == 1:
            saved_str = f"\nWhile the program was running, {self.screenshots_saved} screenshot was saved on path '{PATHFILE}'."
        elif self.screenshots_saved > 1:
            saved_str = f"\nWhile the program was running, {self.screenshots_saved} screenshots were saved on path '{PATHFILE}'."
        return saved_str

"""
Checks if the directory where the screenshots will be saved do exist.
If it does not, it will be created.
"""
def check_if_directory_exists():
    pathlib.Path(PATHFILE).mkdir(parents=True, exist_ok=True)

""" Method that exits the program accordingly by messaging the user and flushing the I/O buffer """
def exit_program():
    print("Exiting the program...")
    time.sleep(0.01)
    flush_input()
    sys.exit(0)

"""
Flushes input and output buffered data.
Useful for cleaning the terminal from keystrokes pressed while the program was running.
"""
def flush_input():
    try: # For Linux/Unix
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError: # For Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def main():
    screenshot_manager = ScreenshotThread()

    initial_hotkeys = keyboard.GlobalHotKeys(
        {
            START_HOTKEY: screenshot_manager.initialize,
            QUIT_HOTKEY: screenshot_manager.exit,
            PAUSE_HOTKEY: screenshot_manager.pause_or_resume
        })

    initial_hotkeys.start()
    try:
        initial_hotkeys.join()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()