import subprocess
import phonefleet.server.data as dataphone
import numpy as np
import phonefleet.network.whoami as whoami
import os

global LOCAL_FOLDER
LOCAL_FOLDER = '/data/data/com.termux/files/home/storage/downloads/Gobannos/'

#from LAITA computer
global SERVEUR_FOLDER
SERVEUR_FOLDER = '/Users/stephane/Documents/CASCADE26/Data/Buffer/Tests/'
global USERNAME
USERNAME = 'stephane'
global IP_ADDRESS
IP_ADDRESS = '172.30.0.5'

def command(filename):
    whoami_info = whoami.get_phone_info()
    print(f"Phone info: {whoami_info}")
    folder = f"{SERVEUR_FOLDER}{whoami_info['Name']}/" #also add date to the folder path
    filedest = '.'.join(os.path.basename(filename).split('.')[:-1])+ f'_{whoami_info['Name']}.csv' #remove the extension and name of the phone in the name of the files
    destination = f"{folder}{filedest}"
    cmd  = [
        "scp",
        "-i", "/data/data/com.termux/files/home/.ssh/id_ed25519",  # Assurez-vous que ce chemin est correct
        filename,
        f"{USERNAME}@{IP_ADDRESS}:{destination}"
    ]
    #if not os.path.exists(folder):
    #    print(f"Create folder {folder} on the server !")#    os.makedirs(folder)
    return cmd

def send_data(data):
    for filename in data['filelist']:
        try:
            #run a scp per filename, using the command function to build the command    
            result = subprocess.run(command(filename), check=True, capture_output=True, text=True)
            print("Fichiers copiés avec succès !")
        except subprocess.CalledProcessError as e:
            print(f"Erreur scp (Code {e.returncode}) : {e.stderr}")


if __name__ == "__main__":
    datas = dataphone.search()
    keys = np.sort(list(datas.keys()))
    last = keys[-1]
    data = datas[last]

    sorted = dataphone.sort_data(data)
    complete = dataphone.complete_data(sorted)

    num = complete[-1] 
    # load the data for the last complete set of files
    sorted[num].update(dataphone.combine(sorted[num]))
    print(sorted[num]['data'].keys())
    send_data(sorted[num])