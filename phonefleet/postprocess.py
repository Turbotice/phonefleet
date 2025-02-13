import numpy as np
import glob
import data as dataphone


import icewave.phone.analyse as analyse
import icewave.tools.rw_data as rw
import icewave.field.time as timest
import icewave.field.multi_instruments as multi
import os


def get_phonelist(date):
    folder = dataphone.savefolder(date)
    folders = glob.glob(folder+'*/')

    print(len(folders))
    print(folders[0])

    phonelist=[]
    for f in folders:
        try:
            phone = int(f.split('/')[-2])
            phonelist.append(phone)
        except:
            print(f+str(', not a phone number'))
    print(phonelist)

    return phonelist,folders

def get_ref_time(phone,date):
    folder = dataphone.savefolder(date)
    timeref_files = glob.glob(folder+'Tsync/*')
    print(timeref_files)
    tref = None
    for filename in timeref_files:
        synctable = rw.read_csv(filename,delimiter=',')
        synctable = rw.csv2dict(synctable)

        for key in synctable:
            select,i = key.split('_')
            select = int(select)
            if select==phone:
                tref = synctable[key]['tlag']
                break
        if tref is not None:
            break
    if tref is None:
        print(f'No sync file for {phone}')
    return tref


def summary(filename,phone,date,var='a',coord='z',dt=1/50,tmin=20):
    dic = dataphone.load_data(filename)
    #local_time, phone, number, variable, tag, A_moy_wave, A_std_wave, f, GPS_phone, GPS_Garmin, filename
    
    
    r = {}
    tref = get_ref_time(phone,date)
    t0 = dic['t'+var][0]+tref
    t0 = timest.today_time([t0])[0]
    r['date'] = date
    r['local_time'] = timest.display_time([t0])[0]
    r['phone']=phone
    r['num']=filename.split('-')[-3]


    r['var']=var
    y = dic[var+coord]
    y = y-np.mean(y)

    t = dic['t'+var]
    t = t-t[0]

    y_high,y_wave,y_trend,err = analyse.filtering(y,fc=0.01,flow=0.0001)
    f = interp.interp1d(t,y_wave)
    ti = np.arange(tmin,np.max(t),dt)
    yi = f(ti)
    f,TFmoy,fmax,Amax = analyse.time_spectrum(ti,yi,nt=int(len(yi)/10),flim=100)


    ratio = np.std(y_wave)/np.std(y)

    sigma = np.round(np.std(y),decimals=5)
    if Amax>0.005 and Amax<0.2:
        r['tag']='wave'
    elif sigma>0.2:
        r['tag']='not set up'
    else:
        r['tag']='noise'

    moy = np.round(np.mean(y_wave),decimals=5)
    sigma = np.round(np.std(y_wave),decimals=5)
    r['A_wave']=sigma
    return r

    
if __name__=='__main__':
    date = '0204'
    phonelist,folders = get_phonelist(date)

    for (phone,f) in zip(phonelist,folders):
        filelist = glob.glob(f+'*accelerometer*')
        #filelist2 = glob.glob(f+'accelerometer*')
        #filelist = set(filelist1 + filelist2)

        R={}
        for i,filename in enumerate(filelist):
            print(filename)
            r = summary(filename,phone,date)
            r['filename']=os.path.basename(filename)

            if i==0:
                for key in r.keys():
                    R[key]=[r[key]]
            else:
                for key in r.keys():
                    R[key].append(r[key])

        folder = dataphone.savefolder(date)
        filesave=folder+f'Summary/{phone}.csv'
        if not os.path.isdir(os.path.dirname(filesave)):
            os.makedirs(os.path.dirname(filesave))
        rw.write_csv(filesave,R)