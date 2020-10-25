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
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h


def plot_states():
    filename = "results-dataset_sarsa/sarsa-compare-aw--sm<REPETITION>-<STATES>-1--teststates.txt"
    x, y, e = [], [], []
    z, ze = [], []
    clients = {}
    for i in settings.TEST_STATES_RANGE:
        x.append(i+1)
        total = []
        med_z = []
        for j in range(10):
            try:
                f = filename\
                    .replace("<REPETITION>", str(j))\
                    .replace("<STATES>", str(i))

                cnt = open(f, 'r').read()
                for line in cnt.splitlines()[2:]:
                    values = line.split(',')
                    med_z.append(float(values[-1]))
                    for k in range(len(values)-1):
                        total.append(float(values[k])/(settings.CLIENT1_BW + settings.BW_STEP*k))

                        if k not in clients:
                            clients[k] = []
                        clients[k].append(float(values[k]))
            except:
                pass

        med_z = [1 - (np.mean(med_z_frac)/settings.MAX_SERVER_LOAD) for med_z_frac in med_z]
        z.append(np.mean(med_z))
        ze.append(mean_confidence_interval(med_z))

        y.append(np.mean(total))
        e.append(mean_confidence_interval(total))
    y = [100*yi for yi in y]
    e = [100*ye for ye in e]
    z = [100*ye for ye in z]
    ze = [100*ye for ye in ze]
    scale = .2
    font = {'family': 'DejaVu Sans',
            # 'weight' : 'bold',
            'size': scale * 105, }
    matplotlib.rc('font', **font)
    #fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)
#
    #plt.xlabel('Number of States')
    #plt.ylabel('SLA mean Fitness [%]')
    #plt.savefig("pdf/states_justify.pdf")
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)
    plt.errorbar(x, z, yerr=ze)
    plt.xlabel('Number of States')
    plt.ylabel('Cloud idleness [%]')
    plt.savefig("pdf/states_idleness.pdf")
    #plt.show()
    for k in clients:
        clients[k] = np.mean(clients[k])

if __name__ == "__main__":
    plot_states()
#ret = {}
#for i, j in zip(x, y):
#    ret[i] = j
#pprint(ret)
#pprint(clients)

