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
* Write a line of string and display it on LCD.
* Clear LCD display.

This module cannot:

* Read any data or address from LCD.
* Any other HD44780-supported operations with writing to LCD involved. (e.g. Write to CGRAM, etc.)

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
adjust the delay times if the LCD doesn't work.

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

