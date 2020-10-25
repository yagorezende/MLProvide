import os
import numpy as np
from scapy.all import rdpcap, wrpcap
from scipy.interpolate import UnivariateSpline
from matplotlib import pyplot as plt
import matplotlib


def N(n, digits=2):
    if len(str(n)) < digits:
        n = "0" + str(n)
    return n

if __name__ == '__main__':
    DIRNAME = 'C://Users/reine/Dropbox/datasets/netforager/netforager-pcaps/'
    clients = [f'client{N(i)}' for i in range(12, 15)]
    packets_to_use = []
    days = os.listdir(DIRNAME)

    pkt_all = []
    pkt_time = False
    max_len = 100000
    url = ''

    for client in clients:
        pkt_interval = []
        for day in days:
            uuids = os.listdir(DIRNAME + day)
            for uuid in uuids:
                try:
                    path = f"{DIRNAME}{day}/{uuid}/{client}/clientResults/"
                    files = os.listdir((path))
                    for f in files:
                        if f.count('pcap'):
                            packets = rdpcap(path + f)
                            for packet in packets:
                                if not pkt_time:
                                    pkt_time = packet.time
                                    continue
                                if float(abs(pkt_time - packet.time)) < 0.0005:
                                    packets_to_use.append(packet)
                                    pkt_interval.append(float(abs(pkt_time - packet.time)))
                                    pkt_all.append(float(abs(pkt_time - packet.time)))
                                pkt_time = packet.time
                    pkt_time = False
                    print(len(pkt_interval))
                    if len(pkt_interval) >= max_len:
                        break
                except:
                    pass
            if len(pkt_interval) >= max_len:
                break
        wrpcap(client + ".pcap", [])
        pkt_interval = [i*1000 for i in pkt_interval]
        plt.figure()
        scale = .2
        font = {'family': 'DejaVu Sans',
                # 'weight' : 'bold',
                'size': scale * 95, }
        matplotlib.rc('font', **font)
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)
        s = [a*1 for a in pkt_interval]
        print(s)
        n = len(pkt_interval)//10
        p, x = np.histogram(s, bins=n)  # bin it into n = N//10 bins
        x = x[:-1] + (x[1] - x[0]) / 2  # convert bin edges to centers
        f = UnivariateSpline(x, p, s=n)
        plt.plot(x, f(x))
        border = [0, 3]
        #print(border)
        #plt.xlim(border)
        plt.xlabel('Packet Interval [ms]')
        plt.ylabel('Ocurrence')
        plt.title = client
        plt.savefig(client + '.pdf')
        print("FEITO", client)

    plt.figure()
    s = [a * 1 for a in pkt_all]
    print(s)
    n = len(pkt_all) // 10
    p, x = np.histogram(s, bins=n)  # bin it into n = N//10 bins
    x = x[:-1] + (x[1] - x[0]) / 2  # convert bin edges to centers
    f = UnivariateSpline(x, p, s=n)
    plt.plot(x, f(x))
    border = [0, 3]
    # print(border)
    # plt.xlim(border)

    plt.xlabel = 'Intervalo entre pacotes'
    plt.ylabel = 'Incidência'
    plt.savefig('all.pdf')
    print("FEITO", client)




