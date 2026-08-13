


import os
import time
import numpy as np
import concurrent.futures
import tsync
import aiohttp
import run_gobannos as gob
import connect
import rw_data
import  asyncio
import socket
import platform
from datetime import datetime
import shutil
from time import perf_counter
from threading import Barrier
def move_csv_files(directory, new_rep):
    # Créer un répertoire pour les fichiers CSV

    csv_dir = os.path.join(directory, new_rep )
    os.makedirs(csv_dir, exist_ok=True)

    # Parcourir tous les fichiers du répertoire
    for filename in os.listdir("buffer"):
        if filename.lower().endswith(".csv"):
            src_path = os.path.join("buffer", filename)
            print(src_path)
            dest_path = os.path.join(csv_dir, filename)
            print(dest_path)
            shutil.move(src_path, dest_path)
            

    print(f"Tous les fichiers CSV ont été stocké dans : {csv_dir}")
def get_os():
    return platform.platform().split('-')[0]

def get_folder():
    ostype = platform.platform().split('-')[0]
    osname = socket.gethostname()
    if osname=='localhost':
        folder = '/storage/emulated/0/Documents/'
    elif ostype=='macOS':
        folder = 'Phonefleet/'
    elif ostype=='linux':
        folder= 'Phonefleet/'
    else:
        folder= 'Phonefleet/'
    return folder

def set_network():
    s = input('Type sub network number')
    network = int(s)
    return network

def set_phonelist():
    s = input('Type phonelist to adress :')
    lis = s.split(':')
    phonelist = []
    for i,l in enumerate(lis[:-1]):
        phonelist = phonelist+list(range(int(lis[i]),int(lis[i+1])+1))
    phonelist = list(set(phonelist))
    return phonelist

def get_filelist(network,s,display=True):
    phone = int(s.split(' ')[1])
    try:
        ip = connect.get_adress(phone,network=network)
        filelist = gob.get_file_list_V2(ip)

        if display:
            for i,filename in enumerate(filelist):
                print(i,filename)
        return filelist
    except Exception as e:
        print(f'error on phone {phone}: {e}')
        return []

def get_file(network,s):
    try:
        phone = int(s.split(' ')[1])
        num = int(s.split(' ')[2])
    except:
        print('argument not valid, specify phone and file number,')
        print('exemple : pull 5 16')
        return None
    s = f'ls {phone}'
    filelist = get_filelist(network,s)
    if len(filelist)==0:
        return None
    if num<len(filelist):
        filename = filelist[num]

        ip = connect.get_adress(phone,network=network)
        a = gob.get_file(ip,filename)
        
        data = a.decode('utf-8')
        
        save_file(filename,data,phone)

    else:
        print(f'Num {num} greater than the number of files')
        return None

def save_file(filename,data,phone):
    name = os.path.basename(filename)
    savefile = 'buffer/'+f'P{phone}_D{name}'

#    print(data)
    with open(savefile,'w') as f:
        f.write(data)


def save_last_file(network,phonelist):
    grandeur = input("Choisir une grandeur\n gyroscope\n magnetic_field\n gps\n accelerometer\n")
    num = int(input("quel fichier voulez vous telecharger ? \n pour le dernier 1, l'avant dernier 2 etc ..."))
    date = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) 
    for phone in phonelist:
        filelist = get_filelist(network,'a ' +str(phone),display= False)

        file_dict = {
        "gyroscope": [],
        "magnetic_field": [],
        "gps": [],
        "accelerometer": []
        }

        
        for file in filelist:
        # Vérifier le type de fichier et l'ajouter au bon endroit
            if "gyroscope" in file:
                file_dict["gyroscope"].append(file)
            elif "magnetic_field" in file:
                file_dict["magnetic_field"].append(file)
            elif "gps" in file:
                file_dict["gps"].append(file)
            elif "accelerometer" in file:
                file_dict["accelerometer"].append(file)
        
        filename = file_dict[grandeur][-num]
        ip = connect.get_adress(phone,network=network)
        a = gob.get_file(ip,filename)
                    
        data = a.decode('utf-8')
        name_dir = grandeur + date
        
        save_file(filename,data,phone)
    
    move_csv_files(f"../../../data_phone_fleet/{grandeur}",name_dir)

