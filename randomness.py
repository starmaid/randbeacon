import requests
import json
import time
from multiprocessing import Process, Value, Array
from ctypes import Structure, c_bool


nist_url = "https://beacon.nist.gov/beacon/2.0/pulse/last"
randomness_str_len = 128

# force ipv4 because i was having issues
requests.packages.urllib3.util.connection.HAS_IPV6 = False

class randomness():
    def __init__(self):
        self.shr_str = Array('c', randomness_str_len)
        self.shr_data = Value(recProcData)
        self.shr_data.command = True
        pass

    def startProcess(self):
        p = childproc(self.shr_data, self.shr_str)
        self.bgenworkerproc = Process(target=p.loop, args=(), daemon=True)
        self.bgenworkerproc.start()
    
    def stopProcess(self):
        self.shr_data.command = False

    def getPulse(self):
        return(self.shr_str.value.decode())
    

class recProcData(Structure):
    _fields_ = [
        ("status", c_bool),
        ("command", c_bool)
    ]

class childproc():
    def __init__(self, shr_data, shr_str):
        self.shr_data = shr_data
        self.shr_str = shr_str
        pass

    def loop(self):
        # set up values
        self.shr_data.status = True

        while True:
            if self.shr_data.command == False:
                break
            r = requests.get(nist_url, timeout=5)
            data = json.loads(r.content.decode())
            value = data['pulse']['outputValue']
            self.shr_str.value = bytes(value, 'ascii')
            #print(value)
            time.sleep(5)
        
        self.shr.status = False


if __name__ == "__main__":
    a = randomness()
    a.startProcess()
    while True:
        print(a.getPulse())
        time.sleep(2)
