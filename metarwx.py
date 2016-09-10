import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import time
import csv
import re
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
    return(city)
def getCountry():
    url = 'http://freegeoip.net/json/'
    r = requests.get(url)
    js = r.json()
    country = js['country_name']
    return(country)


#Organizes the METAR and translates it to plain english
def translateMetar(METAR):
    METAR = str(METAR.strip())
    print(METAR)
    rmkTemp = METAR.split('RMK')
    metRMK = rmkTemp[1]
    metMETAR = rmkTemp[0]
    metInfo = {}

    #Station
    metInfo['Station'] = metMETAR[:4]
    metStation = metInfo['Station']
    metMETAR = metMETAR[4:]
    metMETAR = str(metMETAR.strip())

    #Time
    metInfo['Time'] = metMETAR[:7]
    metMETAR = metMETAR[8:]
    metTime = [0, 0]
    metTime = '%s:%s' % (metInfo['Time'][2:4], metInfo['Time'][4:6])
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
    if metInfo['Winds'] == '00000KT':
        metWinds = ['Calm']
        metWinds = 'Calm'
    elif 'VRB' in metInfo['Winds']:
        metWindsDir = 'Variable'
        metWindsVel = metInfo['Winds'][3:5]
        metWinds = '%s @ %s KT' % (metWindsDir, metWindsVel)
    else:
        metWindsDir = metInfo['Winds'][:3]
        metWindsVel = metInfo['Winds'][3:5]
        if 'G' in metInfo['Winds']:
            metWindsGust = metInfo['Winds'][6:8]
            metWinds = '%s @ %s KT, Gusting to %s' % (metWindsDir, metWindsVel, metWindsGust)
        else:
            metWinds = '%s @ %s KT' % (metWindsDir, metWindsVel)
    if len(metMETAR.split()[0]) == 7:
        metInfo['VarWinds'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['VarWinds'], "")
        metWindsVar = metInfo['VarWinds']
        if 'G' in metInfo['Winds']:
            metWindsGust = metInfo['Winds'][6:8]
            metWinds = '%s, Variable between %s and %s @ %s KT, Gusting to %s' % (metWindsDir, metWindsVar[:3], metWindsVar[4:], metWindsVel, metWindsGust)
        else:
            metWinds = '%s, Variable between %s and %s @ %s KT' % (metWindsDir, metWindsVar[:3], metWindsVar[4:], metWindsVel)
    metMETAR = metMETAR.strip()

    #Visibility
    metVisibility = metMETAR.split()[0]
    metMETAR = metMETAR.replace(metVisibility, "")
    metVisibility = metVisibility[:2]
    metMETAR = metMETAR.strip()

    metRVR = 'None'
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
            metRVR = 'Runway %s, Visibility is %s, Tendency: %s' % (metRVR[0], metRVR[1], metRVR[2])
        metMETAR = metMETAR.strip()

    #Vicinity wx
    metVicinity = 'None'
    if 'VC' in metMETAR.split()[0] and not 'OVC' in metMETAR.split()[0]:
        metInfo['Vicinity'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Vicinity'], "")
        metVicinity = metInfo['Vicinity'][2:]
        if len(metVicinity) == 4:
            metVicinity = 'Vicinity ' + (dictDescriptors.get(metVicinity[:2], 'Unknown')) + ' ' + (dictConditions.get(metVicinity[2:], 'Unknown'))
        else:
            metVicinity = 'Vicinity ' + (dictConditions.get(metVicinity, 'Unknown'))
    metMETAR = metMETAR.strip()

    #Weather conditions
    metCondition = "None"
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
    metClouds = 'None'
    if metMETAR.split()[0][:3] in dictClouds:
        metClouds = ''
        metInfo['Clouds'] = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metInfo['Clouds'], "")
        metSkyCondition = metInfo['Clouds']
        metClouds = (dictClouds.get(metSkyCondition[:3], 'Unknown'))
        metCloudHeight = metSkyCondition[3:6].lstrip('0') + '00'
        if metClouds == "Sky Clear":
            metClouds = metClouds
        else:
            metClouds = metClouds + ' at ' + metCloudHeight + 'ft'
        while metMETAR.split()[0][:3] in dictClouds:
            metInfo['Clouds'] = metMETAR.split()[0]
            metMETAR = metMETAR.replace(metInfo['Clouds'], "")
            metSkyCondition = metInfo['Clouds']
            metClouds += ' &'
            metClouds = metClouds + ' ' + (dictClouds.get(metSkyCondition[:3], 'Unknown'))
            metCloudHeight = metSkyCondition[-3:].lstrip('0') + '00'
            if metClouds == "Sky Clear":
                metClouds = metClouds
            else:
                metClouds = metClouds + ' at ' + metCloudHeight + 'ft'
    metMETAR = metMETAR.strip()

    #Temperature
    metTemperature = metMETAR[:2]
    metDewpoint = metMETAR[3:5]
    metMETAR = metMETAR[5:]
    if metTemperature[:1] == 'M':
        metTemperature = '-' + metTemperature[1:] + 'C'
    else:
        metTemperature = metTemperature + 'C'
    metMETAR = metMETAR[1:]
    #Dewpoint
    metMETAR = metMETAR.replace(metDewpoint, "")
    if metDewpoint[:1] == 'M':
        metDewpoint = '-' + metDewpoint[1:] + 'C'
    else:
        metDewpoint = metDewpoint + 'C'
    metMETAR = metMETAR.strip()

    #Altimeter Setting
    if len(metMETAR) == 5:
        metAltimeter = metMETAR
        metAltimeter = '%s.%s"Hg' % (metAltimeter[1:3], metAltimeter[3:])
    else:
        metAltimeter = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metAltimeter, "")
        metAltimeter = '%s.%s"Hg' % (metAltimeter[1:3], metAltimeter[3:])
    metMETAR = metMETAR.strip()
    #Recent Wx
    metRecent = 'None'
    if 'RE' in metMETAR.split():
        metRecent = metMETAR.split()[0]
        metMETAR = metMETAR.replace(metRecent, "")
        metRecent = metRecent[2:]
        if len(metRecent) == 4:
            metRecent = 'Recent ' + (dictDescriptors.get(metRecent[:2], 'Unknown')) + ' ' + (dictConditions.get(metRecent[2:], 'Unknown'))
        else:
            metRecent = 'Recent ' + (dictConditions.get(metRecent, 'Unknown'))
    metMETAR = metMETAR.strip()

    #Wind Shear
    if 'WS' in metMETAR.split():
        metWindShear = metMETAR
        metMETAR = metMETAR.replace(metWindShear, "")
        if 'ALL RWY' in metWindShear:
            metWindShear = 'Wind Shear: All Runways'
        else:
            metWindShear = 'Wind Shear: Runway ' + metWindShear[6:]
    else: metWindShear = 'None'

    #RMK
    #CloudDetails
    metCloudType = metRMK.split()[0]
    metRMK = metRMK.strip()
    metCTOctas = (re.findall(r'\d+', metCloudType))
    metCTCover = (re.findall(r'\D+', metCloudType))
    cloudTypesNum = len(metCTCover)
    iternum = 0
    metCloudDetails = ""
    for clouds in metCTCover:
        metCloudDetails = metCloudDetails + dictCloudType.get(clouds) + ' ' + metCTOctas[iternum] + '/8 coverage; '
        iternum += 1
    metCloudDetails = metCloudDetails[:-2]
    metRMK = metRMK.replace(metCloudType, "")
    metRMK = metRMK.strip()

    #Density altitude
    metDensityAlt = metRMK.split()[-1]
    metRMK = metRMK.replace('DENSITY ALT', "")
    metRMK = metRMK.replace(metDensityAlt, "")
    metRMK = metRMK.strip()

    #Sea Level Pressure
    metSLP = metRMK.split()[-1]
    metRMK = metRMK.replace(metSLP, '')
    metSLP = metSLP[3:]
    metRMK = metRMK.strip()
    if metSLP[0] == '5' or metSLP[0] == '4' or metSLP[0] == '3' or metSLP[0] == '2' or metSLP[0] == '1' or metSLP[0] == '0':
        metSLP = "10" + metSLP[:-1] + "." + metSLP[-1] + ' hPa'
    else:
        metSLP = "9" + metSLP[:-1] + "." + metSLP[-1] + ' hPa'

    msgMETAR = 'Station: %s | Time of Observation: %s GMT | Winds: %s | Visibility: %s SM | Runway Visual Range: %s| Vicinity: %s| Present Weather Condition: %s | Cloud Heights: %s | Temperature: %s | Dewpoint: %s | Pressure: %s / %s | Recent Weather: %s | Wind Shear: %s | Cloud Details: %s | Density Altitude: %s | Remarks: %s' % (metStation, metTime, metWinds, metVisibility, metRVR, metVicinity, metCondition, metClouds, metTemperature, metDewpoint, metAltimeter, metSLP, metRecent, metWindShear, metCloudDetails, metDensityAlt, metRMK)
    return(msgMETAR)
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
    return(METAR)

def getICAO(userCity, userCountry, delimiter=None):
    import csv
    if not delimiter:
        delimiter = ','
    if userCountry == "Canada":
        reader = csv.reader(open('canairports.csv'), delimiter=delimiter)
        result = {}
        for row in reader:
            result[row[0]] = row[1]
        ICAO = result.get(userCity, 'CYOW')
    else:
        reader = csv.reader(open('airports.csv'), delimiter=delimiter)
        result = {}
        for row in reader:
            result[row[0]] = row[1]
        print(result)
        ICAO = result.get(userCity, 'CYOW')
    return(ICAO)

#Gets new METAR every hour



userCity = getLoc()
userCountry = getCountry()
userApCode = getICAO(userCity, userCountry)
updatedMETAR = getMetar(userApCode)
returnMETAR = translateMetar(updatedMETAR)
print(returnMETAR)


while 1 == 1:
    if (time.strftime("%M")) == '10':
        userCity = getLoc()
        userCountry = getCountry()
        userApCode = getICAO(userCity, userCountry)
        updatedMETAR = getMetar(userApCode)
        returnMETAR = translateMetar(updatedMETAR)
        print(returnMETAR)
    time.sleep(60)
