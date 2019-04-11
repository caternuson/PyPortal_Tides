import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

STATION_ID = "9447130" # find yours here: https://tidesandcurrents.noaa.gov/
DATA_SOURCE = "https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&interval=hilo&format=json&units=metric&time_zone=lst_ldt&station="+STATION_ID
DATA_LOCATION = ["predictions"]

# determine the current working directory needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/tides_bg.bmp")

tide_font = bitmap_font.load_font(cwd+"/fonts/cq-mono-30.bdf")
tide_font.load_glyphs(b'1234567890:')
tide_colors = { "L" : 0x11FFFF ,
                "H" : 0x00FF00 }
tide_locations = { "L" : [(180,  85), (180, 170)] ,
                   "H" : [( 40,  85), ( 40, 170)] }

tide_info = pyportal.fetch()

for tide in tide_info:
    x, y = tide_locations[tide["type"]].pop(0)
    text = tide["t"].split(" ")[1]
    label = Label(tide_font, text=text)
    label.x = x
    label.y = y
    label.color = tide_colors[tide["type"]]
    pyportal.splash.append(label)