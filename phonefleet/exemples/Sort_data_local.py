

import phonefleet.server.data as dataphone
from pprint import pprint
import numpy as np

# if no folder and no date are specified, the default folder is used and all files are searched
datas = dataphone.search()

print(dataphone.display(datas))
keys = np.sort(list(datas.keys()))
last = keys[-1]

data = datas[last]
sorted = dataphone.sort_data(data)
complete = dataphone.complete_data(sorted)

num = complete[-1] 
# load the data for the last complete set of files
sorted[num].update(dataphone.combine(sorted[num]))
print(sorted[num]['data'].keys())