
#!usr
import argparse
import os
import ifcfg
from time import sleep


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inout", action='store_true')
    args = parser.parse_args()
    index = ""
    for i in list(ifcfg.interfaces().items()):
        if str(i[0]).count("-eth0") and str(i[0])[0] == 'h':
            index = str(i[0]).replace("-eth0", "").replace("h", "")

    if args.inout:
        while 1:
            cmd = f"tcpreplay -i h{index}-eth0 -l 80000 --mbps=100 /home/reiner/Mestrado/pcaps/client{index}.pcap"
            print(cmd)
            os.system(cmd)
            sleep(30)
    cmd = f"tcpreplay -i h{index}-eth0 -l 0 --mbps=100 /home/reiner/Mestrado/pcaps/client{index}.pcap"
    print(cmd)
    os.system(cmd)
