import numpy as np
import pylab as plt


def display_time_serie(data,var='a',coord='z'):
    fig,ax = plt.subplots(figsize=(10,5))

    ax.plot(data['t'+var],data[var+coord])

    plt.xlabel('$t$')
    plt.ylabel(f'${var}_{coord}$')

    plt.show()
    pass




def summary():
    #local_time, phone, number, variable, tag, A_wave, f, GPS_phone, GPS_Garmin, filename

    pass