def save_all_last_file(network,phonelist):
    
    num = int(input("quel fichier voulez vous telecharger ? \n pour le dernier 1, l'avant dernier 2 etc ..."))
    #boucle sur les telephones 
    date = "date"
    for i,phone in enumerate(phonelist):

        filelist = get_filelist(network,'a ' +str(phone),display= False)

        file_dict = {
        "gyroscope": [],
        "magnetic_field": [],
        "gps": [],
        "accelerometer": []
        }

        
        for file in filelist:
        # Vérifier le type de fichier et l'ajouter au bon endroit
            if "gyroscope" in file:
                file_dict["gyroscope"].append(file)
            elif "magnetic_field" in file:
                file_dict["magnetic_field"].append(file)
            elif "gps" in file:
                file_dict["gps"].append(file)
            elif "accelerometer" in file:
                file_dict["accelerometer"].append(file)

        for grandeur in file_dict.keys():
            
            filename = file_dict[grandeur][-num]
            #on fixe la date avec le nom du premier fichier accelero
            if grandeur == "gyroscope" and i == 0:
                date = filename[3:20]
                
                
            ip = connect.get_adress(phone,network=network)
            #on recupere le  fichier avec gob.getfile
            a = asyncio.run(gob.get_file_V3(ip, filename))
                
            data = a.decode('utf-8')
            
            name_dir = f"{grandeur} {date}"
            
            path = f"../../../data_phone_fleet/{grandeur}/{name_dir}_ref"
            os.makedirs(path, exist_ok=True)
            with open(path + f"/P{phone}_{filename}",'w') as f:
                f.write(data)
            
            print(name_dir)


async def save_all_last_file_V2(network, phonelist):
    num = int(input(
        "Quel fichier voulez-vous télécharger ?\n"
        "Pour le dernier 1, l'avant-dernier 2, etc… "
    ))
    print("chargement des meta data")
    date = ""

    liste_url_fichier = []
    for i, phone in enumerate(phonelist):
        ip = connect.get_adress(phone, network=network)
        filelist = get_filelist(network, f"P {phone}", display=False)
        file_dict = {k: [f for f in filelist if k in f] 
                     for k in ("gyroscope", "magnetic_field", "gps", "accelerometer")}

        for j, grandeur in enumerate(file_dict.keys()):
            if grandeur == "gyroscope" and i == 0:
                date = file_dict[grandeur][-num][3:20]
            url = f"http://{ip}:8080/get-file/{file_dict[grandeur][-num]}"
            path = os.path.join(
                "../../../data_phone_fleet",
                grandeur,
                f"{grandeur}{date}",
                f"P{phone}_{file_dict[grandeur][-num]}"
            )
            liste_url_fichier.append((url, path))

    print("chargement des meta data terminé")

    connector = aiohttp.TCPConnector(limit=20, limit_per_host=1)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [gob.download_file(session, url, path) for url, path in liste_url_fichier]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                url, path = liste_url_fichier[idx]
                print(f"Erreur téléchargement {url} -> {path}: {result}")
    


def check_status(network,phonelist):
    for phone in phonelist:
        try:
            get_status(phone,network=network)
        except Exception as e:
            print(f"{phone} error {e}")

def get_status(phone,network=1):
    ip = connect.get_adress(phone,network=network)
    status = gob.get_status(ip)
    print(status)
    
def stop_phonelist(network,phonelist):
    for phone in phonelist:
        ip = connect.get_adress(phone,network=network)
        status = gob.get_status(ip)
        print(status)
        if not status==b'STOPPED':
            gob.individual_stop(ip)

