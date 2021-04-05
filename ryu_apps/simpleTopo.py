"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def network():
    "Create custom topo."

    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/16')

    info('*** Adding controllers\n')
    c1 = net.addController(name='c1',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           protocol='tcp',
                           port=6653)

    info('*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch, protocols='OpenFlow13')

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.11', mac='00:00:00:00:00:01', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.12', mac='00:00:00:00:00:02', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.13', mac='00:00:00:00:00:03', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.14', mac='00:00:00:00:00:04', defaultRoute=None)

    info('*** Add links\n')
    # Link entre switches e hosts
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    # Link entre switches
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s1, s4)
    net.addLink(s2, s3)
    net.addLink(s2, s4)
    net.addLink(s3, s4)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        info(controller)
        controller.start()

    info('*** Starting switches\n')
    net.get('s1').start([c1])
    net.get('s2').start([c1])
    net.get('s3').start([c1])
    net.get('s4').start([c1])

    info('*** Post configure switches and hosts\n')

    # h1.cmd('pwd')
    h1.cmd('tcpreplay -i h1-eth0 -l 0 --mbps=100 datasets/pcaps/client1.pcap')
    h2.cmd('tcpreplay -i h2-eth0 -l 0 --mbps=100 datasets/pcaps/client2.pcap')
    h3.cmd('tcpreplay -i h3-eth0 -l 0 --mbps=100 datasets/pcaps/client3.pcap')
    h4.cmd('tcpreplay -i h4-eth0 -l 0 --mbps=100 datasets/pcaps/client4.pcap')
    # h2.cmd("tcpreplay -i h2-eth0 -K --loop 50000 goose_test.pcap &")
    # h1.cmd("wireshark -i h1-eth0 -Y arp &")
    # h2.cmd("wireshark -i h2-eth0 -Y arp &")
    # h3.cmd("wireshark -i h3-eth0 -Y arp &")
    # h4.cmd("wireshark -i h4-eth0 -Y arp &")

    CLI(net)
    net.stop()

# topos = {'mytopo': (lambda: MyTopo())}
if __name__ == '__main__':
    setLogLevel( 'info' )
    network()