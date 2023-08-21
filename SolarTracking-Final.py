import pandas as pd
import numpy as np
import datetime
from datetime import *
import time
import RPi.GPIO as GPIO
import spidev


# setting up SPI for ADC
spi_ch = 0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

def read_adc(adc_ch, vref = 3.3):

    # Make sure ADC channel is 0 or 1
    if adc_ch != 0:
        adc_ch = 1

    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + adc_ch) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    return adc

in_pin = 14     # if set to HIGH, this pin goes in    
out_pin = 15    # if set to HIGH, this pin goes out

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(in_pin, GPIO.OUT, initial=GPIO.LOW)#Motor Driver
GPIO.setup(out_pin, GPIO.OUT, initial=GPIO.LOW)#Motor Driver

def actuator_in():                      # retracts actuator, increases ADC
    GPIO.output(in_pin, GPIO.LOW)
    GPIO.output(out_pin, GPIO.HIGH)

def actuator_out():                     # extends actuator, decreases ADC
    GPIO.output(in_pin, GPIO.HIGH)
    GPIO.output(out_pin, GPIO.LOW)

def actuator_STOP():                     # actuator STOP
    GPIO.output(in_pin, GPIO.LOW)
    GPIO.output(out_pin, GPIO.LOW)
    
filename = 'adc_by_time.csv'
adc_by_time = pd.read_csv(filename)
adc_by_time = adc_by_time.drop(columns='Unnamed: 0')


# today_midnight = datetime.combine(date.today(), datetime.min.time())
now = datetime.strptime(str(datetime.now()),"%Y-%m-%d %H:%M:%S.%f")
month = int(now.strftime("%m"))
time_striffed = now.strftime("%H:%M:%S")
time_stripped = datetime.strptime(time_striffed,"%H:%M:%S")

adj = timedelta(days=0,hours=0,minutes=10,seconds=0,microseconds=0)

month_df = adc_by_time.loc[adc_by_time['Month'] == month]

difference = 10*60*60   #time in seconds between movements


while True:
    start_time = time.time()                                         # start stopwatch
    
    check = True
    n=0
    while check:
        new_df = month_df.loc[month_df['Time'] == time_striffed]     # find df to find time row, i will fix this line @chris
        if n > 0:
            last_desired_adc = desired_adc
        else:
            last_desired_adc = -1000
        desired_adc = int(new_df.to_numpy()[0][3])                   # find desired adc based on time
        current_adc = read_adc(0)                                    # find current adc value from channel 0
        print("/ncurrent adc:", current_adc)                         # print it to check
        print("desired adc:", desired_adc)

        if last_desired_adc != desired_adc:                              # ensures actuator has to move
            if desired_adc >= current_adc:                               # check if desired adc is greater than current
                check1 = True
                while check1:                                            # while check = true
                    actuator_in()                                        # turn on actuator to retract
    #                 print("retracting")
                    current_adc = read_adc(0)
                    print(current_adc)
                    if desired_adc <= current_adc:                       # when it reaches the desired value
                        print("stop1")
                        actuator_STOP()
                        check1 = False                                   # check = false, stop retracting

            elif desired_adc < current_adc:
                check2 = True
                while check2:
                    actuator_out()
    #                 print("expanding")
                    current_adc = read_adc(0)
                    print(current_adc)
                    if desired_adc >= current_adc:
                        print("stop2")
                        actuator_STOP()
                        check2 = False

        time_striffed = time_stripped.strftime("%H:%M:%S")           # convert to strif time
        time_stripped += adj                                         # add 10 minutes to time
#         time.sleep(difference)
        n+=1
        check = False
#         if n>143:
#             check = False                                           # stop running after 24 hrs

    end_time = time.time()                                            # stop stopwatch
    elapsed_time = end_time - start_time
    time.sleep(difference - elapsed_time)
    