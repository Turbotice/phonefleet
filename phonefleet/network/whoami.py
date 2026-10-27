import numpy as np
import os
import csv

def read_csv(filename,delimiter=','):
    rows = []
    with open(filename,'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        for row in spamreader:
            rows.append(row)
    return rows

def csv2dict(table,headerindex=0,symbol='#'):
    data = {}
    if table[0][0]==symbol:
        keys = table[0][1:]
        print(keys)
        for tab in table[1:]:
            try:
                #try to convert to int the key
                tab[0]=int(tab[0])
            except:
                pass #do nothing
            #print(tab)
            data[tab[0]]={}
            for (t,key) in zip(tab[1:],keys):
                print(key)
                if len(t.split('.'))>2:
                    data[tab[0]][key]=t
                elif len(t.split('.'))==2: 
                    data[tab[0]][key]=float(t)
                else:
                    try:
                        data[tab[0]][key]=int(t)
                    except:
                        data[tab[0]][key]=str(t)
    else:
        header = table[headerindex]
        data = {}
        for key in header:
            data[key]=[]
        for i in range(headerindex+1,len(table)):
            for j,key in enumerate(header):
                data[key].append(table[i][j])
    return data



fileinfo = "/data/data/com.termux/files/home/Phone.info"

if os.path.exists(fileinfo):
	raw = read_csv(fileinfo,delimiter='\t')
	info = csv2dict(raw)
	if 'Name' in info.keys():
		print(info['Name'][0])
	else:
		print("Identifier not found")
else:
	print("No Phone.info file found, please create it")
