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


DL_8BIT = 1
DL_4BIT = 0


class LCD1602GPIO:
    def __init__(self,
                 rs, e,
                 db7, db6, db5, db4,
                 db3, db2, db1, db0,
                 e_pulse=0.0005,
                 e_delay=0.0005,
                 delayfunc=time.sleep,
                 dl_mode=DL_8BIT):
        self.dl_mode = dl_mode

        self.rs = rs    # RS pin number
        self.e = e      # E (Enable) pin number
        # Data bus pins
        self.db7 = db7
        self.db6 = db6
        self.db5 = db5
        self.db4 = db4
        if dl_mode == DL_8BIT:
            self.db3 = db3
            self.db2 = db2
            self.db1 = db1
            self.db0 = db0
            self._write = self._write_8bit
        else:
            # 4bit mode
            self._write = self._write_4bit

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
        if self.dl_mode == DL_8BIT:
            GPIO.setup(self.db3, GPIO.OUT)
            GPIO.setup(self.db2, GPIO.OUT)
            GPIO.setup(self.db1, GPIO.OUT)
            GPIO.setup(self.db0, GPIO.OUT)

            self.data_channel = (self.db7, self.db6, self.db5, self.db4,
                                 self.db3, self.db2, self.db1, self.db0)
        else:
            # 4bit mode
            self.data_channel = (self.db7, self.db6, self.db5, self.db4)

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

    def _write_8bit(self, c):
        '''
        Write a byte to register in 8bit mode.

        :param c: a byte of data
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

        GPIO.output(self.data_channel, data_set)
        self.toggle_enable()

    def _write_4bit(self, c):
        '''
        Write a byte to register in 4bit mode.

        :param c: a byte of data
        :type c: int
        '''
        # DB7 to DB4 (the high bit part)
        data_set = ((c >> 7) & 1,
                    (c >> 6) & 1,
                    (c >> 5) & 1,
                    (c >> 4) & 1)

        GPIO.output(self.data_channel, data_set)
        self.toggle_enable()

        # DB7 to DB4 (the low bit part)
        data_set = ((c >> 3) & 1,
                    (c >> 2) & 1,
                    (c >> 1) & 1,
                    c & 1)

        GPIO.output(self.data_channel, data_set)
        self.toggle_enable()

    def command(self, c):
        '''
        Send an instruction.

        :param c: a byte of instruction
        :type c: int
        '''
        GPIO.output(self.rs, GPIO.LOW)  # RS=0 (Select instruction register)
        self._write(c)

    def write_char(self, c):
        '''
        Write a character to data register.

        :param c: a byte of character
        :type c: int
        '''
        GPIO.output(self.rs, GPIO.HIGH)  # RS=1 (Select data register)
        self._write(c)

    def clear_lcd(self):
        '''
        Display clear: 00000001
        '''
        self.command(0b00000001)

    def initialize_lcd(self):
        '''
        Initialize the LCD module.

        We assume the internal reset circuit didn't work,
        so we always initialize the LCD by instructions manually.

        Ref.: HD44780U manual page 45-46 Figure 23-24
        '''
        if self.dl_mode == DL_8BIT:
            self._write = self._write_8bit
        else:
            self._write = self._write_4bit

        '''
        We don't know what data length mode the LCD is on now,
        so we do the procedure of resetting the LCD by two universal commands
        in order to enter the target mode.

        4 cases:

        (1) 8-bit circuit + 8-bit mode LCD

        RS  RW  DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0
        ---------------------------------------
        (the 1st call: self.command(0b00110011) + self._write_8bit, 1 cycle)
        0   0   0   0   1   1   0   0   1   1   Function Set DL=1
        (the LCD entered 8-bit mode)

        (the 2nd call: self.command(0b00110010) + self._write_8bit, 1 cycle)
        0   0   0   0   1   1   0   0   1   1   Function Set DL=1
        (the LCD entered 8-bit mode)

        (2) 8-bit circuit + 4-bit mode LCD

        RS  RW  DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0
        ---------------------------------------
        (the 1st call: self.command(0b00110011) + self._write_8bit, 1 cycle)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD received high order bits 0b0011???? and waiting for low order bits)

        (the 2nd call: self.command(0b00110010) + self._write_8bit, 1 cycle)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD received low order bits 0b0011)
        (the LCD accepted one instruction 0b00110011 and entered 8-bit mode)

        (3) 4-bit circuit + 8-bit mode LCD

        RS  RW  DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0
        ---------------------------------------
        (the 1st call: self.command(0b00110011) + self._write_4bit, 2 cycles)
        (splitted into 2 parts by nibble sending logic)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD accepted one instruction 0b0011**** in a cycle and entered 8-bit mode)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD accepted one instruction 0b0011**** in a cycle and entered 8-bit mode)

        (the 2nd call: self.command(0b00110010) + self._write_4bit, 2 cycle)
        (splitted into 2 parts by nibble sending logic)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD accepted one instruction 0b0011**** in a cycle and entered 8-bit mode)
        0   0   0   0   1   0   *   *   *   *   Function Set DL=0
        (the LCD accepted one instruction 0b0010**** in a cycle and entered 4-bit mode)

        (4) 4-bit circuit + 4-bit mode LCD

        RS  RW  DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0
        ---------------------------------------
        (the 1st call: self.command(0b00110011) + self._write_4bit, 2 cycles)
        (splitted into 2 parts by nibble sending logic)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD accepted one instruction 0b00110011 in 2 cycles and entered 8-bit mode)

        (the 2nd call: self.command(0b00110010) + self._write_4bit, 2 cycle)
        (splitted into 2 parts by nibble sending logic)
        0   0   0   0   1   1   *   *   *   *   Function Set DL=1
        (the LCD accepted one instruction 0b0011**** and entered 8-bit mode)
        0   0   0   0   1   0   *   *   *   *   Function Set DL=0
        (the LCD accepted one instruction 0b0010**** and entered 4-bit mode)
        '''
        self.command(0b00110011)  # 0x33, the 1st call
        self.command(0b00110010)  # 0x32, the 2nd call

        '''
        Function Set: 001110**
        DL=0 (4-bit) or 1 (8-bit)
        N=1 (2-line display)
        F=0 (character font 5*8, but don't care when N=1,
             see HD44780U manual page 29 Table 8's footer)
        '''
        self.command(0b00101000 | (self.dl_mode << 4))

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

    def goto_lcd_line(self, line, pos=0):
        '''
        Go to the beginning or the specified position of line 0 or line 1.

        For the address range of Display Data RAM (DDRAM)
        see HD44780U manual page 11 Figure 4

        :param line: the index of line (0 or 1).
        :type line: int
        :param pos: the display position of a line (0 ~ 15).
        :type pos: int
        '''
        if line == 1:
            self.command(0b10000000 | 0x40 | (pos & 0b1111))
        else:
            # for line 0 and other invalid input line numbers
            # default to line 0.
            self.command(0b10000000 | (pos & 0b1111))

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

    def set_cgram_char(self, cgram_no, bitmap):
        '''
        Set CGRAM address and write 5x8 bitmap pixels.

        After setting the custom character to CGRAM,
        you can call self.write_char(cgram_no) to display it on LCD.

        Also see HD44780U manual page 20 for drawing custom char HOWTO.

        :param cgram_no: The number of CGRAM address (0 ~ 7)
        :type cgram_no: int
        :param bitmap: The list of 8 single-byte integers
        :type bitmap: List[int]
        '''
        if not (0 <= cgram_no <= 7):
            raise ValueError("Invalid CGRAM number: %s" % str(cgram_no))
        if not isinstance(bitmap, list) or len(bitmap) != 8:
            raise ValueError("Invalid bitmap: should be a list of 8 integers")

        # Set CGRAM address (0b01AAAAAA)
        self.command(0b01000000 | (cgram_no * 8))

        # Write CGRAM data
        for row_byte in bitmap:
            self.write_char(row_byte & 0b11111)  # filter only 5 column bits