def start_phonelist(network,phonelist):
    for phone in phonelist:
        ip = connect.get_adress(phone,network=network)
        status = gob.get_status(ip)
        print(status)
        gob.individual_start(ip)

def time_sync(network,phonelist,iter=5):
    savefolder = '../../../data_phone/t_sync'
    if not os.path.exists(savefolder):
        os.makedirs(savefolder)

    for i in range(iter):
        results={}
        for phone in phonelist:
            ip = connect.get_adress(phone,network=network)
            status = gob.get_status(ip)
            print(status)
            print(ip)

            if get_os()=='linux' or get_os()=='localhost':
                Dt = tsync.time_sync_ip(ip,n=100,timeout=0.1)
            else:
                import tsync_windows
                Dt = tsync_windows.time_sync_ip(ip,n=100,timeout=0.1)
            print(Dt)
            if Dt is not None:
                result = get_lag(Dt)
                results[phone]=result
        filename = savefolder+f'/tsync_{str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))}.txt'
        rw_data.writedict_csv(filename,results)


def get_lag(Dt):
    duration = Dt['duration']
    t0 = Dt['time']
    tmedian = np.median(duration)

    tmax = tmedian*1
    print(f'Median duration of UDP request : {np.round(tmedian*1000,decimals=3)} ms')

    indices = np.where(duration<tmax)[0]
    tlag1 = np.asarray(Dt[1])[indices]
    tlag2 = np.asarray(Dt[2])[indices]
    tlag3 = np.asarray(Dt[3])[indices]
    tlag = (tlag1+tlag3)/2
    Dt = np.median(tlag)

    results={}
    results['tlag'] = Dt
    results['dtmedian'] = tmedian
    results['tmin'] = np.min(tlag)
    results['tmax'] = np.max(tlag)
    results['tstd'] = np.std(tlag)
    results['n'] = len(duration)
    results['t0'] = t0
    return results
                
def choose(network,phonelist):
    print('chose action among : ')
    actions = ['network','phones','status','time','start','stop','save', 'save all','ls','pull','exit','ls options','pull options']
    descriptions = ['','','','','','','','','']
    for action,description in zip(actions,descriptions):
        print(action,description)
    s = input('')

    if s=='network':
        network = set_network()
        return s,network
    if s=='phones':
        phonelist = set_phonelist()
        return s,phonelist
    elif s=='status':
        print(f'Available phonelist : {phonelist}')
        check_status(network,phonelist)
    elif s=='time':
        time_sync(network,phonelist)
    elif s=='start':
        start_phonelist(network,phonelist)
    elif s=='stop':
        stop_phonelist(network,phonelist)
    elif s[:2]=='ls':
        get_filelist(network,phonelist,s)
    elif s[:4]=='pull':
        data = get_file(network,phonelist,s)
    elif s[:] ==  'save' : 
        save_last_file(network,phonelist)
    elif s[:] ==  'save all' : 
        asyncio.run(save_all_last_file_V2(network,phonelist))
        #save_all_last_file(network,phonelist)
    elif s=='exit':
        print("exit")
    else:
        print('command not known, do nothing')
    return s,None

def defaults():
    ostype = platform.platform().split('-')[0]
    osname = socket.gethostname()
    if osname=='localhost':
        phonelist = [1,2,3,4,5]
        network = 0
    elif ostype=='macOS':
        phonelist = [5]
        network = 2
    else:
        phonelist = range(30,39)
        network = 0
    return phonelist,network

def main():
    phonelist,network = defaults()

    s=''
    while not s=='exit':
        s,output = choose(network,phonelist)
        if s=='phones':
            phonelist=output
        elif s=='network':
            network = output
        print(phonelist)
        print(network)
    #action to code :
    #define phonelist (phones)
    #check connection (status)
    #timesync (time)
    #start acquisition (start)
    #

if __name__=='__main__':
    main()
