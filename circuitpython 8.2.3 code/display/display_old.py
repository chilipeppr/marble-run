"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import busio

# release display from prior boot
displayio.release_displays()

# NOTES on Teyleten Robot display from Amazon
# The SPI mode is the 4-wire mode, which is NOT the normal SCLK, MISO, MOSI, and SS signals of SPI, 
# but are SCLK (labeled SCK), DC, MOSI (labeled SDA), and SS (labeled CS). 
# The DC pin, when in SPI mode, is a Data/Command select input (Data when it's high or '1' and 
# Command when it's low or '0')

# On Teyleten  | GPIO for Lolin S2 Mini
# SCK (SCLK)     IO12
# SDA (MOSI)     IO11
# RES (Reset)    IO9  
# DC             IO38
# CS (SS)        IO10

class Display:
    def __init__(self, *args):

        print("Initting Display library...")

        oled_reset = board.IO9
        oled_cs = board.IO10
        oled_dc = board.IO38

        # Use for I2C
        # i2c = board.I2C()  # uses board.SCL and board.SDA
        # # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        # display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)

        # Use for SPI (SPI2 are the lower gpio numbers)
        #define TFT_CS 34 // 10 or 34
        #define TFT_MOSI 35 // 11 or 35
        #define TFT_SCLK 36 // 12 or 36
        #define TFT_MISO 37 // 13 or 37
        #define TFT_DC 38

        # spi = board.SPI()

        # In case board.SPI() doesn't work, or tell you what pins to use
        # import busio
        # spi = busio.SPI(board.SCK, MISO=board.MISO)
        spi = busio.SPI(clock=board.IO12, MOSI=board.IO11)

        display_bus = displayio.FourWire(spi, command=oled_dc, chip_select=oled_cs,
                                        reset=oled_reset, baudrate=1000000)

        WIDTH = 128
        HEIGHT = 64 #32  # Change to 64 if needed
        BORDER = 5

        self.display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

    def deinit():
        # release display from prior boot
        displayio.release_displays()
