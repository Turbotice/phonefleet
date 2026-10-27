mkdir ~/log
date >> ~/log/sensors_log.txt
name=date
date "+%H:%M:%S.%N" >> ~/log/sensors_log_$1.txt
termux-sensor -s "lsm6dsv_0 Accelerometer Non-wakeup","ak0991x_0 Magnetometer Non-wakeup", "lsm6dsv_0 Gyroscope Non-wakeup","bmp5 Pressure Sensor Non-wakeup" -d 100 -n 500 >> ~/log/sensors_log_$1.txt
