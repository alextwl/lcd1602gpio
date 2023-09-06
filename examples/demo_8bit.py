'''
demo_8bit.py -- LCD 8-bit demo
'''

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

    lcd.write_line("abcdefghijklmnop", 0)
    lcd.write_line("1234567890123456", 1)

    GPIO.cleanup()


if __name__ == '__main__':
    main()

