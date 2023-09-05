'''
lcd1602gpio -- Use HD44780-compatible 16x2 LCD module via RPi.GPIO

Copyright (c) 2023 Wei-Li Tang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
import RPi.GPIO as GPIO


class LCD1602GPIO:
    def __init__(self,
                 rs, e,
                 db7, db6, db5, db4,
                 db3, db2, db1, db0,
                 e_pulse=0.0005,
                 e_delay=0.0005,
                 delayfunc=time.sleep):
        self.rs = rs    # RS pin number
        self.e = e      # E (Enable) pin number
        # Data bus pins
        self.db7 = db7
        self.db6 = db6
        self.db5 = db5
        self.db4 = db4
        self.db3 = db3
        self.db2 = db2
        self.db1 = db1
        self.db0 = db0

        '''
        Define clock pulse & delays between instructions.

        Also see HD44780U manual page 24 Table 6
        for instructions' max execution time.

        Since the read function is not implemented here
        and we cannot read Busy Flag (BF),
        so the defaults are longer than standard execution times.
        '''
        # a clock pulse length for Enable pin's voltage high status
        self.e_pulse = e_pulse
        # head & tail delays for a toggle of Enable pin
        self.e_delay = e_delay
        # Preferred delay function
        self._sleep = delayfunc

        # set gpio pin layout
        self.gpio_setup()
        self.initialize_lcd()

    def gpio_setup(self):
        GPIO.setup(self.rs, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)
        GPIO.setup(self.db7, GPIO.OUT)
        GPIO.setup(self.db6, GPIO.OUT)
        GPIO.setup(self.db5, GPIO.OUT)
        GPIO.setup(self.db4, GPIO.OUT)
        GPIO.setup(self.db3, GPIO.OUT)
        GPIO.setup(self.db2, GPIO.OUT)
        GPIO.setup(self.db1, GPIO.OUT)
        GPIO.setup(self.db0, GPIO.OUT)

        self.data_channel = (self.db7, self.db6, self.db5, self.db4,
                             self.db3, self.db2, self.db1, self.db0)

    def toggle_enable(self):
        '''
        Toggle E (Enable) pin from HIGH to LOW in a cycle.

        run it when submitting an instruction or a data set.
        '''
        self._sleep(self.e_delay)
        GPIO.output(self.e, GPIO.HIGH)
        self._sleep(self.e_pulse)
        GPIO.output(self.e, GPIO.LOW)
        self._sleep(self.e_delay)

    def command(self, cmd_byte):
        '''
        Send an instruction.

        :param cmd_byte: a byte of instruction
        :type cmd_byte: int
        '''
        # DB7 to DB0 (High bit to low bit)
        data_set = ((cmd_byte >> 7) & 1,
                    (cmd_byte >> 6) & 1,
                    (cmd_byte >> 5) & 1,
                    (cmd_byte >> 4) & 1,
                    (cmd_byte >> 3) & 1,
                    (cmd_byte >> 2) & 1,
                    (cmd_byte >> 1) & 1,
                    cmd_byte & 1)

        GPIO.output(self.rs, GPIO.LOW)  # RS=0 (Select instruction register)
        GPIO.output(self.data_channel, data_set)
        self.toggle_enable()

    def write_char(self, c):
        '''
        Write a character to data register.

        :param c: a byte of character
        :type c: int
        '''
        # DB7 to DB0 (High bit to low bit)
        data_set = ((c >> 7) & 1,
                    (c >> 6) & 1,
                    (c >> 5) & 1,
                    (c >> 4) & 1,
                    (c >> 3) & 1,
                    (c >> 2) & 1,
                    (c >> 1) & 1,
                    c & 1)

        GPIO.output(self.rs, GPIO.HIGH)  # RS=1 (Select data register)
        GPIO.output(self.data_channel, data_set)
        self.toggle_enable()

    def clear_lcd(self):
        '''
        Display clear: 00000001
        '''
        self.command(0b00000001)

    def initialize_lcd(self, reset_delay=0.001):
        '''
        Initialize the LCD module.

        We assume the internal reset circuit didn't work,
        so we always initialize the LCD by instructions manually.

        Ref.: HD44780U manual page 45-46 Figure 23-24
        '''
        # Function Set in the beginning: 0011**** DL=1 (8-bit) N=* F=*
        self.command(0b00110000)

        '''
        assume Vcc raised to rated voltage after power on,
        we need to wait for the first function set to be completed.
        (at least 4.1ms + 100 microseconds)
        '''
        self._sleep(reset_delay)

        '''
        Function Set: 001110**
        DL=1 (8-bit)
        N=1 (2-line display)
        F=0 (character font 5*8, but don't care when N=1,
             see HD44780U manual page 29 Table 8's footer)
        '''
        self.command(0b00111000)

        '''
        Display off: 00001000
        D=0 (Display off)
        C=0 (Cursor off)
        B=0 (Blinking off)
        '''
        self.command(0b00001000)

        # Display clear
        self.clear_lcd()

        '''
        Entry Mode Set: 00000110
        I/D=1 (Increment)
        S=0 (display does not shift)
        '''
        self.command(0b00000110)

        # the standard initialization ends here.
        # continue setting custom configs.
        
        '''
        Display on: 00001100
        D=1 (Display on)
        C=0 (Cursor off)
        B=0 (Blinking off)
        '''
        self.command(0b00001100)

    def goto_lcd_line(self, line):
        '''
        Go to the beginning of line 0 or line 1.

        For the address range of Display Data RAM (DDRAM)
        see HD44780U manual page 11 Figure 4

        :param line: the index of line (0 or 1).
        :type line: int
        '''
        if line == 1:
            self.command(0b10000000 | 0x40)
        else:
            # for line 0 and other invalid input line numbers
            # default to the beginning of line 0.
            self.command(0b10000000 | 0x00)

    def write_line(self, s, line):
        '''
        Write a line of string to LCD.

        :param s: the input string to be written to LCD.
        :param line: the index of line (0 or 1).
        :type line: int
        '''
        self.goto_lcd_line(line)

        for c in s:
            self.write_char(ord(c))


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

