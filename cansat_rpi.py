#ASPiRE UoWM 2019
#CanSat in Greece 2019

import os
import string
import time
import datetime
import serial
import board
import busio
import smbus
import adafruit_bmp280
from picamera import PiCamera, Color

cameracapture = True

#Telemetry serial port
Telemetry_SerialConnection = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600, timeout = 1)

# Create library object using Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(0) for older version boards
#Device_Address = 0x68 # MPU6050 device address

if cameracapture == True:
	camera = PiCamera()
	camera.resolution = (3264, 2448)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

#GPS Serial port
GPS_port = "/dev/ttyAMA0"
GPS_SerialConnection = serial.Serial(GPS_port, baudrate = 9600, timeout = 1)

def timestamp():
	return time.time()

def read_GPS():
	GPS_SerialConnection.flushInput()
	GPS_Data = GPS_SerialConnection.readline() #Read raw data from GPS chipset (NEO-6M)
	GPS_DataString = str(GPS_Data) #Raw data is binary. We need string to process.

	if 'GGA,' in GPS_DataString:
		GPGGAStringDecoded = GPS_DataString[18:30] + "(Latitude)|" + GPS_DataString[32:44] + "(Longitude)"
		f = open("nmea_strings.txt", "a")
		f.write(GPS_DataString + "\n")
		f.close()
		return "|" + GPGGAStringDecoded

def read_GPS_Latitude():
	GPS_SerialConnection.flushInput()
	GPS_Data = GPS_SerialConnection.readline() #Read raw data from GPS chipset (NEO-6M)
	GPS_DataString = str(GPS_Data) #Raw data is binary. We need string to process.

	if 'GGA,' in GPS_DataString:
		Latitude = "Lat" + GPS_DataString[18:30] + "\n"
		return Latitude

def read_GPS_Longitude():
	GPS_SerialConnection.flushInput()
	GPS_Data = GPS_SerialConnection.readline() #Read raw data from GPS chipset (NEO-6M)
	GPS_DataString = str(GPS_Data) #Raw data is binary. We need string to process.

	if 'GGA,' in GPS_DataString:
		Longitude = "Lon" + GPS_DataString[32:44] + "\n"
		return Longitude

def read_BMP280():
	bmp280.sea_level_pressure = 1013.25
	sensordata = "|Temperature=%0.1f(C)" %bmp280.temperature + "|Pressure=%0.1f(hPa)" %bmp280.pressure + "|Altitude=%0.2f(m)" %bmp280.altitude
	return sensordata

def read_BMP280_Temperature():
	bmp280.sea_level_pressure = 1013.25
	sensordata = "Tmp%0.1f(C)\n" %bmp280.temperature
	return sensordata

def read_BMP280_Pressure():
	bmp280.sea_level_pressure = 1013.25
	sensordata = "Prs%0.1f(hPa)\n" %bmp280.pressure
	return sensordata

def read_BMP280_Altiture():
	bmp280.sea_level_pressure = 1013.25
	sensordata = "Alt%0.2f(m)\n" %bmp280.altitude
	return sensordata

def main():
	try:
		i = 0 #Counter for data lines

		while True:
			#Main Loop Start
			while True:
				gpsDataForFileTransmission = read_GPS()
				if type(gpsDataForFileTransmission) is str:
					break

			#mpu6050DataForFileTransmission = read_MPU6050()
			bmp280DataForFileTransmission = read_BMP280()
			finalData = "|" + str(i) + "|" + str(timestamp()) + gpsDataForFileTransmission + bmp280DataForFileTransmission
			print(finalData)
			i = i + 1
			f = open("measurements.txt", "a")
			f.write(finalData + "\n")
			f.close()

			TEMP = read_BMP280_Temperature()
			Telemetry_SerialConnection.write(TEMP.encode())
			time.sleep(1)
			PRESS = read_BMP280_Pressure()
			Telemetry_SerialConnection.write(PRESS.encode())
			time.sleep(1)
			ALT = read_BMP280_Altiture()
			Telemetry_SerialConnection.write(ALT.encode())
			time.sleep(1)
			while True:
				LAT = read_GPS_Latitude()
				if type(LAT) is str:
					break
			Telemetry_SerialConnection.write(LAT.encode())
			time.sleep(1)
			while True:
				LON = read_GPS_Longitude()
				if type(LON) is str:
					break
			Telemetry_SerialConnection.write(LON.encode())
			time.sleep(1)
			if cameracapture == True:
				camera.start_preview()
				time.sleep(1)
				print("Capturing format: jpeg | picture\n")
				camera.capture('images/image%s.jpg' %str(timestamp()), 'jpeg')
				camera.stop_preview()

			time.sleep(1)
			#Main Loop End
	except KeyboardInterrupt:
		GPS_SerialConnection.close()
		Telemetry_SerialConnection.close()

if __name__ == "__main__":
	main()