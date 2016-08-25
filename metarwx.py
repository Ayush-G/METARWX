import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import time
import re
METAR = "CYOW 051200Z AUTO CCA 30015G20KT 260V340 3/4SM R36/4000FT/D R27L/3000V5000FT/U VCRA +BLSN FZRA FEW008 BKN012 OVC025 14/M05 A3015 RESN WS RWY36C RMK SF6AC1 ACSL OVR RDG NW SLP992"
dictDescriptors = {'-': 'Light',
                    '+': 'Heavy',
                    'MI': 'Shallow',
                    'BC': 'Patches',
                    'DR': 'Drifting',
                    'BL': 'Blowing',
                    'SH': 'Shower',
                    'TS': 'Thunderstorm',
                    'PR': 'Partial',
                    'FZ': 'Freezing'}
dictConditions = {'DZ': 'Drizzle',
                    'RA': 'Rain',
                    'SN': 'Snow',
                    'SG': 'Snow Grains',
                    'PL': 'Ice Pellets',
                    'GR': 'Hail',
                    'GS': 'Snow Pellets',
                    'IC': 'Ice Crystals',
                    'UP': 'Unknown',
                    'HZ': 'Haze',
                    'FU': 'Smoke',
                    'SA': 'Sand',
                    'DU': 'Dust',
                    'FG': 'Fog',
                    'BR': 'Mist',
                    'VA': 'Volcanic Ash',
                    'PO': 'Dust/Sand Whirls',
                    'SS': 'Sandstorm',
                    'DS': 'Duststorm',
                    'SQ': 'Squalls',
                    'FC': 'Funnel Cloud',
                    'SH': 'Showers'}
dictClouds = {'CLR': 'Sky Clear',
                'SKC': 'Sky Clear',
                'FEW': 'Few Clouds',
                'SCT': 'Scattered Clouds',
                'BKN': 'Broken Clouds',
                'OVC': 'Overcast Clouds'}

dictCloudType = {'CB': 'Cumulonimbus',
                    'TCU': 'Towering Cumulus',
                    'CU': 'Cumulus',
                    'CF': 'Cumulus Fractus',
                    'SC': 'Stratocumulus',
                    'NS': 'Nimbostratus',
                    'ST': 'Stratus',
                    'SF': 'Stratus Fractus',
                    'AS': 'Altostratus',
                    'AC': 'Altocumulus',
                    'ACC': 'Altocumulus Castellanus',
                    'CI': 'Cirrus',
                    'CC': 'Cirrocumulus'}
#Uses the user ip to get the city and time zone
def getLoc():
    url = 'http://freegeoip.net/json/'
    r = requests.get(url)
    js = r.json()
    city = js['city']
    timezone = js['time_zone']

