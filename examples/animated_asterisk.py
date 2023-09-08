'''
animated_asterisk.py -- create custom animated circle in CGRAM
'''

import time
import RPi.GPIO as GPIO

from lcd1602gpio import LCD1602GPIO


def main():
    '''
    a demo function.
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # 8bit mode setup, write only.
    lcd = LCD1602GPIO(rs=7,
                      e=8,
                      db7=18,
                      db6=23,
                      db5=24,
                      db4=25,
                      db3=6,
                      db2=13,
                      db1=19,
                      db0=26)

    # create 8 custom characters for my own animated asterisk
    # '-' (half left)
    lcd.set_cgram_char(0, [0b00000,
                           0b00000,
                           0b00000,
                           0b11000,
                           0b01000,
                           0b10000,
                           0b00000,
                           0b00000])
    # '\' (top-left)
    lcd.set_cgram_char(1, [0b00000,
                           0b10000,
                           0b01000,
                           0b11000,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000])

    # '|' (half top)
    lcd.set_cgram_char(2, [0b00000,
                           0b10100,
                           0b01100,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000])

    # '/' (top-right)
    lcd.set_cgram_char(3, [0b00000,
                           0b00101,
                           0b00110,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000])

    # '-' (half right)
    lcd.set_cgram_char(4, [0b00000,
                           0b00001,
                           0b00010,
                           0b00011,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00000])

    # '\' (bottom-right)
    lcd.set_cgram_char(5, [0b00000,
                           0b00000,
                           0b00000,
                           0b00011,
                           0b00010,
                           0b00001,
                           0b00000,
                           0b00000])

    # '|' (half bottom)
    lcd.set_cgram_char(6, [0b00000,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b00110,
                           0b00101,
                           0b00000,
                           0b00000])

    # '/' (bottom-left)
    lcd.set_cgram_char(7, [0b00000,
                           0b00000,
                           0b00000,
                           0b00000,
                           0b01100,
                           0b10100,
                           0b00000,
                           0b00000])

    # time to play animated asterisk
    try:
        while(True):
            for i in range(8):
                lcd.goto_lcd_line(0)
                lcd.write_char(i)
                time.sleep(0.3)
    except KeyboardInterrupt:
        lcd.write_line("Byebye!", 0)
        GPIO.cleanup()

if __name__ == '__main__':
    main()

