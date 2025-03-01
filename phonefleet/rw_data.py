
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
