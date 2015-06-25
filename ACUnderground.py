#!/usr/bin/env python
import re, requests, time,json

class ACUnderground:
	def __init__(self, email, password, WUStation, WUPass):
		self.email = email
		self.password = password
		self.WUStation = WUStation
		self.WUPass = WUPass
		self.s = requests.Session()
	
	def Authenticate(self):
		#Fetch login page	
		r  = self.s.get('https://acu-link.com/')

		#Scan for authentication token
		m = re.search('<input name="authenticity_token" type="hidden" value="(([^"]|\\")*=)" /></div>',r.text)
		authenticity_token = m.group(1)

		#Authenticate
		Data = {'authenticity_token':authenticity_token, 'user_session[email]': self.email, 'user_session[password]': self.password}
		r = self.s.post('https://acu-link.com/user_session',data=Data)
		
		#Get user
		m = re.search('<div class= "hidden" id="user-id">(\d*)</div>',r.text)
		self.user = m.group(1)	
	
	def GetReadings(self):
		r = self.s.get('https://acu-link.com/users/' + self.user + '/widget_refresh')
		
		Data ={}
		#Loop over sensors
		for Sensor in r.json:
			Type =  Sensor['user_sensor']['sensor']['type_alias']
			if Type == 'PressureSensor':
				Data['Barometer'] =  float(Sensor['user_sensor']['formatted_current_readings']['formatted_reading'])
			elif Type == 'TemperatureSensor':
				Data['Temp'] = float(Sensor['user_sensor']['formatted_current_readings']['formatted_reading']) + float(Sensor['user_sensor']['formatted_current_readings']['formatted_decimal'])
			elif Type == 'HumiditySensor':
				Data['Humidity'] = float(Sensor['user_sensor']['formatted_current_readings']['formatted_reading'])
			elif Type == 'RainfallSensor':
				Data['Rain'] = float(Sensor['user_sensor']['formatted_current_readings']['formatted_reading'])
			elif Type == 'WindVelocitySensor':
				Data['WindSpeed'] = float(Sensor['user_sensor']['formatted_current_readings']['formatted_reading'])
				Data['WindDir'] = Sensor['user_sensor']['formatted_current_readings']['formatted_direction']
			
			
		return Data

	def WUUpload(self,Data):
		WindDirs = {'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5, 'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5, 'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5, 'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5}
	
		Payload = {'dateutc': 'now', 
			'ID': self.WUStation,
			'PASSWORD': self.WUPass,
			'action': 'updateraw',
			'reamtlime': 1,
			'rtfreq': 5,
			'winddir': WindDirs[Data['WindDir']],
			'windspeedmph': Data['WindSpeed'],
			'humidity': Data['Humidity'],
			'tempf': Data['Temp'],
			'dailyrainin': Data['Rain'],
			'baromin': Data['Barometer']
			}
		#Upload to WUUpload
		r = requests.get('http://rtupdate.wunderground.com/weatherstation/updateweatherstation.php',params=Payload)
		
	
ACU = ACUnderground('aculink email', 'aculink password', 'WUnderground Station', 'WUnderground Password') #Username, Password for acu-link, WUnderground Station, Password
ACU.Authenticate()
while 1:
	Data = ACU.GetReadings()
	ACU.WUUpload(Data)
	time.sleep(5)