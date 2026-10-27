import subprocess
import phonefleet.server.data as dataphone
import numpy as np

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
    cmd  = [
        "scp",
        "-i", "/data/data/com.termux/files/home/.ssh/id_ed25519",  # Assurez-vous que ce chemin est correct
        filename,
        f"{USERNAME}@{IP_ADDRESS}:{SERVEUR_FOLDER}"
    ]
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