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
import argparse



class Project(Topo):
    def __init__(self):
        Topo.__init__(self)

        # hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        #Intf('eth2', node=s1)

        # links
        self.addLink(h1, s1, cls=TCULink)
        self.addLink(s2, s1, cls=TCULink)
        self.addLink(s3, s1, cls=TCULink)
        self.addLink(s4, s1, cls=TCULink)

        # links
        self.addLink(h2, s2, cls=TCULink)
        self.addLink(h3, s3, cls=TCULink)
        self.addLink(h4, s4, cls=TCULink)


def start_server(server):
    server.sendCmd('python3 server.py')

def start_client(client):
    client.sendCmd('python3 iperf_infinite.py -u -b 100m')
    print(client.waiting)



if __name__ == '__main__':
    setLogLevel('info')
    cleanup()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manual", help="manual mininet", action="store_true")
    args = parser.parse_args()
    topo = Project()
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='172.16.100.9', port=6633),
        switch=UserSwitch,
        autoSetMacs=True,
    )
    net.start()
    try:
        print("variando...")
        clients = []
        server = net.getNodeByName('h1')
        server.setMAC('00:00:00:00:00:01')
        clients.append(net.getNodeByName('h2'))
        clients.append(net.getNodeByName('h3'))
        clients.append(net.getNodeByName('h4'))
        if not args.manual:
            start_server(server)
            for client in clients:
                start_client(client)
    except Exception as e:
        print("Houve um erro, stopando...", str(e))
        net.stop()

    try:
        while server.waiting:
            sleep(5)
            print('Running.')
    except:
        net.stop()

    if args.manual:
        CLI(net)


    #CLI(net)
#
    #net.stop()

# Allows the file to be imported using `mn --custom <filename> --topo minimal`
topos = {
    'mytopo': Project
}

