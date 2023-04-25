# Show a bitmap from the flash drive on the display
# Use our Display class which defines our Teletyn 128x64 display

from display import Display
import displayio
import board

display = Display()

# Setup the file as the bitmap data source
bitmap = displayio.OnDiskBitmap("/images/purple.bmp")

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
display.show(group)

# Loop forever so you can enjoy your image
while True:
    pass