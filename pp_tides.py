import time
import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

STATION_ID = "9447130" # find yours here: https://tidesandcurrents.noaa.gov/

DATA_SOURCE = "https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&interval=hilo&format=json&units=metric&time_zone=lst_ldt&station="+STATION_ID
DATA_LOCATION = ["predictions"]
UPDATE_TIME = 3 # 24 hour based time, ex: 3 = 3AM

# determine the current working directory needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/tides_bg.bmp")

# Connect to the internet and get local time
pyportal.get_local_time()

# Tide info setup
tide_font = bitmap_font.load_font(cwd+"/fonts/cq-mono-30.bdf")
tide_font.load_glyphs(b'1234567890:')
tide_colors =    { "L" : 0x11FFFF ,
                   "H" : 0x00FF00 }
tide_locations = { "L" : ((180, 80), (180, 165)) ,
                   "H" : (( 40, 80), ( 40, 165)) }

# Date info setup
date_font = bitmap_font.load_font(cwd+"/fonts/Arial-12.bdf")
date_font.load_glyphs(b'1234567890-')
date_color = 0xFFFFFF
date_location = (115, 228)

# Labels setup
HI_LABELS = [ Label(tide_font, text="00:00", color=tide_colors["H"], x=tide_locations["H"][0][0], y=tide_locations["H"][0][1]) ,
              Label(tide_font, text="00:00", color=tide_colors["H"], x=tide_locations["H"][1][0], y=tide_locations["H"][1][1]) ]
LO_LABELS = [ Label(tide_font, text="00:00", color=tide_colors["L"], x=tide_locations["L"][0][0], y=tide_locations["L"][0][1]) ,
              Label(tide_font, text="00:00", color=tide_colors["L"], x=tide_locations["L"][1][0], y=tide_locations["L"][1][1]) ]
DATE_LABEL = Label(date_font, text="0000-00-00", color=date_color, x=date_location[0], y=date_location[1])
labels = HI_LABELS + LO_LABELS + [DATE_LABEL]

# Add all the labels to the display
for label in labels:
    pyportal.splash.append(label)

def update_display():
    # Fetch data from NOAA
    tide_info = pyportal.fetch()

    # Clear current info
    for label in labels:
        label.text = ""

    # Extract high/low times and update labels
    h = l = 0
    for tide in tide_info:
        tide_type = tide["type"]
        tide_time = tide["t"].split(" ")[1]
        if tide_type == "H":
            HI_LABELS[h].text = tide_time
            h += 1
        if tide_type == "L":
            LO_LABELS[l].text = tide_time
            l += 1

    # Update date label
    DATE_LABEL.text = tide_info[0]["t"].split(" ")[0]

# First run update
update_display()

# Update daily
while True:
    if time.localtime().tm_hour == UPDATE_TIME:
        update_display()
        time.sleep(23 * 60 * 60)
    time.sleep(300)