while read line; do echo $line; done < routing_table.txt
echo $1
while read line; do id=`echo $line | awk -F ' ' '{print $1}'`; if [[ $id == $1 ]]; then num=`echo $line | awk -F ' ' '{print $2}'`; ip=`echo $line | awk -F ' ' '{print $3}'`; port=`echo $line | awk -F ' ' '{print $4}'`; fi; done < routing_table.txt
echo $num
echo $ip
ssh $num@$ip -p $port