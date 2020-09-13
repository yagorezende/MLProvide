import numpy as np
from models import settings
import json
f = open("cpu-network1.txt", "r")

file = f.read().replace("\x00", "")
f.close()

p=[]
b=[]
for line in file.splitlines()[1::]:
    if line != "0,0,0" and line:
        p.append(float(line.split(',')[0]))
        b.append(float(line.split(',')[1]))

max_p = max(p)
min_p = min(p)


layers = 60
MAP = dict()
try:
    r = open("cpu-network-map.json", "r")
    content = r.read()
    r.close()
except:
    content = ""

if content:
    MAP = json.loads(content)
else:
    for i in range(layers):
        upper = (100*(i+1)/layers)
        lower = (100*i/layers)
        values = []
        for j in range(len(p)):
            if p[j] < upper and p[j] >= lower:
                values.append(b[j])
        if values:
            mean = np.mean(values)
        elif lower > min_p:
            mean = 92274
        else:
            mean = 0
        if lower not in MAP:
            MAP[lower] = dict()
        MAP[lower][upper] = mean/5.2

def mirror(v, real=False):
    for lower in MAP:
        if v >= float(lower):
            for upper in MAP[lower]:
                if v <= float(upper):
                    val = MAP[lower][upper]
                    if real:
                        MAP[lower][upper] = (0.5*MAP[lower][upper] + 0.5*real)
                        #print('MAP ATUALIZED', lower, upper)
                        #print(MAP[lower])
                        st = json.dumps(MAP)
                        if st.replace(' ',''):
                            w = open("cpu-network-map.json", "w+")
                            w.write(json.dumps(MAP))
                            w.close()
                    return val


class NetProcDiff:

    def __init__(self):
        self.net = 0
        self.proc = 0
        self.mem = 0

    def process(self, proc):
        if not self.proc:
            self.proc = proc
            return 0
        else:
            diff = self.proc - proc
            self.proc = proc
            return self.net_diff(diff)

    def dump_diff(self, proc, mem, net):
        w = open("cpu-network.txt", "a+")
        w.write(f'\n{proc},{mem},{net}')
        w.close()

        if not self.proc or not self.net:
            self.proc = proc
            self.mem = mem
            self.net = net
            proc_diff = 0
            net_diff = 0
            mem_diff = 0
        else:
            proc_diff = self.proc - proc
            net_diff = self.net - net
            mem_diff = self.mem - mem

        self.proc = proc
        self.mem = mem
        self.net = net
        diff = f'{proc_diff}, {mem_diff}, {net_diff}'
        w = open("cpu-network-map-diff.txt", "a+")
        w.write('\n' + diff)
        w.close()
        return self.net_diff(proc_diff)


    def net_diff(self, proc_diff):
        pass
















