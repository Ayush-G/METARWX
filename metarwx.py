import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import time

#Uses the user ip to get the city and time zone
def getLoc():
    url = 'http://freegeoip.net/json/'
    r = requests.get(url)
    js = r.json()
    city = js['city']
    timezone = js['time_zone']
    print(city)
    print(timezone)

#Organizes the METAR and translates it to plain english
def translateMetar(METAR):
    METAR.strip()
    rmkTemp = METAR.split('RMK')
    metRMK = rmkTemp[1]
    metList = rmkTemp[0].split(' ')
    print(metList)
    print(metRMK)
    metInfo = {}
    metInfo['Station'] = metList[0]
    metInfo['Time'] = metList[1]
    metInfo['Wind'] = metList[2]
    metInfo['Visibility'] = metList[3]
    metInfo['Clouds'] = metList[4]
    metInfo['Temperature'] = metList[5]
    metInfo['Altimeter'] = metList[6]
    print(metInfo)

#Submits ICAO code to get METAR
def getMetar(ICAO):    
    url = 'https://aviationweather.gov/metar/data?'  #encodes the URL with the ICAO code
    values = {'ids': ICAO,
              'format': 'raw',
              'date': '0',
              'hours': '0',
              'taf': 'off'}
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17" #Makes script look human
    req = urllib.request.Request(url, data, headers = headers)

    r = urllib.request.urlopen(req).read() #Gets the website data
    soup = BeautifulSoup(r, "lxml")
    letters = soup.find_all("div", {"id": "awc_main_content"})
    for item in letters:
        METAR =(item.text[738:]) #gets only the text, trims to only the metar
        METAR = METAR.strip()
    print(METAR)
    translateMetar(METAR)

#Gets the time in UTC and Local
def getTime():
    print("UTC Time is: ", (time.strftime("%H:%M", time.gmtime())))
    print("Local Time is: ", (time.strftime("%H:%M")))
          
#Gets new METAR every hour    
apCode = 'CYOW'
getLoc()
getMetar(apCode)

    
while True:
    if (time.strftime("%M", time.gmtime()))== '10':
        getMetar(apCode)
    time.sleep(60)
    getTime()



