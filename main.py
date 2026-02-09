import time
import colorsys
import math
import logging
import json
from datetime import datetime

from randomness import randomness, sleepUntilMinute, sleepUntilSecond
from lights.lights import WledLightStrip, PrintTestLightStrip

# set up logging
logging.getLogger("asyncio").setLevel(logging.ERROR)
logfilename = str(datetime.now())[0:10] + '.log'
logging.basicConfig(filename=logfilename, format='%(asctime)s %(levelname)s %(message)s', level=logging.WARNING)

def indexWithWrap():
    pass

def makeBitString(input_int):
    return([str((input_int >> x) & 1) for x in range(int(math.log2(input_int)))])

def multiplyTuple(tup,scalar):
    return(tuple(int(scalar*x) for x in tup))

def print_index_with_cursor(strip_arr, index, color, cursor_color, strip_len):
    strip_arr[index%strip_len] = color 
    strip_arr[(index+1)%strip_len] = cursor_color
    strip_arr[(index+2)%strip_len] = cursor_color
    strip_arr[(index+3)%strip_len] = multiplyTuple(strip_arr[(index+3)%strip_len],0.8)
    strip_arr[(index+4)%strip_len] = multiplyTuple(strip_arr[(index+4)%strip_len],0.7)
    strip_arr[(index+5)%strip_len] = multiplyTuple(strip_arr[(index+5)%strip_len],0.6)
    strip_arr[(index+6)%strip_len] = multiplyTuple(strip_arr[(index+6)%strip_len],0.5)

if __name__ == "__main__":
    # Try to load the config file
    try:
        with open("./config.json","r") as f:
            config = json.load(f)
    except Exception as e:
        logging.error('Error loading config file: ' + str(e))
        logging.error('Stopping Program')
        raise e
    
    try:
        strip_len = config.get("strip_len")
        lights_addr = config.get("lights_addr")
        network_addr = config.get("network_addr")
    except Exception as e:
        logging.error('Error parsing config file: ' + str(e))
        logging.error('Stopping Program')
        raise e
    
    strip_arr = [(0,0,0)]*strip_len

    lights = WledLightStrip(strip_len, lights_addr)
    
    # loop until we get a connection...
    while True:
        r = lights.getLightState()
        if r is None:
            logging.error(f"Couldn't reach WLED light strip at {lights_addr}:")
            time.sleep(10)
        else:
            break
    
    #lights = PrintTestLightStrip(strip_len)
    beacon = randomness(network_addr=network_addr)

    beacon.startProcess()
    time.sleep(1)

    

    current_index = 0

    while True:
        # first lets get the status to try and jumpstart lost connections
        if lights.getLightState() is None:
            logging.warning("Failed to get light state")

        # first print the minute really fast
        minute_bitstring = makeBitString(int(time.time()/60))
        
        num_time_bits = 12 #len(minute_bitstring)

        for i in range(num_time_bits):
            print_index_with_cursor(strip_arr, current_index, (255,255,255) if minute_bitstring[i] == '1' else (0,0,0), (255,255,255), strip_len)
            lights.setLights(strip_arr)
            current_index += 1
            time.sleep(1 / num_time_bits)

        # lets just get one and play it
        v = beacon.getPulse()
        #print(v)

        i = 0
        while True:
            # if the minute just advanced, skip the rest and start the next print
            if int(time.time()/60) != (int((time.time()-59)/60) + 1):
                break
            
            # grab next byte
            try:
                c = v[i]
                
                # convert to color
                saturation = 255
                value = 159 | ((c >> 6) << 5)
                hue = (c & 63) << 2
                rgb = colorsys.hsv_to_rgb(hue/255, saturation/255, value/255)
                color = multiplyTuple(rgb,255)
                
                cursor_color = (255,255,255) #white
            except IndexError:
                color = (100,100,100) # grey
                cursor_color = (255,0,0) # red
                
            i += 1
            print_index_with_cursor(strip_arr, current_index, color, cursor_color, strip_len)
            
            lights.setLights(strip_arr)
            current_index += 1
            sleepUntilSecond()
            #time.sleep(59/64) # play full string in 59 seconds

    pass

