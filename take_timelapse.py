#!/usr/bin/python

from calc_sunrise_sunset import calc_sunrise_sunset
from datetime import datetime, timedelta
import os
from picamera import PiCamera
import pytz
import shlex
import shutil
import subprocess
from time import sleep

# This script is called using CRON to start the image capture each day
# e.g.  /some/path/to/time lapse script/take_timelapse.py

# To use this script, replace all values in angle brackets '<>' with appropriate
# values for your application.
ln = 40.71 # Specify longitude for calculation
lat = 74.0 # Specify latitude for calculation
delay = 30 # seconds
tz = pytz.timezone('<TIME ZONE FOR CALCULATION>')

date_time_now = datetime.now(tz=tz)
path = "<LOCATION TO IMAGES DIR>/%s" % date_time_now.strftime('%d-%b-%Y')
os.mkdir(path)
os.chdir(path)

# Calculate time values
(sunrise, sunset) = calc_sunrise_sunset(date_time_now, ln, lat, tz)
# Time delta helps create start/stop time no actually sunrise/sunset
time_offset = timedelta(hours=0, minutes=40)
start_time = sunrise - time_offset 
stop_time = sunset + time_offset
sleep_time = start_time - date_time_now

# Handles the case where the script was started manually
if sleep_time.total_seconds() < 0:
    sleep_time = timedelta()

# If the script is started before sunrise, sleep until then
sleep(sleep_time.total_seconds())
date_time_now = datetime.now(tz=tz)

if date_time_now >= start_time:
    camera = PiCamera()
    # Wait for the automatic gain control to settle
    # Now fix the values
    camera.awb_mode = 'auto'
    sleep(2)
    camera.start_preview()
    sleep(2)
    camera.stop_preview()

    for filename in camera.capture_continuous('img-{counter:04d}.jpg'):
        sleep(delay) # wait in seconds 
        curr_time = datetime.now(tz=tz)

        if curr_time >= stop_time:
            break
    
    mp4_file = "%s.mp4" % curr_time.strftime("%d-%b-%Y")
    # ffmpeg command to create an mp4 from all the images
    cmd = "ffmpeg -r 25 -i img-%4d.jpg -vcodec libx264 -crf 25 -pix_fmt yuv420p " + mp4_file
    subprocess.call(shlex.split(cmd))
    # Convert pics to MP4 
    # Clean up all pics from current day
    month = curr_time.strftime("%B")
    cmd = "python <PATH TO UPLOAD SCRIPT>/upload_video.py  --file <PATH TO GENERATED MP4> --title \"Appropriate video title\" --description \"Appropriate video description\" --privacyStatus public --keywords \"Appropriate keywords\""
    
    os.chdir("<CHANGE DIR TO upload_video.py LOCATION>")
    output = subprocess.check_output(shlex.split(cmd))
    result = output.find("successfully")
    
    # If the upload was successful, remove the directory
    # that was created
    if (result > 0):
        shutil.rmtree(path)
