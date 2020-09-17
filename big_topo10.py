#!/usr/bin/python

from threading import Thread
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, UserSwitch
from mininet.cli import CLI
from mininet.link import Intf, TCULink
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.clean import cleanup
from time import sleep
import argparse, traceback

HOSTS = 4

class Project(Topo):
    def __init__(self):
        Topo.__init__(self)
        #hosts = dict()

        #for i in range(HOSTS):
        #    h = 'h' + str(i+1)
        #    s = 's' + str(i+1)
        #    hosts[h] = self.addHost(h)
        #    hosts[s] = self.addSwitch(s)
        #    self.addLink(h, s, cls=TCULink)
        #print(hosts)


        #for i in range(1, HOSTS):
        #    self.addLink(hosts['s' + str(i+1)], hosts['s1'], cls=TCULink)

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
        h10= self.addHost('h10')
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
        # links
        self.addLink(h2, s2, cls=TCULink)
        self.addLink(h3, s3, cls=TCULink)
        self.addLink(h4, s4, cls=TCULink)
        self.addLink(h5, s5, cls=TCULink)
        self.addLink(h6, s6, cls=TCULink)
        self.addLink(h7, s7, cls=TCULink)
        self.addLink(h8, s8, cls=TCULink)
        self.addLink(h9, s9, cls=TCULink)
        self.addLink(h10, s10, cls=TCULink)


def start_server(server):
    server.sendCmd('python3 server.py')


def start_client(client, index):
    client.sendCmd('tcpreplay -i h%s-eth0 -l --multiplier=100000 pcaps/client%s.pcap' % (index, index))
    #client.sendCmd('python3 iperf_infinite.py -u -b 100m')
    print(client.waiting)


if __name__ == '__main__':
    setLogLevel('info')

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manual", help="manual mininet", action="store_true")
    args = parser.parse_args()

    ryu = RemoteController('ame', ip='172.16.100.9', port=6633)

    try:
        all_set = False

        while not all_set:
            topo = Project()
            cleanup()
            net = Mininet(
                topo=topo,
                controller=ryu,
                switch=UserSwitch,
                autoSetMacs=True,
            )
            net.start()
            percentage = net.pingAll()
            response = net.waitConnected(3)
            if int(percentage) != 0:
                percentage = net.pingAll()
            print("------- CONECTADOS: ", response)
            if response or int(percentage) == 0:
                print ("------- PORCENTAGEM DE PING: ", response)
                all_set = True
            else:
                net.stop()
                cleanup()
                print('-------- PARANDO O RYU')
                ryu.stop()


        clients = []
        server = net.getNodeByName('h1')
        server.setMAC('00:00:00:00:00:01')

        if not args.manual:
            start_server(server)
            for i in range(1, HOSTS):
                start_client(
                    net.getNodeByName(
                        'h' + str(i+1)
                    ),
                    str(i+1)
                )


    except Exception as e:
        print("Houve um erro, stopando...", e)
        net.stop()

    try:
        while net.getNodeByName('h2').waiting:
            sleep(5)
            print('Running.')
    except:
        net.stop()

    if args.manual:
        CLI(net)

    cleanup()

    #CLI(net)
#
    #net.stop()

# Allows the file to be imported using `mn --custom <filename> --topo minimal`
topos = {
    'mytopo': Project
}

