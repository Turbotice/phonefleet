

import phonefleet.server.data as dataphone
from pprint import pprint
import numpy as np

# if no folder and no date are specified, the default folder is used and all files are searched
datas = dataphone.search()

print(dataphone.display(datas))
keys = np.sort(list(datas.keys()))
last = keys[-1]

data = datas[last]
sorted = {}
for filename in data['filelist']:
    dic = dataphone.parse_filename(filename)
    if not dic['num'] in sorted.keys():
        sorted[dic['num']] = {}
        sorted[dic['num']]['filelist'] = [filename]
    else:
        sorted[dic['num']]['filelist'].append(filename)

for num in sorted.keys():
    print(f"{num} : {len(sorted[num]['filelist'])}")
    #sorted[num]['data'] = dataphone.combine(sorted[num])

print(np.sort(list(sorted.keys())))