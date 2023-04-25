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

displayio.release_displays()

# NOTES on Teyleten Robot display from Amazon
# The SPI mode is the 4-wire mode, which is NOT the normal SCLK, MISO, MOSI, and SS signals of SPI, 
# but are SCLK (labeled SCK), DC, MOSI (labeled SDA), and SS (labeled CS). 
# The DC pin, when in SPI mode, is a Data/Command select input (Data when it's high or '1' and 
# Command when it's low or '0')

# On Teyleten
# SCK (SCLK)  IO12
# SDA (MOSI)  IO11
# RES (Reset) IO9  
# DC        IO38
# CS (SS)   IO10

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

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

# Draw a label
text = "Hello World!"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
splash.append(text_area)

while True:
    pass
