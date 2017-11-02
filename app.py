#!/usr/bin/env python

import os
import time
import glob
import pygame
import random
import logging
import itertools
import RPi.GPIO as GPIO

log = logging.getLogger(__name__)


class MainApp:
    def __init__(self):
        # Use BCM GPIO references instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Define GPIO to use on Pi
        self.GPIO_PIR = 14
        self.GPIO_LED = 25
        # Set pin as input
        GPIO.setup(self.GPIO_PIR, GPIO.IN)
        GPIO.setup(self.GPIO_LED, GPIO.OUT)
        GPIO.output(self.GPIO_LED, GPIO.LOW)
        # Music files
        resource_dir_glob = os.path.join(
            os.path.abspath(
                os.path.join(__file__, os.pardir, 'resources', '*.mp3')))
        files = glob.glob(resource_dir_glob)
        assert len(files) > 0, "Can't find music files"
        random.shuffle(files)
        self.music_files = itertools.cycle(files)
        pygame.mixer.init()

    def __del__(self):
        # Reset GPIO settings
        GPIO.cleanup()

    def run(self):
        Current_State = 0
        Previous_State = 0

        # Loop until PIR output is 0
        while GPIO.input(self.GPIO_PIR) == 1:
            Current_State = 0
        # Loop until users quits with CTRL-C
        while True:
            # Read PIR state
            Current_State = GPIO.input(self.GPIO_PIR)
            if Current_State == 1 and Previous_State == 0:
                # PIR is triggered
                log.info("Motion detected!")
                track = self.music_files.next()
                pygame.mixer.music.load(track)
                pygame.mixer.music.play()
                # Blink an LED while the sound playing
                while pygame.mixer.music.get_busy() == True:
                    GPIO.output(self.GPIO_LED, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(self.GPIO_LED, GPIO.LOW)
                    time.sleep(0.5)
                    continue
                # Record previous state
                Previous_State = 1
            elif Current_State == 0 and Previous_State == 1:
                # REED has returned to ready state
                log.info("Ready")
                Previous_State = 0
            # Wait for 10 milliseconds
            time.sleep(0.01)


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        level=logging.ERROR
    )
    log.setLevel(logging.INFO)

    try:
        MainApp().run()
    except KeyboardInterrupt:
        pass
