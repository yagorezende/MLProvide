#!/usr/bin/python2

#
# Minimal example showing how to use MaxiNet
#

import time

from MaxiNet.Frontend import maxinet
#from MaxiNet.tools import FatTree
from mininet.topo import Topo, SingleSwitchTopo
from mininet.node import UserSwitch, OVSSwitch
from mininet.link import TCULink
import random

class DC(Topo):

    def __init__(self, **opts):
        Topo.__init__(self, **opts)

    def build(self):
        #h1 = self.addHost('h1', ip="10.0.0.1")
        #h2 = self.addHost('h2', ip="10.0.0.2")
        #s1 = self.addSwitch('s1', dpid='1')
        #h1s1 = self.addLink(h1, s1, cls=TCULink)
        #h2s1 = self.addLink(h2, s1, cls=TCULink)

        # hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        h9 = self.addHost('h9')
        h10 = self.addHost('h10')
        #
        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')
        s8 = self.addSwitch('s8')
        s9 = self.addSwitch('s9')
        s10 = self.addSwitch('s10')

        #
        # Intf('eth2', node=s1)
        #
        # links
        self.addLink(h1, s1, cls=TCULink)
        self.addLink(s2, s1, cls=TCULink)
        self.addLink(s3, s1, cls=TCULink)
        self.addLink(s4, s1, cls=TCULink)
        self.addLink(s5, s1, cls=TCULink)
        self.addLink(s6, s1, cls=TCULink)
        self.addLink(s7, s1, cls=TCULink)
        self.addLink(s8, s1, cls=TCULink)
        self.addLink(s9, s1, cls=TCULink)
        self.addLink(s10, s1, cls=TCULink)
        #
        # linkss
        self.addLink(h2, s2, cls=TCULink)
        self.addLink(h3, s3, cls=TCULink)
        self.addLink(h4, s4, cls=TCULink)
        self.addLink(h5 , s5 , cls=TCULink)
        self.addLink(h6 , s6 , cls=TCULink)
        self.addLink(h7 , s7 , cls=TCULink)
        self.addLink(h8 , s8 , cls=TCULink)
        self.addLink(h9 , s9 , cls=TCULink)
        self.addLink(h10, s10, cls=TCULink)

def start_server(server):
    server.sendCmd('python3 server.py')


def start_client(client, index):
    client.sendCmd('tcpreplay -i h%s-eth0 -l 0 --multiplier=100000 pcaps/client%s.pcap' % (index, index))
    #client.sendCmd('python3 iperf_infinite.py -u -b 100m')
    print(client.waiting)

if __name__ == '__main__':
    topo = DC()
    print "Done Topo"
    cluster = maxinet.Cluster()
    print "Done Cluster"

    exp = maxinet.Experiment(
        cluster,
        DC(),
        switch=UserSwitch
    )
    exp.setup()

    print "set up done"

    print "waiting 5 seconds for routing algorithms on the controller to converge"
    time.sleep(5)

    exp.CLI(locals(), globals())
    exp.stop()



#print exp.get_node("h1").cmd("ifconfig")  # call mininet cmd function of h1
#print exp.get_node("h4").cmd("ifconfig")
#print exp.get_node("h1").cmd("ping -c 5 10.0.0.4")
