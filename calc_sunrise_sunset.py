import datetime
import time
from math import sin, asin, acos, cos, tan, radians, degrees
import pytz
from datetime import datetime, timedelta

def is_dst():
    n = datetime.now()
    dt = time.mktime((n.year, n.month, n.day, 12, 0, 0, -1, -1, -1))
    return time.localtime(dt).tm_isdst
   
def convert_from_utc(julian_date):
	unixTime = (julian_date - 2440587.5) * 86400
	unixConvertDate = datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
	return (unixConvertDate + timedelta(seconds=unixTime))
	
	
# Calculations inspired by the wiki page:
# https://en.wikipedia.org/wiki/Sunrise_equation
def calc_sunrise_sunset(date, longitude, latitude, timeZone):
	debug = False
	# M = Mean anomoly
	# C = Equation of center
	# lambda = elicptical longitude of the sun = eliptical_longitude_sun
	# delta = declination of the sun 

	# Compute julian date
	unix_epoch = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
	date_utc = date.replace(tzinfo=pytz.utc)
	days_since = (date_utc - unix_epoch)
	julian_date = days_since.days + 2451545

    # Compute julian cycle
	julian_cycle = (julian_date - 2451545 - 0.0009) - (longitude / 360)
	n = round(julian_cycle)
	julian_solar_noon = 2451545 + 0.0009 + (longitude / 360) + n
	M = (357.5291 + 0.98560028 * (julian_solar_noon - 2451545)) % 360
	C = (1.9148 * sin(radians(M))) + (0.0200 * sin(2 * radians(M))) + (0.0003 * sin(3 * radians(M)))
	eliptical_longitude_sun = (M + 102.9372 + C + 180) % 360
	julian_date_solar_noon = julian_solar_noon + (0.0053 * sin(radians(M))) - \
	                               (0.0069 * sin(2 * radians(eliptical_longitude_sun)))
    # Compute declination of the sun
	delta = degrees(asin(sin(radians(eliptical_longitude_sun)) * sin(radians(23.44))))
	H = degrees(acos((sin(radians(-0.83)) - sin(radians(latitude)) * sin(radians(delta))) / \
	                 (cos(radians(latitude)) * cos(radians(delta)))))
    # Compute solar noon
	julian_solar_noon2 = 2451545 + 0.0009 + ((H + longitude) / 360) + n
	
	julian_solar_noon_datetime = convert_from_utc(julian_date_solar_noon)
    # Now compute sunrise and sunset (in julian format)
	julian_sunset = julian_solar_noon2 + (0.0053 * sin(radians(M))) - (0.0069) * sin(2 * radians(eliptical_longitude_sun))
	julian_date_sunrise = julian_date_solar_noon - (julian_sunset - julian_date_solar_noon)
    # Now convert to UTC
	sunrise_datetime = convert_from_utc(julian_date_sunrise).astimezone(timeZone)
	sunset_datetime = convert_from_utc(julian_sunset).astimezone(timeZone)

	if (debug == True):
		print("julian date: %s" % julian_date)
		print("n*: ", julian_cycle)
		print("n: ", n)
		print("julian_solar_noon:  ", julian_solar_noon)
		print("Mean anomoly: ", M)
		print("Equation of center: ", C)
		print("eliptical longitude (lambda): ", eliptical_longitude_sun)
		print("julian_date_solar_noon: ", julian_date_solar_noon)
		print("delta (sun's declination): ", delta)
		print("H (hour angle): ", H)
		print ("julian_solar_noon2 (julian_solar_noon using H): ", julian_solar_noon2)
		print("date time transit: ", julian_solar_noon_datetime)
		print("date time transit tz: ", julian_solar_noon_datetime.astimezone(timeZone))
		print("IS DST: ", is_dst())
		print("julian_date_sunrise: ", julian_date_sunrise, " >>> ", sunrise_datetime)
		print("julian_sunset: ", julian_sunset, " >>> ", sunset_datetime)
	
	return (sunrise_datetime, sunset_datetime)





