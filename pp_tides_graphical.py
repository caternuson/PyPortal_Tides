import time
import math
import board
import displayio
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

STATION_ID = "9447130" # find yours here: https://tidesandcurrents.noaa.gov/
UPDATE_TIME = 3 # 24 hour based time, ex: 3 = 3AM

DATA_SOURCE = "https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&format=json&units=metric&time_zone=lst_ldt&station="+STATION_ID
DATA_LOCATION = ["predictions"]

# determine the current working directory needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/tides_bg_graph.bmp")

# Connect to the internet and get local time
pyportal.get_local_time()

# Setup tide plot bitmap
VSCALE = 20
WIDTH = board.DISPLAY.width
HEIGHT = board.DISPLAY.height
tide_plot = displayio.Bitmap(WIDTH, HEIGHT, 3)
palette = displayio.Palette(3)
palette[0] = 0x0
palette[1] = 0xFFFFFF   # plot color
palette[2] = 0xFF0000   # current time
palette.make_transparent(0)
#tide_plot = displayio.TileGrid(canvas, pixel_shader=palette)

# Add tide plot to display
pyportal.splash.append(displayio.TileGrid(tide_plot, pixel_shader=palette))

# Setup date label
date_font = bitmap_font.load_font(cwd+"/fonts/Arial-12.bdf")
date_font.load_glyphs(b'1234567890-')
DATE_LABEL = Label(date_font, text="0000-00-00", color=0xFFFFFF, x=230, y=14)
pyportal.splash.append(DATE_LABEL)

def update_display():
    # Fetch data from NOAA
    tide_data = pyportal.fetch()

    t = time.localtime()
    xc  = int(((WIDTH - 1) / 1439) * (60*float(t.tm_hour) + float(t.tm_min)))

    # Main tide data plot
    for data in tide_data:
        d, t = data["t"].split(" ") # date and time
        h, m = t.split(":")         # hours and minutes
        v = data["v"]               # water level
        x = int(((WIDTH - 1) / 1439) * (60*float(h) + float(m)))
        y = (HEIGHT // 2) - int(VSCALE * float(v))
        y = 0 if y < 0 else y
        y = HEIGHT-1 if y >= HEIGHT else y
        if x == xc:
            yc = y
        try:
            tide_plot[x-1, y-1] = 1
            tide_plot[x  , y-1] = 1
            tide_plot[x+1, y-1] = 1

            tide_plot[x-1, y  ] = 1
            tide_plot[x  , y  ] = 1
            tide_plot[x+1, y  ] = 1

            tide_plot[x-1, y+1] = 1
            tide_plot[x  , y+1] = 1
            tide_plot[x+1, y+1] = 1
        except IndexError:
            pass

    DATE_LABEL.text = d

    # Current time location marker
    try:
        steps = 50
        dd = 2 * math.pi / steps
        for r in range(3, 6):
            o = 0.0
            for _ in range(steps):
                x = int(xc + r * math.cos(o))
                y = int(yc + r * math.sin(o))
                tide_plot[(x , y)] = 2
                o += dd
    except IndexError:
        pass

# First run update
update_display()

# Update daily
while True:
    if time.localtime().tm_hour == UPDATE_TIME:
        update_display()
        time.sleep(23 * 60 * 60)
    time.sleep(300)