#Organizes the METAR and translates it to plain english
def translateMetar(METAR):
    METAR = METAR.strip()
    rmkTemp = METAR.split('RMK')
    metRMK = rmkTemp[1]
    metMETAR = rmkTemp[0]
    metInfo = {}

    #Station
    metInfo['Station'] = metMETAR[:4]
    metMETAR = metMETAR[4:]
    metMETAR = metMETAR.strip()

    #Time
    metInfo['Time'] = metMETAR[:7]
    metMETAR = metMETAR[8:]
    metTime = [0, 0]
    metTime[0] = metInfo['Time'][:3]
    metTime[1] = metInfo['Time'][3:-1]
    metMETAR = metMETAR.strip()

    #Remove AUTO and CCA
    if "AUTO" in metMETAR:
        metMETAR = metMETAR.replace('AUTO', '')
    if "CCA" in metMETAR:
        metMETAR = metMETAR.replace('CCA', '')
    metMETAR = metMETAR.strip()

    #Winds
    metInfo['Winds'] = metMETAR.split()[0]
    metMETAR = metMETAR.replace(metInfo['Winds'], "")
    metWinds = ['0', '0', '0']
    if metInfo['Winds'] == '00000KT':
        metWinds = ['Calm']
    elif 'VRB' in metInfo['Winds']:
        metWinds[0] = 'Variable'
        metWinds[1] = metInfo['Winds'][3:5]
    else:
        metWinds[0] = metInfo['Winds'][:3]
        metWinds[1] = metInfo['Winds'][3:5]
    if 'G' in metInfo['Winds']:
        metWinds[0] = metInfo['Winds'][:3]
        metWinds[1] = metInfo['Winds'][3:5]
        metWinds[2] = metInfo['Winds'][6:8]

    if len(metMETAR.split()[0]) == 7:
        metInfo['VarWinds'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['VarWinds'], "")
        metWinds[0] = metInfo['VarWinds']
    metMETAR = metMETAR.strip()

    #Visibility
    metInfo['Visibility'] = metMETAR.split('SM')[0]
    metMETAR = metMETAR.replace(metInfo['Visibility'], "")
    metVisibility = metInfo['Visibility']
    metMETAR = metMETAR[3:]
    metMETAR = metMETAR.strip()

    if '/' in metMETAR.split()[0]:
        metRVR = ['0', '0', '0']
        while '/' in metMETAR.split()[0]:
            metInfo['RVR'] = metMETAR.split()[0]
            metMETAR = metMETAR.replace(metInfo['RVR'], "")
            if metRVR != ['0', '0', '0']:
                metRVR.append(metInfo['RVR'].split('/')[0])
                metRVR.append(metInfo['RVR'].split('/')[1])
                metRVR.append(metInfo['RVR'][-1])
            else:
                metRVR[0] = metInfo['RVR'].split('/')[0]
                metRVR[1] = metInfo['RVR'].split('/')[1]
                metRVR[2] = metInfo['RVR'][-1]
        metMETAR = metMETAR.strip()

    #Vicinity wx
    if 'VC' in metMETAR.split()[0]:
        metInfo['Vicinity'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Vicinity'], "")
        metVicinity = metInfo['Vicinity'][2:]
        if len(metVicinity) == 4:
            metVicinity = 'Vicinity ' + (dictDescriptors.get(metVicinity[:2], 'Unknown')) + ' ' + (dictConditions.get(metVicinity[2:], 'Unknown'))
        else:
            metVicinity = 'Vicinity ' + (dictConditions.get(metVicinity, 'Unknown'))
    metMETAR = metMETAR.strip()

    #Weather conditions
    if metMETAR.split()[0][:1] in dictDescriptors or metMETAR.split()[0][-2:] in dictConditions:
        metCondition = ''
        metInfo['Condition'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Condition'], "")
        metWeather = metInfo['Condition']
        if metWeather[:1] in dictDescriptors:
            metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[:1], 'Unknown'))
            if metWeather[1:3] in dictDescriptors:
                metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[1:3], 'Unknown'))
        if metWeather[:2] in dictDescriptors:
            metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[:2], 'Unknown'))
        metCondition = metCondition + ' ' + (dictConditions.get(metWeather[-2:], 'Unknown'))
        while metMETAR.split()[0][:1] in dictDescriptors or metMETAR.split()[0][-2:] in dictConditions:
            metInfo['Condition'] = metMETAR.split()[0]
            metMETAR = metMETAR.replace(metInfo['Condition'], "")
            metWeather = metInfo['Condition']
            metCondition += ' &'
            if metWeather[:1] in dictDescriptors:
                metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[:1], 'Unknown'))
                if metWeather[1:3] in dictDescriptors:
                    metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[1:3], 'Unknown'))
            if metWeather[:2] in dictDescriptors:
                metCondition = metCondition + ' ' + (dictDescriptors.get(metWeather[:2], 'Unknown'))
            metCondition = metCondition + ' ' + (dictConditions.get(metWeather[-2:], 'Unknown'))
        metMETAR = metMETAR.strip()

        #Cloud coverage and altitude
        if metMETAR.split()[0][:3] in dictClouds:
            metClouds = ''
            metInfo['Clouds'] = metMETAR.split()[0]
            metMETAR = metMETAR.replace(metInfo['Clouds'], "")
            metSkyCondition = metInfo['Clouds']
            metClouds = (dictClouds.get(metSkyCondition[:3], 'Unknown'))
            metCloudHeight = metSkyCondition[-3:].lstrip('0') + '00'
            metClouds = metClouds + ' at ' + metCloudHeight + 'ft'
            while metMETAR.split()[0][:3] in dictClouds:
                metInfo['Clouds'] = metMETAR.split()[0]
                metMETAR = metMETAR.replace(metInfo['Clouds'], "")
                metSkyCondition = metInfo['Clouds']
                metClouds += ' &'
                metClouds = metClouds + ' ' + (dictClouds.get(metSkyCondition[:3], 'Unknown'))
                metCloudHeight = metSkyCondition[-3:].lstrip('0') + '00'
                metClouds = metClouds + ' at ' + metCloudHeight + 'ft'
            metMETAR = metMETAR.strip()

        #Temperature
        metInfo['Temperature'] = metMETAR.split('/')[0]
        metMETAR = metMETAR.replace(metInfo['Temperature'], "")
        metTemperature = metInfo['Temperature']
        if metTemperature[:1] == 'M':
            metTemperature = '-' + metTemperature[1:] + 'C'
        else:
            metTemperature = metTemperature + 'C'
        metMETAR = metMETAR[1:]

        #Dewpoint
        metInfo['Dewpoint'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Dewpoint'], "")
        metDewpoint = metInfo['Dewpoint']
        if metDewpoint[:1] == 'M':
            metDewpoint = '-' + metDewpoint[1:] + 'C'
        else:
            metDewpoint = metDewpoint + 'C'
        metMETAR = metMETAR.strip()

        #Altimeter Setting
        metInfo['Altimeter'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Altimeter'], "")
        metAltimeter = metInfo['Altimeter']
        metAltimeter = '%s.%s"Hg' % (metAltimeter[1:3], metAltimeter[3:])
        metMETAR = metMETAR.strip()

        #Recent Wx
        if 'RE' in metMETAR.split()[0]:
            metRecent = metMETAR.split()[0]
            metMETAR = metMETAR.replace(metRecent, "")
            metRecent = metRecent[2:]
            if len(metRecent) == 4:
                metRecent = 'Recent ' + (dictDescriptors.get(metRecent[:2], 'Unknown')) + ' ' + (dictConditions.get(metRecent[2:], 'Unknown'))
            else:
                metRecent = 'Recent ' + (dictConditions.get(metRecent, 'Unknown'))
        metMETAR = metMETAR.strip()

        #Wind Shear
        metWindShear = metMETAR
        metMETAR = metMETAR.replace(metWindShear, "")
        if 'ALL RWY' in metWindShear:
            metWindShear = 'Wind Shear: All Runways'
        else:
            metWindShear = 'Wind Shear: Runway ' + metWindShear[6:]
translateMetar(METAR)




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

#apCode = 'CYOW'
#getLoc()
#getMetar(apCode)

'''
while True:
    if (time.strftime("%M", time.gmtime()))== '10':
        getMetar(apCode)
    time.sleep(60)
    #getTime()
'''
