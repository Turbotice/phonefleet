

import phonefleet.server.data as dataphone

# if no folder and no date are specified, the default folder is used and all files are searched
datas = dataphone.search()

for key in datas.keys():
    datas[key] = dataphone.combine(datas[key])

print(datas.keys())