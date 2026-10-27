

import phonefleet.server.data as dataphone
from pprint import pprint
import numpy as np

# if no folder and no date are specified, the default folder is used and all files are searched
datas = dataphone.search()

print(dataphone.display(datas))
keys = np.sort(list(datas.keys()))
last = keys[-1]
#load all the data from the last recording, may take a while !
print(datas[last]['filelist'])
#datas[last] = dataphone.combine(datas[last])
#print(datas[last]['data'].keys())