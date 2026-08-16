import glob
import subprocess
from pprint import pprint
from PIL import Image
import pytesseract
import phonefleet
import time
import datetime

global folder
folder = '/data/data/com.termux/files/home/storage/pictures/Screenshots'
global screen_count
global filelist
filelist = glob.glob(folder+'/*.png')
screen_count = len(filelist)

def check_screenshots():
        global screen_count
        global filelist
        filelist = glob.glob(folder+'/*.png')
        if len(filelist) > screen_count:
                print('New screenshot detected, parsing text ...')
                success = pairing_device()
                if success:
                        screen_count += 1
                        
def pairing_device():
#pprint(filelist)
        global filelist
        image_path = filelist[-1]
        print(image_path)

        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        lines = extracted_text.split('\n\n')
        text = [line.split('\n') for line in lines]

        psswd = None

        for t in text:
                print(t)
                if t[0]=='Pair with device':
                        print(t)
                        if len(t)>=3:
                                psswd = t[2]
                        else:
                                print('check parsing!')
                if t[0]=='IP address & Port':
                        ip,port=t[1].split(':')

        if psswd is None:
                print('no password detected')
                print(ip,port)
                out = subprocess.run(['adb','connect',ip+':'+port],text=True,capture_output=True)
        else:
                print(ip,port,psswd)
                out = subprocess.run(['adb','pair',ip+':'+port],text=True,capture_output=True,input=psswd)
        print(out.stdout)
        return True

if __name__=='__main__':
        while True:
                print(f"Check for new screenshot at {str(datetime.datetime.now())}")
                check_screenshots()
                time.sleep(10)
