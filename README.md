# lcd1602gpio
Use HD44780-compatible 16x2 LCD module by Python via Raspberry Pi GPIO

## Introduction

Based on [RPi.GPIO](https://pypi.org/project/RPi.GPIO/),
it writes instructions to a 16x2 LCD module through Raspberry Pi's GPIO pins directly.

This is not for interfacing an I2C LCD.

This module provides the following functions:

* Initialize LCD in 8-bit and 4-bit data bus modes.
* Write instructions to LCD.
* Write data to LCD's DDRAM. (Data Display RAM)
* Write custom character to LCD's CGRAM. (Character Generator RAM)
* Write a line of string and display it on LCD.
* Clear LCD display.

This module cannot:

* Read any data or address from LCD.

## Synopsis

```
class LCD1602GPIO
|   LCD1602GPIO(rs, e,
|               db7, db6, db5, db4,
|               db3, db2, db1, db0,
|               e_pulse=0.0005,
|               e_delay=0.0005,
|               delayfunc=time.sleep,
|               dl_mode=DL_8BIT) --> an LCD controller instance
```

Arguments:

* `rs`: GPIO pin number to RS.
* `e`: GPIO pin number to E (Enable).
* `db7` ~ `db0`: GPIO pin numbers of data bus. (set `db3` ~ `db0` to None if you're going to use 4-bit mode.)
* `e_pulse`: the pulse length of E in high voltage, in seconds.
* `e_delay`: the delays before & after E in high voltage, in seconds.
* `delayfunc`: the delay function. Default to `time.sleep`.
* `dl_mode`: the data bus mode of LCD. Set to `DL_8BIT` for 8-bit or `DL_4BIT` for 4-bit.

### Class members

* `gpio_setup()`: configure GPIO pins. (invoked during class initialization.)
* `toggle_enable()`: Toggle E (Enable) pin from HIGH to LOW in a cycle.
* `_write(c)`: write a byte `c` (int) to data bus. an alias of `_write_8bit(c)` or `_write_4bit(c)` depending on data bus mode.
* `command(c)`: send an instruction byte `c` (int) to LCD's instruction register (IR).
* `write_char(c)`: write a character byte `c` (int) to LCD's data register (DR).
* `clear_lcd()`: clear the LCD display.
* `initialize_lcd()`: reset and initialize the LCD module. (invoked during class initialization.)
* `goto_lcd_line(line, pos=0)`: Go to the beginning or the specified position `pos` (int, 0 to 15) of line `line` (int, 0 or 1). See table below:

| 16x2 LCD | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` | `pos` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `line=0` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| `line=1` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |

* `write_line(s, line)`: write a string `s` (str) to LCD line `line` (int, 0 or 1).
* `set_cgram_char(cgram_no, bitmap)`: set CGRAM number `cgram_no` (int, 0 to 7) and write 5x8 bitmap pixels `bitmap` (List[int], len=8). e.g. Define a custom character “↑” (Upwards Arrow) to CGRAM number `0`:

```python
import RPi.GPIO as GPIO
import lcd1602gpio

# Disable GPIO warnings
GPIO.setwarnings(False)
# Set GPIO pin mode. RPi pins described in this example use BCM.
GPIO.setmode(GPIO.BCM)

# create an instance of LCD1602GPIO with 8-bit mode.
lcd = lcd1602gpio.LCD1602GPIO(
        rs=7,
        e=8,
        db7=18,
        db6=23,
        db5=24,
        db4=25,
        db3=6,
        db2=13,
        db1=19,
        db0=26)

# define a custom character (Upwards Arrow) to CGRAM number 0.
lcd.set_cgram_char(0, [0b00000,
                       0b00100,
                       0b01110,
                       0b10101,
                       0b00100,
                       0b00100,
                       0b00000,
                       0b00000])

# Go to the beginning of Line 0.
lcd.goto_lcd_line(0)
# Display the character at CGRAM no 0.
lcd.write_char(0)

GPIO.cleanup()
```

## Caveats

* Since it's not for realtime applications, the clock pulse and delays are not precise.
  This might not work with your LCD module properly or require some tweaks on delays.
  Using LCD module on an Arduino will make your life easier.
* Read function is not yet implemented so it **does not read Busy Flag (BF)**
  and the default value of delay is much longer to ensure each LCD instruction
  can be executed in time.
  The performance of manipulating an LCD module will be slower than expected.

## Examples

The examples are based on LCD module LMM84S019D2E (PCB: M019F REV:A)
[manufactured by Nan Ya Plastics](https://www.npc.com.tw/j2npc/enus/prod/Electronic/Liquid-Crystal-Display(LCD)/Liquid%20Crystal%20Display%20(%20Character%20type%20)),
but its pin layout may be different to yours. You may need to change the wiring and
adjust the delay times if your LCD doesn't work.

You may need to add a resistor to your LCD backlight's anode (if available) to protect it.
You may also add a potentiometer to Contrast pin (aka V<sub>o</sub> or V<sub>L</sub>) to adjust your LCD contrast.

It supports both 8-bit and 4-bit data bus modes.
The R/W pin is grounded because read function is not yet implemented.

### 8-bit mode

The configuration requires 5V power, GND, 2 GPIO pins for signaling and 8 GPIO pins for 8-bit data bus.

| No. of LCD Pin | Name | Description | RPi Pin |
| --- | --- | --- | --- |
| 16  | K   | LCD Backlight Cathode   | GND |
| 15  | A   | LCD Backlight Anode     | 5V |
| 1   | GND | Ground                  | GND |
| 2   | +5V | +5V Power Supply        | 5V |
| 3   | Contrast | LCD Display Contrast | GND |
| 4   | RS  | Register Select         | GPIO 7 |
| 5   | R/W | Read/Write Switch       | GND |
| 6   | E   | Enable Signal           | GPIO 8 |
| 7   | DB0 | Data Bus                | GPIO 26 |
| 8   | DB1 | Data Bus                | GPIO 19 |
| 9   | DB2 | Data Bus                | GPIO 13 |
| 10  | DB3 | Data Bus                | GPIO 6 |
| 11  | DB4 | Data Bus                | GPIO 25 |
| 12  | DB5 | Data Bus                | GPIO 24 |
| 13  | DB6 | Data Bus                | GPIO 23 |
| 14  | DB7 | Data Bus                | GPIO 18 |

Import required Python modules and create an instance of `LCD1602GPIO`.

```python
import RPi.GPIO as GPIO
import lcd1602gpio

# Disable GPIO warnings
GPIO.setwarnings(False)
# Set GPIO pin mode. RPi pins described in this example use BCM.
GPIO.setmode(GPIO.BCM)

# create an instance of LCD1602GPIO with 8-bit mode.
# the LCD module must be already powered on here.
# the instance initializes the LCD module immediately during init.
lcd = lcd1602gpio.LCD1602GPIO(
        rs=7,
        e=8,
        db7=18,
        db6=23,
        db5=24,
        db4=25,
        db3=6,
        db2=13,
        db1=19,
        db0=26)

# write texts to Line 0 of the LCD.
lcd.write_line("abcdefghijklmnop", 0)
# write texts to Line 1 of the LCD.
lcd.write_line("1234567890123456", 1)

# Do GPIO cleanup manually before exiting.
GPIO.cleanup()
```

### 4-bit mode

The configuration requires 5V power, GND, 2 GPIO pins for signaling and 4 GPIO pins for 4-bit data bus.

Those 4 low order data bus pins DB0 to DB3 are unconnected.

| No. of LCD Pin | Name | Description | RPi Pin |
| --- | --- | --- | --- |
| 16  | K   | LCD Backlight Cathode   | GND |
| 15  | A   | LCD Backlight Anode     | 5V |
| 1   | GND | Ground                  | GND |
| 2   | +5V | +5V Power Supply        | 5V |
| 3   | Contrast | LCD Display Contrast | GND |
| 4   | RS  | Register Select         | GPIO 7 |
| 5   | R/W | Read/Write Switch       | GND |
| 6   | E   | Enable Signal           | GPIO 8 |
| 7   | DB0 | Data Bus (Unused)       | (None) |
| 8   | DB1 | Data Bus (Unused)       | (None) |
| 9   | DB2 | Data Bus (Unused)       | (None) |
| 10  | DB3 | Data Bus (Unused)       | (None) |
| 11  | DB4 | Data Bus                | GPIO 25 |
| 12  | DB5 | Data Bus                | GPIO 24 |
| 13  | DB6 | Data Bus                | GPIO 23 |
| 14  | DB7 | Data Bus                | GPIO 18 |

Import required Python modules and create an instance of `LCD1602GPIO`.

```python
import RPi.GPIO as GPIO
import lcd1602gpio

# Disable GPIO warnings
GPIO.setwarnings(False)
# Set GPIO pin mode. RPi pins described in this example use BCM.
GPIO.setmode(GPIO.BCM)

# create an instance of LCD1602GPIO with 4-bit mode.
# the LCD module must be already powered on here.
# the instance initializes the LCD module immediately during init.
lcd = lcd1602gpio.LCD1602GPIO(
        rs=7,
        e=8,
        db7=18,
        db6=23,
        db5=24,
        db4=25,
        db3=None,
        db2=None,
        db1=None,
        db0=None,
        dl_mode=lcd1602gpio.DL_4BIT)

# write texts to Line 0 of the LCD.
lcd.write_line("abcdefghijklmnop", 0)
# write texts to Line 1 of the LCD.
lcd.write_line("1234567890123456", 1)

# Do GPIO cleanup manually before exiting.
GPIO.cleanup()
```

## Reference

* [HD44780U (LCD-II), (Dot Matrix Liquid Crystal Display Controller/Driver) manual](https://cdn-shop.adafruit.com/datasheets/HD44780.pdf)

