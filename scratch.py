from matplotlib import pyplot as plt
import matplotlib
import time
import numpy as np
from models import settings
from time import sleep
import scipy.stats
from pprint import pprint
import matplotlib
import math
from pprint import pprint

filename = "results-dataset_sarsa/sarsa-compare-aw--sm<REPETITION>-<STATES>-1--teststates.txt"
x, y = [], []
clients = {}
for i in range(5, 50):
    x.append(i+1)
    total = []
    for j in range(10):
        try:
            f = filename\
                .replace("<REPETITION>", str(j))\
                .replace("<STATES>", str(i))

            cnt = open(f, 'r').read()
            for line in cnt.splitlines()[2:]:
                values = line.split(',')
                for k in range(len(values)-1):
                    total.append(float(values[k])/(settings.CLIENT1_BW + settings.BW_STEP*k))
                    if k not in clients:
                        clients[k] = []
                    clients[k].append(float(values[k]))
        except:
            pass
    y.append(np.median(total))

#plt.plot(x, y)
#plt.show()
for k in clients:
    clients[k] = np.mean(clients[k])

ret = {}
for i, j in zip(x, y):
    ret[i] = j
pprint(ret)
pprint(clients)

