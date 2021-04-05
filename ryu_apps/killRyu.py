from mininet.net import Mininet
from mininet.node import Controller, RemoteController, UserSwitch
from mininet.clean import cleanup

"""
This script kills local Ryu execution
"""

SERVER_IP = 'localhost'
ryu = RemoteController('ame', ip=SERVER_IP, port=6633)
net = Mininet(controller=ryu)
net.start()
net.stop()
cleanup()
ryu.stop()
