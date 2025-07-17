import time
import colorsys
import math

from randomness import randomness, sleepUntilMinute
from lights.lights import WledLightStrip, PrintTestLightStrip

def indexWithWrap():
    pass

def makeBitString(input_int):
    return([str((input_int >> x) & 1) for x in range(int(math.log2(input_int)))])

def multiplyTuple(tup,scalar):
    return(tuple(int(scalar*x) for x in tup))

if __name__ == "__main__":
    strip_len = 71
    strip_arr = [(0,0,0)]*strip_len

    lights = WledLightStrip(strip_len)
    #lights = PrintTestLightStrip(strip_len)
    beacon = randomness()

    beacon.startProcess()
    time.sleep(1)

    

    current_index = 0

    while True:
        # first print the minute really fast
        minute_bitstring = makeBitString(int(time.time()/60))

        for i in range(10):
            strip_arr[current_index%strip_len] = (255,255,255) if minute_bitstring[i] == '1' else (0,0,0)
            lights.setLights(strip_arr)
            current_index += 1
            time.sleep(0.1)

        # lets just get one and play it
        v = beacon.getPulse()
        print(v)

        for i,c in enumerate(v):
            saturation = 255
            value = 159 | ((c >> 6) << 5)
            hue = (c & 63) << 2

            rgb = colorsys.hsv_to_rgb(hue/255, saturation/255, value/255)

            color = multiplyTuple(rgb,255)

            strip_arr[current_index%strip_len] = color 
            strip_arr[(current_index+1)%strip_len] = (255,255,255)
            strip_arr[(current_index+2)%strip_len] = (255,255,255)
            strip_arr[(current_index+3)%strip_len] = multiplyTuple(strip_arr[(current_index+3)%strip_len],0.8)
            strip_arr[(current_index+4)%strip_len] = multiplyTuple(strip_arr[(current_index+4)%strip_len],0.7)
            strip_arr[(current_index+5)%strip_len] = multiplyTuple(strip_arr[(current_index+5)%strip_len],0.6)
            strip_arr[(current_index+6)%strip_len] = multiplyTuple(strip_arr[(current_index+6)%strip_len],0.5)
            
            lights.setLights(strip_arr)
            current_index += 1
            time.sleep(59/64)

    pass

