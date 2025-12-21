import requests
import json
import time
from multiprocessing import Process, Value, Array
from ctypes import Structure, c_bool
import logging

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger('charset_normalizer').setLevel(logging.ERROR)

nist_url = "https://beacon.nist.gov/beacon/2.0/pulse/last"
randomness_str_len = 128

# force ipv4 because i was having issues
#requests.packages.urllib3.util.connection.HAS_IPV6 = False

def sleepUntilMinute():
    start_time = time.time()
    next_minute = (int(time.time()/60) + 1 ) * 60
    wait_time = next_minute - start_time
    
    wait_time = max(0, wait_time - 2) # wake up early
    time.sleep(wait_time)

def sleepUntilSecond():
    start_time = time.time()
    next_second = int(time.time()) + 1
    wait_time = next_second - start_time
    
    wait_time = max(0, wait_time + 0.01) # wake up slightly late to garuntee we are on the next second
    time.sleep(wait_time)

def session_for_src_addr(addr: str) -> requests.Session:
    """
    Create `Session` which will bind to the specified local address
    rather than auto-selecting it.
    """
    session = requests.Session()
    for prefix in ('http://', 'https://'):
        session.get_adapter(prefix).init_poolmanager(
            # those are default values from HTTPAdapter's constructor
            connections=requests.adapters.DEFAULT_POOLSIZE,
            maxsize=requests.adapters.DEFAULT_POOLSIZE,
            # This should be a tuple of (address, port). Port 0 means auto-selection.
            source_address=(addr, 0),
        )
    return session


class randomness():
    def __init__(self, network_addr=None):
        self.shr_str = Array('c', randomness_str_len)
        self.shr_data = Value(recProcData)
        self.shr_data.command = True
        self.network_addr = network_addr
        pass

    def startProcess(self):
        p = childproc(self.shr_data, self.shr_str, {"network_addr": self.network_addr})
        self.bgenworkerproc = Process(target=p.loop, args=(), daemon=True)
        self.bgenworkerproc.start()
    
    def stopProcess(self):
        self.shr_data.command = False

    def getPulse(self):
        # return the bytearray of the pulse

        # remember, the beacon gives us a 128-char long string
        # that is ACTUALLY just writing out 0-F hex as 128 regular characters
        # so we have to turn it into a 64-bit long bytestring
        ba = bytearray.fromhex(self.shr_str.value.decode())

        return(ba)
    

class recProcData(Structure):
    _fields_ = [
        ("status", c_bool),
        ("command", c_bool)
    ]

class childproc():
    def __init__(self, shr_data, shr_str, config):
        self.shr_data = shr_data
        self.shr_str = shr_str
        self.network_addr = config["network_addr"]
        pass

    def loop(self):
        # set up values
        self.shr_data.status = True
        
        if self.network_addr is not None:
            logging.info(f"Using user-specified network interface {self.network_addr}")
            net_session = session_for_src_addr(self.network_addr)
        else:
            net_session = requests.Session() # use default session


        while True:
            if self.shr_data.command == False:
                break
            try:
                r = net_session.get(nist_url, timeout=5)
            except Exception as e:
                logging.error(f"Couldn't reach NIST: {e}")
                time.sleep(2)
                sleepUntilMinute()
                continue
                
            try:
                data = json.loads(r.content.decode())
            except json.decoder.JSONDecodeError:
                logging.error(f"JSON decode error, data was {r.content}")
                sleepUntilMinute()
                continue
            value = data['pulse']['outputValue']
            self.shr_str.value = bytes(value, 'ascii')
            #print(value)
            sleepUntilMinute()
        
        self.shr.status = False


if __name__ == "__main__":
    a = randomness()
    a.startProcess()
    while True:
        print(a.getPulse())
        time.sleep(2)
