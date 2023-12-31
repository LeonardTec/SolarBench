button_pin = 23 # INPUT: normally low (internal pull down), will go high when pressed
button_LED = 19 # green button LED
LED_flood_light = 12 #Flood Light LEDS

led_pin_blue = 22             # OUTPUT: normally low, want to go high to turn on lights
led_pin_red = 4
led_pin_green = 27 

in_pin = 14     # if set to HIGH, actuator goes in    
out_pin = 15    # if set to HIGH, actuator goes out

import pandas as pd
import numpy as np
from datetime import *
import RPi.GPIO as GPIO
import spidev
from time import *
import csvLogging
import populateWebsite

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(led_pin_blue, GPIO.OUT, initial=GPIO.LOW) # LED
GPIO.setup(led_pin_green, GPIO.OUT, initial=GPIO.LOW) # LED
GPIO.setup(led_pin_red, GPIO.OUT, initial=GPIO.LOW) # LED
GPIO.setup(button_LED, GPIO.OUT, initial=GPIO.HIGH) # Green LED on button
GPIO.setup(LED_flood_light, GPIO.OUT, initial=GPIO.HIGH) # LED flood lights
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Button
GPIO.setup(in_pin, GPIO.OUT, initial=GPIO.LOW)#Motor Driver
GPIO.setup(out_pin, GPIO.OUT, initial=GPIO.LOW)#Motor Driver

LED_flood_state = 0 # state of Flood lights. 1 is on, 0 is off
Last_Time_Button_Pressed = 0 # debounce stuff
light_off_time = 0 # time to turn off flood lights
LED_time_out = 600 # how long Flood lights stay on in seconds
desired_adc = 0 # where actuator is supposed to be at the current time
actuator_idle = True

next_move_time = 0.0
last_adc = 0 # last postion instructed to move to
ten_min = 60*10

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

def button_callback(channel):
    global LED_flood_state
    global light_off_time
    global Last_Time_Button_Pressed
    if (time() - Last_Time_Button_Pressed) >= 0.3:
        if LED_flood_state == 0:
            LED_flood_state = 1
            light_off_time = (time() + LED_time_out) #turn off LEDs in 10 seconds
        else:
            LED_flood_state = 0
    Last_Time_Button_Pressed = time()

    
GPIO.add_event_detect(button_pin,GPIO.RISING,callback=button_callback)



def actuator_in():                      # retracts actuator, increases ADC
    GPIO.output(in_pin, GPIO.LOW)
    GPIO.output(out_pin, GPIO.HIGH)

def actuator_out():                     # extends actuator, decreases ADC
    GPIO.output(in_pin, GPIO.HIGH)
    GPIO.output(out_pin, GPIO.LOW)

def actuator_stop():                     # actuator STOP
    GPIO.output(in_pin, GPIO.LOW)
    GPIO.output(out_pin, GPIO.LOW)

filename = 'adc_by_time.csv'
adc_by_time = pd.read_csv(filename)
adc_by_time = adc_by_time.drop(columns='Unnamed: 0')

def timeround10(dt):                                               # function to round current time to nearest 10 min
    a, b = divmod(round(dt.minute, -1), 60)
    rounded_time = '%i:%02i' % ((dt.hour + a) % 24, b)
    rounded_time = datetime.strptime(rounded_time,"%H:%M")
    rounded_time = rounded_time.strftime("%H:%M:%S")
    return rounded_time

def get_adc():
    try:
        now = datetime.strptime(str(datetime.now()),"%Y-%m-%d %H:%M:%S.%f")
        month = int(now.strftime("%m"))
        time_striffed = now.strftime("%H:%M:%S")
        time_stripped = datetime.strptime(time_striffed,"%H:%M:%S")
        month_df = adc_by_time.loc[adc_by_time['Month'] == month]
        lookup_time = timeround10(time_stripped)                         # rounds to nearest 10 min
        new_df = month_df.loc[month_df['Time'] == lookup_time]
        desired_adc = int(new_df.to_numpy()[0][3])                       # find desired adc based on time
    except:
        desired_adc = 650
    return (desired_adc)


 
while (True):
    sleep(0.05)
    current_time = time()
    current_adc = read_adc(0) 
    desired_adc = get_adc() #int(input()) # replace with actual code from michelle
    current = (read_adc(1)-511)*0.066
    print(current_adc, "->", desired_adc, "current =", current )
    
    if GPIO.input(button_pin):
        GPIO.output(button_LED, GPIO.LOW)
    else:
        GPIO.output(button_LED, GPIO.HIGH)
        
    if LED_flood_state == 1:
        GPIO.output(led_pin_blue, GPIO.HIGH)
        GPIO.output(LED_flood_light, GPIO.LOW)
    elif LED_flood_state ==0:
        GPIO.output(led_pin_blue, GPIO.LOW)
        GPIO.output(LED_flood_light, GPIO.HIGH)
    
    if (light_off_time < current_time):
        LED_flood_state = 0;

## Pulls CSV Data every 10 min
        
      
      
## Control loop
    if current_adc < (desired_adc + 2) and current_adc > (desired_adc - 2): #desired_adc != last_adc
        actuator_idle = True
    elif current_adc > (desired_adc + 20) or current_adc < (desired_adc - 20): #desired_adc != last_adc
        actuator_idle = False
    

    if actuator_idle == False: #desired_adc != last_adc
        ##Need to move
        if (desired_adc > current_adc): # need to retract actuator
            actuator_in()
#             if (current_adc > desired_adc):
#                 last_adc = desired_adc
#                 actuator_stop()
        elif (desired_adc < current_adc): # need to extend actuator
            actuator_out()
#             if (current_adc < desired_adc):
#                 last_adc = desired_adc
#                 actuator_stop()
    else:
        actuator_stop()
    
    try:
        csvLogging.append("table.csv",read_adc(1), True)
    except:
        print("logging not working")
