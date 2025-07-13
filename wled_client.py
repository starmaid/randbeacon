import socket
import requests
import time

class LightStrip():
    def __init__(self,num_leds):
        self.num_leds = num_leds
        pass

    def powerOn(self):
        pass

    def powerOff(self):
        pass

    def setLights(self,light_arr):
        """
        Light array is a list of 3-tuples, RGB order
        """
        if len(light_arr) > self.num_leds:
            print(f'length of array {len(light_arr)} > length of current strip = {self.num_leds}')
            raise ValueError()
        if not isinstance(light_arr[0],tuple):
            print(f'you didnt pass tuples to the setLights')
            raise TypeError()
        if max(max(light_arr)) > 255:
            print(f'max value higher than 255')
            raise ValueError()
        if min(min(light_arr)) < 0:
            print(f'min value below 0')
            raise ValueError()
        pass


class WledLightStrip(LightStrip):
    def __init__(self, num_leds):
        super().__init__(num_leds)
        self.light_address = "10.0.0.105"
        self.light_baseurl = f"http://{self.light_address}"
        self.light_udp_port = 21324
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def powerOn(self):
        super().powerOn()
    
    def setLights(self, light_arr):
        super().setLights(light_arr)
        
        # This is apparently the magic to flatten tuples
        data = [2,5] + list(sum(light_arr,()))
        self.s.sendto(bytes(data), (self.light_address, self.light_udp_port))
        return

        
    
    def getLightState(self):
        r = requests.get(self.light_address + "/json")
        return(r.content)
    
    def sendUdp(self):
        while True:
            t = int(time.time() * 10000)
            index = t % 10
            data = [1,5,index,t%255,int(t/255)%255,int(t/255/255)%255]
            self.s.sendto(bytes(data), (self.light_address, self.light_udp_port))
            time.sleep(0.001)
    
    def sendUdp2(self):
        index = 0
        len = 400
        while True:
            data = [2,5] + [0] * 3 * len
            data[2+index*3:2+index*3+3] = [255,255,255]
            self.s.sendto(bytes(data), (self.light_address, self.light_udp_port))
            index += 1
            if index >= len:
                index = 0
            time.sleep(0.001)


if __name__ == "__main__":
    import random
    length = 100
    a = WledLightStrip(length)
    #print(a.getLightState())
    while True:
        a.setLights([(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for a in range(length)])
        time.sleep(0.01)