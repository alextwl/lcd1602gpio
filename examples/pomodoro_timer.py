'''
a simple LCD pomodoro timer
'''

import math
import time
import RPi.GPIO as GPIO

from lcd1602gpio import LCD1602GPIO

# a typical length of pomodoro timer (unit: minute)
WORK_LENGTH=25
# a short break (unit: minute)
BREAK_LENGTH=5


def display_time(elapsed, lcd):
    '''
    Display time elapsed on line 1 of LCD.

    :param elapsed: time elapsed in seconds
    :type elapsed: int
    :param lcd: an instance of LCD1602GPIO
    :type lcd: LCD1602GPIO
    '''
    m, s = divmod(elapsed, 60)
    # tick
    lcd.write_line("%02d:%02d" % (m, s), 1)
    time.sleep(0.5)
    # tock
    lcd.write_line("%02d %02d" % (m, s), 1)


def main():
    '''
    initialize the LCD.
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

    lcd.write_line("a Pomodoro timer", 0)
    lcd.write_line('=' * 16, 1)

    time.sleep(3)

    try:
        while(True):
            for title, timer_len in [
                    ("now working...", WORK_LENGTH),
                    ("==take a break==", BREAK_LENGTH)]:
                lcd.clear_lcd()
                lcd.write_line(title, 0)
                lcd.write_line("       (%d mins)" % timer_len, 1)
    
                timer_start = time.monotonic()
                timer_end = timer_start + (timer_len * 60.0)
                while((current_time := time.monotonic()) < timer_end):
                    display_time(math.floor(current_time - timer_start), lcd)
                    # sleep a sec minus LCD execution time
                    time.sleep(current_time + 1.0 - time.monotonic())

    except KeyboardInterrupt:
        lcd.clear_lcd()
        lcd.write_line("Byebye!", 0)

        GPIO.cleanup()


if __name__ == '__main__':
    main()

