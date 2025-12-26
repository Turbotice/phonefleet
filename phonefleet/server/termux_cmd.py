import subprocess
from pprint import pprint

def catch_output(out):
    lines = out.stdout.decode().split('\n')
    return lines

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
