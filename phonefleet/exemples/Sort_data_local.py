

import phonefleet.server.data as dataphone
from pprint import pprint


# if no folder and no date are specified, the default folder is used and all files are searched
datas = dataphone.search()

print(datas.keys())
print(dataphone.display(datas))

keys = np.sort(datas.keys())

last = keys[-1]
#load all the data, may take a while !
datas[last] = dataphone.combine(datas[last])
print(datas[last]['data'].keys())