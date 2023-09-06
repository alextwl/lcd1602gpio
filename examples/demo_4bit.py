'''
demo_4bit.py -- LCD 4-bit demo
'''

import RPi.GPIO as GPIO

from lcd1602gpio import LCD1602GPIO, DL_4BIT


def main():
    '''
    a demo function.
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # 4bit mode setup, write only.
    lcd = LCD1602GPIO(rs=7,
                      e=8,
                      db7=18,
                      db6=23,
                      db5=24,
                      db4=25,
                      db3=None,
                      db2=None,
                      db1=None,
                      db0=None,
                      dl_mode=DL_4BIT)

    lcd.write_line("abcdefghijklmnop", 0)
    lcd.write_line("1234567890123456", 1)

    GPIO.cleanup()


if __name__ == '__main__':
    main()

