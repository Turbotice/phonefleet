date >> ~/log/sensors_log.txt
date "+%H:%M:%S.%N" >> ~/log/sensors_log.txt
termux-sensor -s linear_acceleration,mmc56,Rotation -d 100 -n 500 >> ~/log/sensors_log_260815.txt