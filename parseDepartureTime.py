import numpy as np
import os
import pandas as pd
import requests
import time
from datetime import datetime
import ipdb
import sys

from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose',
     color_scheme='Linux', call_pdb=1)

from lxml import etree
import logging
logging.basicConfig(filename='parse.log', filemode='w', level=logging.WARNING)
logging.disabled = True

# DingSessions = {} # dict of dicts: {stop_name:{'isValid':True, 'sessionID':sessID, 'url':url},...}
watchingTrainID = None

def takeAndSavePhoto():
    # TODO implement raspi stuff

    print('click!_'+ datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+'_ID'+str(watchingTrainID))

# TODO: detect when session time out occurs to set DingSession to invalid
def parse_xml(url, verbose=False):
    r = requests.get(url)

    logging.debug('get url: '+ url)
    # tree = ElementTree.fromstring(content)
    try:
        tree = etree.fromstring(r.content) #.decode('utf-8'))
        logging.debug('successfully received XML')
    except etree.XMLSyntaxError as e:
        print('Error %s occured while trying to parse xml: %s' % (e, r.content))

    # tree = etree.fromstring('')

    if verbose:
        print(etree.tostring(tree, pretty_print=True, encoding="unicode"))
        # writes xml response to file
    xml_object = etree.tostring(tree,
                                pretty_print=True,
                                xml_declaration=True,
                                encoding='UTF-8')

    # TODO can xml be logged via logging module?
    with open("xmlfile.xml", "wb") as writer:
        writer.write(xml_object)
    logging.debug(xml_object.decode("utf-8"))



    curStop = tree.find(".//itdMapItemList").tail


    dmMonitor = []
    for el in tree.iter('itdDeparture'):
        if verbose:
            print('processing node:')
            print(etree.tostring(el, pretty_print=True, encoding="unicode"))

        itdServingLine = el.find("itdServingLine")
        key = itdServingLine.get('key')
        direction = itdServingLine.get("direction")
        linie = itdServingLine.get("number")
        if itdServingLine.get("motType") == '5':
            typ = 'Bus'
        elif itdServingLine.get("motType") == '4':
            typ = 'Tram'
        else:
            raise ValueError('Unkown motType '+itdServingLine.get("motType")+' occured')

        realtime = itdServingLine.get("realtime")

        departure = int(el.get("countdown")) - 1
        platform = el.get("platformName")

        itdNoTrain = itdServingLine.find("itdNoTrain") # sicher? nicht itdServingLine?
        delay = itdNoTrain.get("delay")

        itdRouteDescText = itdServingLine.find("itdRouteDescText")
        routeText = itdRouteDescText.text

        if verbose:
            print(key, direction, linie, typ, realtime)
            print(departure, platform)
            print(delay)
            print(routeText)
        if int(realtime) == 1 and int(linie) <= 16 or linie.startswith('N') or linie == 'E':
            arr =(key, linie, direction, int(departure), typ, routeText)
            dmMonitor.append(arr)


    dmMonitor.sort(key=lambda x: x[2])
    if verbose:
        print('Abfahrt von %s:' % curStop)
        [print('%s Linie %s (ID%s) - nach %s - Abfahrt: %d min - über: %s' %
               (typ, linie, key, direction, departure, routeText))
         for key, linie, direction, departure, typ, routeText in dmMonitor]

    logging.debug('Abfahrt von %s:' % curStop)
    [logging.debug('%s Linie %s (ID%s) - nach %s - Abfahrt: %d min - über: %s' %
           (typ, linie, key, direction, departure, routeText))
     for key, linie, direction, departure, typ, routeText in dmMonitor]


    return dmMonitor

def get_haltepunkt(name='Hauptbahnhof'):
    prefix = '900'
    if isinstance(name, int):
        return prefix + str(name)

    if name == 'Hauptbahnhof':
        return prefix+'1008'
    elif name == 'Römerplatz':
        return prefix+ '1360'
    elif name == 'Saarlandstraße':
        return prefix+ '1380'
    else:
        return None

