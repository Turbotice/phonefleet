import subprocess
from pprint import pprint
import phonefleet.rw_data as rw
from datetime import datetime
import zoneinfo


def catch_output(out):
    lines = out.stdout.decode().split('\n')
    return lines

def get_apps_running():
    #names :
    dic = {}
    names =     {'gobannos':'fr.pmmh.gobannos','termux':'com.termux','zerotier':'com.zerotier.one', 'teamviewer':'com.teamviewer.quicksupport.addon.universal'}
    for name in names.keys():
        dic.update(is_app_running(name,names[name]))
    return dic

def is_app_running(name,name_id):
    dic = {}
    out = subprocess.run(['adb','shell','pidof',name_id],capture_output=True)
    lines = out.stdout.decode().split('\n')
    #if an id exist, app is running
    if len(lines)>1:
        dic[name]=True
    else:
        dic[name]=False
    return dic

def read_csv_gps(filename):
    raws = rw.read_csv(filename,delimiter=':')
    print(len(raws))
    d = {}
    for raw in raws:
        if raw[0][0]=='{' or raw[0][:2]==" '":
        #print('Attribute : '+raw[0][2:-1])
        #print(raw)
            key = raw[0][2:-1]
            parse = raw[1].split("'")
            if len(parse)>=2:
                k = parse[1]            
            #print(parse)
            else:
            #print(f'no value detected for {key}')
                continue
            if key=='time':
                elem = ':'.join(raw[2:])[:-2].split("'")[1]#.split(" ")[1]
            elif key=='id':
                elem = raw[2][:-2].split("'")[1]#.split(" ")[1]
            elif len(raw)>2:
                elem = raw[2].split(" ")[1]
            else:
                elem = None
            if not key in d.keys():
                d[key] = [{}]
            else:
                d[key].append({})
        else:
            k = raw[0].split("'")[1]
            elem = raw[1].split(" ")[1]
        #print(key,k,elem)
        d[key][-1][k]=elem
#        print(raw)
        #print('   '+raw[0])
    return d

def convert_time(date):
    # The original date string
    date_str = date
    # 1. Strip the weekday and 'CEST' for easier standard parsing
    # "Sat Aug 15 09:55:00 CEST 2026" -> "Aug 15 09:55:00 2026"
    clean_str = " ".join(date_str.split()[1:4] + [date_str.split()[-1]])
    # 2. Parse the cleaned string into a naive datetime object
    naive_dt = datetime.strptime(clean_str, "%b %d %H:%M:%S %Y")
    # 3. Attach the correct Central European Summer Time zone (UTC+2)
    # CEST is equivalent to the Europe/Paris or Europe/Berlin timezone in August
    localized_dt = naive_dt.replace(tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
    # 4. Convert to a Unix timestamp float
    timestamp_float = localized_dt.timestamp()
    return timestamp_float

def trajectory(dic,imin=0,imax=-1):
    m = {}
    m['latitude'] = []
    m['longitude'] = []
    m['t'] = []

    for gps,t in zip(dic['gps'][imin:imax],dic['time'][imin:imax]):
        lat = float(gps['latitude'][:-1])
        lon = float(gps['longitude'][:-1])
            
        #print(lat,lon)
        m['latitude'].append(lat)
        m['longitude'].append(lon)
        #t0 = convert_time(t['date'])#convert_time(t['date'])
        m['t'].append(t['date'])
    return m
        #plt.plot(lon,lat,color+'.')

def get_time():
    out = subprocess.run('date',capture_output=True)
    lines = catch_output(out)
    return {'date':lines[0]}

def get_whoami():
    out = subprocess.run('whoami',capture_output=True)
    lines = catch_output(out)
    return {'whoami':lines[0]}

def get_adb_status():
    out = subprocess.run(['adb','devices'],capture_output=True)
    lines = catch_output(out)
    results = lines[1:-2] #may depend on phone type ?? works on FP3
    dic = {}
    if len(results)==1:
        #print('Exactly one adb interface connected')
        dic['name'] = results[0].split('\t')[0]
        dic['status'] = results[0].split('\t')[1]
        return dic
    else:
        print(f'Number of devices connected : {len(results)}')
        print('Not implemented, do nothing')
        return None
    
def get_battery():
    out = subprocess.run('termux-battery-status',capture_output=True)
    lines = catch_output(out)
    dic = parse_battery_output(lines)
    return dic

def parse_battery_output(lines):
    outs = {line.split(': ')[0].split('"')[1]:line.split(': ')[1][:-1] for line in lines if ':' in line}
    for key in outs.keys():
        out = outs[key]
        try:
            outs[key]=int(out)
        except:
            try:
                outs[key]=float(out)
            except:
                try:
                    outs[key]=str(out.split('"')[1])
                except:
                    outs[key]=out
        #print(key,outs[key])
    return outs

def get_gps_position():
    out = subprocess.run('termux-location',capture_output=True)
    lines = catch_output(out)
    dic = parse_battery_output(lines)
    return dic

def get_sensors():
    out = subprocess.run(['termux-sensor','-s','linear_acceleration,mmc56,Rotation','-d','100'],capture_output=True)
    lines = catch_output(out)
    dic = parse_battery_output(lines)
    return dic    

    
def get_all_ips():
        out = subprocess.run('ifconfig',capture_output=True)
        lines = out.stdout.decode().split('\n')
        protocols = [line.split(':')[0] for line in lines if ':' in line]
        ips= [line.split('inet ')[1].split(' netmask')[0] for line in lines if 'inet ' in line]

        if len(ips)==len(protocols):
                res = {}
                for p,ip in zip(protocols,ips):
                        res[p]=ip
                return res
        else:
                print('parsing of ifconfig non valid, abort')
                return None
