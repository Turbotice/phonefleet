
import csv
import os

def write_csv(filename,data):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        print(f"Creating folder {folder}")
        os.makedirs(folder)
    with open(filename, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|')
        for d in data:
            spamwriter.writerow(d)    

def writedict_csv(filename,data,symbol='#'):
    with open(filename, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|')#, quoting=csv.QUOTE_MINIMAL)

        keys = list(data.keys())
        print(keys)
        header = [symbol]+list(data[keys[0]].keys())
        spamwriter.writerow(header)
        for key in data.keys():
            row = [key]+[data[key][k] for k in data[key].keys()]
            spamwriter.writerow(row)


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
