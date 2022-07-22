#!/usr/bin/env python3
import requests
from urllib.parse import urlencode, parse_qs, splitquery
from datetime import datetime
import json
import time
import appdaemon.plugins.hass.hassapi as hass

#
# Stromer app
#

password = "FILL IN "
username = "FILL IN"
client_id = "RETRIEVE FROM DECOMPILED APK"

class stromer(hass.Hass):
    def initialize(self):
        starttime=time.time()
        while True:
            try:
                def get_code(client_id, username, password):
                    MAX_RETRIES = 20  #!Added https://stackoverflow.com/questions/33895739/python-requests-module-error-cant-load-any-url-remote-end-closed-connection
                    session = requests.Session()
                    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
                    session.mount('https://', adapter)
                    session.mount('http://', adapter)
                    url = "https://stromer-portal.ch/mobile/v4/login/"
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
                        "next": "/mobile/v4/o/authorize/?" + qs
                    }
                
                    res = s.post(url, data=data, headers=dict(Referer=url), allow_redirects=False)
                    res = s.send(res.next, allow_redirects=False)
                    _, qs = splitquery(res.headers["Location"])
                    code = parse_qs(qs)["code"][0]
                    return code
                
                
                def get_access_token(client_id, code):
                    url = "https://stromer-portal.ch/mobile/v4/o/token/"
                    params = {
                        "grant_type": "authorization_code",
                        "client_id": client_id,
                        "code": code,
                        "redirect_uri": "stromer://auth",
                    }
                
                    res = requests.post(url, params=params)
                    return res.json()["access_token"]
                
                
                def call_api(access_token, endpoint, params={}):
                    url = "https://api3.stromer-portal.ch/rapi/mobile/v4.1/%s" % endpoint
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
                access_token = get_access_token(client_id, code)
                bike = call_api(access_token, "bike")
                state = call_bike(access_token, bike, 'state/')
                position = call_bike(access_token, bike, 'position/')
     
                self.set_state("sensor.stromer_current_speed", state = state['bike_speed'])
                self.set_state("sensor.stromer_trip_distance", state = state['trip_distance'])
                self.set_state("sensor.stromer_avg_speed_trip", state = state['average_speed_trip'])
                self.set_state("sensor.stromer_triptime", state = state['trip_time'])
                self.set_state("sensor.stromer_battery_chargelevel", state = state['battery_SOC'])
                self.set_state("sensor.stromer_lockstate", state = state['lock_flag'])
                self.set_state("sensor.stromer_geocoded_location", state = '', attributes = {"altitude": position['altitude'], "latitude": position['latitude'], "longitude": position['longitude'], "icon": 'mdi:map'})
                self.set_state("sensor.stromer_batterytemp", state = state['battery_temp'])
                self.set_state("sensor.stromer_motortemp", state = state['motor_temp'])
                self.set_state("sensor.stromer_battery_healthstate", state = state['battery_health'])
                self.set_state("sensor.stromer_battery_poweron_cycles", state = state['power_on_cycles'])
                self.set_state("sensor.stromer_totaldistance", state = state['total_distance'])
                self.set_state("sensor.stromer_totaltime", state = state['total_time'])
                self.set_state("sensor.stromer_avg_energy", state = state['average_energy_consumption'])
                self.set_state("sensor.stromer_softwareversion", state = state['suiversion'])
                self.set_state("sensor.stromer_lastupdated", state = state['rcvts'])
                self.log("Omni data updated")
                time.sleep(60)
            except Exception:
                self.log("ERROR")
                time.sleep(300)
                continue
