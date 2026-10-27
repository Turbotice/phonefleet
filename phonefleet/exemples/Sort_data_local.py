

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

nums = np.sort(list(sorted.keys()))
complete = []
for num in nums:
    print(f"{num} : {len(sorted[num]['filelist'])}")
    #sorted[num]['data'] = dataphone.combine(sorted[num]['filelist'])
    if len(sorted[num]['filelist'])>=4:
        complete.append(num)

num = complete[-1] 
# load the data for the last complete set of files
sorted[num]['data'] = dataphone.combine(sorted[num]['filelist'])
print(sorted[num]['data'].keys())