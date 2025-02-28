


import tsync
global network

folder = '/storage/emulated/0/Documents/Gobannos/'

import run_gobannos as gob
import connect


def set_network():
    s = input('Type sub network number')
    network = int(s)
    return network

def get_phonelist():
    s = input('Type phonelist to adress :')
    lis = s.split(':')
    phonelist = []
    for i,l in enumerate(lis[:-1]):
        phonelist = phonelist+list(range(int(lis[i]),int(lis[i+1])+1))
    phonelist = list(set(phonelist))
    return phonelist

def check_status(network,phonelist):
    for phone in phonelist:
        get_status(phone,network=network)

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

def time_sync():
    for phone in phonelist:
        ip = connect.get_adress(phone,network=network)
        status = gob.get_status(ip)
        print(status)
        Dt = tsync.time_sync_ip(ip,n=100,timeout=0.1)
        print(Dt)

        with open(filename,'w') as f:
            for key in Dt.keys():
                f.write(Dt[key])
        
def choose(network,phonelist):
    print('chose action among : ')
    actions = ['network','phones','status','time','start','stop','exit']
    descriptions = ['','','','','','','']
    for action,description in zip(actions,descriptions):
        print(action,description)
    s = input('')


    if s=='network':
        network = set_network()
        return s,network
    if s=='phones':
        phonelist = get_phonelist()
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
    elif s=='exit':
        print("exit")
    else:
        print('command not known, do nothing')
    return s,None

def main():
    phonelist = []
    network = 0
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
