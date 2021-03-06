import json
from os import path
import shutil
import pandas as pd
import requests
from get_ip import get_ip
from dbmodel import Services

def load_services():
    # f = open(path.join('static/data/ports.json'))
    services = Services.query.all()
    columns = Services.__table__.columns
    final_list = {}
    for i in services:
        final_list[i.name] = [i.id, i.name, i.port]
    return final_list

available_services = {}

#TODO Add Plex, Kodi, SMB and FTP Shares
def check_local_services(db):

    ip = get_ip()
    services = load_services()
    r = None

    #PNCmdr
    available_services['PNCmdr'] = [str('http://'+ip+':'+services['PNCmdr'][2])]
    #Emby
    try:
        r = None
        r = requests.get(str('http://'+ip+':'+services['emby'][2])).text
    except:
        pass
    
    if not r is None and r.find('emby'):
        # return 'user Registered'
        available_services['emby'] = [str('http://'+ip+':'+services['emby'][2])]

    #Temp Monitor api
    try:
        r = None
        r = requests.get(str('http://'+ip+':'+services['temp_monitor_api'][2])).text
    except:
        pass
        
    if not r is None and not r.find('temp_monitor_api') == -1 :
        
        available_services['temp_monitor_api'] = [str('http://'+ip+':'+services['temp_monitor_api'][2])]
    #Temp Monitor webui
    try:
        r = None
        r = requests.get(str('http://'+ip+':'+services['temp_monitor'][2])).text
    except:
        pass
    
    if not r is None and r.find('temp_monitor') :
        available_services['temp_monitor'] = [str('http://'+ip+':'+services['temp_monitor'][2])]

    with open('available_services.json', 'w') as json_file:
        json.dump(available_services, json_file)   
    
    return available_services

#TODO Test network Scan    
def check_network_machines(db):
    
    ip = get_ip()
    services = load_services()

    all_services = check_local_services(db)
    ip = ip.split('.')
    for i in range(1,256):
        if i == int(ip[-1]):
            continue
        try:
            r = requests.get('http://'+ip[0]+'.'+ip[1]+'.'+ip[2]+'.'+str(i)+':2357/services')
            if r.status_code == 200:
                new_services = json.loads(r.text)
                for i in new_services:
                    if i in all_services:
                        for j in new_services[i]:
                            all_services[i].append(j)
                    else:
                        all_services[i] = []
                        for j in new_services[i]:
                            all_services[i].append(j)
        except:
            continue
    with open('all_available_services.json', 'w') as json_file:
        json.dump(all_services, json_file)    
    return all_services