def get_sessionID(name='Hauptbahnhof'):
    haltepunkt = get_haltepunkt(name)
    r = requests.get('https://www.ding.eu/ding3/XSLT_DM_REQUEST?sessionID=0&type_dm=stopID&name_dm='+haltepunkt+'&useRealtime=1&excludedMeans=0&excludedMeans=6&excludedMeans=10&outputFormat=XML')
    try:
        tree = etree.fromstring(r.content)
    except etree.XMLSyntaxError as e:
        print('Error %s occured while trying to get session ID: %s' %(e, r.content))
    return tree.get('sessionID')

def generateURL(haltepunkt='Saarlandstraße', limit=10, outputformat='XML'):
    # get sessionID, where the haltepunkt is set
    # then use this id in url
    sessID = get_sessionID(haltepunkt)

    url = 'https://www.ding.eu/ding3/XSLT_DM_REQUEST?useRealtime=1&sessionID=' + sessID + '&requestID=1&dmLineSelectionAll=1&limit=' + \
          str(limit) + '&outputFormat=' +outputformat
    # global DingSessions
    # DingSessions[haltepunkt]= {'isValid':True, 'sessionID':sessID, 'url':url}

    return {'isValid':True, 'sessionID':sessID, 'url':url}

def printETA(stop_name='Saarlandstraße', richtung='Science Park II'):
    abfahrtMonitor = generateURL(stop_name)
    abfahrtListe = parse_xml(abfahrtMonitor['url'])

    df = pd.DataFrame(abfahrtListe, columns=['ID', 'linie', 'richtung', 'abfahrt', 'typ', 'route'])
    df = df.loc[df['richtung']==richtung]
    print(df)

def getETA(stop_name='Saarlandstraße', richtung='Science Park II'):
    # global DingSessions
    # if stop_name not in DingSessions or not DingSessions[stop_name]['isValid']:
    #     abfahrtMonitor = generateURL(stop_name)
    # # else:
    #     abfahrtMonitor = DingSessions[stop_name]

    abfahrtMonitor = generateURL(stop_name)

    abfahrtListe = parse_xml(abfahrtMonitor['url'])

    if not abfahrtListe:
        return None # no estimated time of arrival

    df = pd.DataFrame(abfahrtListe, columns=['ID', 'linie', 'richtung', 'abfahrt', 'typ', 'route'])
    logging.debug('read dmMonitor into DataFrame:'+ df.to_string())
    df = df.loc[df['richtung']==richtung]
    logging.debug('filter for direction %s: %s' % (richtung, df.to_string()))

    # can be empty after filtering
    if df.empty:
        return None

    logging.debug('return: '+str(df.iloc[0][['abfahrt','ID']].to_dict()))
    return df.iloc[0][['abfahrt','ID']].to_dict()



# TODO: some bug with key
def trainIsComing():
    global watchingTrainID
    sld = getETA('Saarlandstraße')

    if not sld:
        print("Saarlandstraße: no ETA while checking for Coming")
    else:
        if  sld['abfahrt'] <= 1:
            watchingTrainID = sld['ID']
            print('train is coming, watching train ID '+ str(watchingTrainID))
            return True
        else:
            print('Saarlandstraße in %s min' % (sld['abfahrt'],))

    watchingTrainID = None
    return False

# TODO some bug with key
def trainHasArrived():
    global watchingTrainID
    rmp = getETA('Römerplatz')

    if not rmp:
        print("Römerplatz: no ETA while checking for Arrival")
    else:
        if rmp['ID'] != watchingTrainID:
            print('train has arrived: old ID %s -> %s' % (str(watchingTrainID), rmp['ID']))
            return True

    return False



def main():

    take_photo_every = 5
    check_departure_every = 5
    delay_saarlandstr_roemerplatz = 10

    while True:
        if trainIsComing():
            time.sleep(delay_saarlandstr_roemerplatz)
            while not trainHasArrived():
                takeAndSavePhoto()
                time.sleep(take_photo_every)
        time.sleep(check_departure_every)


    ipdb.set_trace()



if __name__ == '__main__':
    main()


