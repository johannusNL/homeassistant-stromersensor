#!/usr/bin/env python3
import requests
from urllib.parse import urlencode, parse_qs, splitquery
from datetime import datetime
import json
import time
import appdaemon.plugins.hass.hassapi as hass

password = "PASSWORD-Here"
username = "username@email.com"
client_id = "Clientid-here"
client_secret = "Secret-here"

class stromer(hass.Hass):
    def initialize(self):
        starttime=time.time()
        while True:
            def get_code(client_id, username, password):
                MAX_RETRIES = 20  #!Added https://stackoverflow.com/questions/33895739/python-requests-module-error-cant-load-any-url-remote-end-closed-connection
                session = requests.Session()
                adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
                session.mount('https://', adapter)
                session.mount('http://', adapter)
                url = "https://api3.stromer-portal.ch/users/login/"
                s = requests.session()
                res = s.get(url)
                s.cookies
            
                qs = urlencode({
                    "client_id":
                    client_id,
                    "response_type":
                    "code",
                    "redirect_url":
                    "stromerauth://auth",
                    "scope":
                    "bikeposition bikestatus bikeconfiguration bikelock biketheft bikedata bikepin bikeblink userprofile",
                })
            
                data = {
                    "password": password,
                    "username": username,
                    "csrfmiddlewaretoken": s.cookies.get("csrftoken"),
                    "next": "/o/authorize/?" + qs,
                }
            
                res = s.post(url, data=data, headers=dict(Referer=url), allow_redirects=False)
                res = s.send(res.next, allow_redirects=False)
                _, qs = splitquery(res.headers["Location"])
                code = parse_qs(qs)["code"][0]
                return code
            
            
            def get_access_token(client_id, client_secret, code):
                url = "https://api3.stromer-portal.ch//o/token/"
                data = {
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": "stromerauth://auth",
                }
            
                res = requests.post(url, data=data)
                return res.json()["access_token"]
            
            
            def call_api(access_token, endpoint, params={}):
                url = "https://api3.stromer-portal.ch/rapi/mobile/v2/%s" % endpoint
                headers = {"Authorization": "Bearer %s" % access_token}
                res = requests.get(url, headers=headers, params={})
                data = res.json()["data"]
                if isinstance(data, list):
                    return data[0]
                else:
                    return data
            
            
            def call_bike(access_token, bike, endpoint, cached="false"):
                endpoint = 'bike/%s/%s' % (bike["bikeid"], endpoint)
                params = {'cached': '%s' % cached}
                state = call_api(access_token, endpoint, params)
                return state
            
            
            code = get_code(client_id, username, password)
            access_token = get_access_token(client_id, client_secret, code)
            bike = call_api(access_token, "bike")
            state = call_bike(access_token, bike, 'state/')
            position = call_bike(access_token, bike, 'position/')
 
            
            self.set_state("sensor.stromer_lockstate", state = state['lock_flag'])
            self.set_state("sensor.stromer_current_speed", state = state['bike_speed'])
            self.set_state("sensor.stromer_battery_chargelevel", state = state['battery_SOC'])
            self.set_state("sensor.stromer_totalenergyconsumption", state = state['total_energy_consumption'])
            self.set_state("sensor.stromer_batterytemp", state = state['battery_temp'])
            self.set_state("sensor.stromer_total_distance", state = (int(state['total_distance'])))
            self.set_state("sensor.stromer_avg_speed", state = state['average_speed_trip'])
            self.set_state("sensor.stromer_softwareversion", state = state['suiversion'])
            self.set_state("sensor.stromer_battery_healthstate", state = state['battery_health'])
            self.set_state("sensor.stromer_triptime", state = state['trip_time'])
            self.set_state("sensor.stromer_motortemp", state = state['motor_temp'])
            self.set_state("sensor.stromer_totaltime", state = state['total_time'])
            self.set_state("sensor.stromer_geocoded_location", state = '', attributes = {"friendly_name": "Stromer GPS", "altitude": position['altitude'], "latitude": position['latitude'], "longitude": position['longitude'], "icon": 'mdi:map'})
            self.log("end of sensor writing")
            time.sleep(40.0 - ((time.time() - starttime) % 40.0))
