from .ryuapi import RyuApi
from .agent import Agent, Bcolors, Mlog
import time
from . import settings
import math
from .datacenter import DC

class Client:
    def __init__(self, id, bw, dc, states=settings.STATES, bs=True):
        self.id = id
        self.bw = bw
        self.nbw = bw
        self.new_nbw = bw
        self.dc = dc
        self.dpid = id
        self.rapi = RyuApi(_dc=self.dc)
        if bs:
            self.bootstrap()
            self.agent = Agent(self, dc, states=states)
        self.nbw_bw = 1
        self.nbw_rate = 1
        self.bytes = 0
        self.old_bytes = 0
        self.enabled = True
        self.old_time = time.time()
        self.now_speed = 0
        self.error = False

    def __str__(self):
        return f"CLIENT:{self.id}"

    def bootstrap(self):

        # install flow
        self.rapi.add_flow(self.dpid, self.id, self.id)

        # install meter
        #self.rapi.add_meter(self.dpid, self.id, int(self.bw / 1000))

        rate = self.bw/1000
        self.rapi.add_meter(self.dpid, self.id, rate)

        #self.set_rate(2*self.bw/1000)
        self.set_rate(rate)

    def get_rate(self, raw=False):
        if raw:
            return self.rapi.get_meter(self.dpid, self.id)
        return int(self.rapi.get_meter(self.dpid, self.id))

    def set_rate(self, rate):
        self.rapi.change_meter(self.dpid, self.id, rate)

    def port_stats(self):
        return self.rapi.get_port_stats(self.id, port_no=1)

    def speed(self):
        new_time = time.time()
        print("getting speed")
        new_value = self.port_stats()
        speed = (new_value - self.old_bytes) / (new_time - self.old_time)
        self.now_speed = speed * 8
        print(
            "PORT STATS",
            self.id,
            new_value,
            self.old_bytes ,
            #(new_value - self.old_bytes),
            #new_time - self.old_time,
            #speed,
            #speed * 8,
            self.now_speed
        )
        self.old_time = new_time
        self.old_bytes = new_value


        return speed*8

    def get_nbw(self):
        if self.enabled:
            return self.nbw
        else:
            return 0

    def get_gain1(self):
        try:
            return 7*abs(self.new_nbw - self.bw) / self.nbw_bw
        except ZeroDivisionError:
            return 1

    def get_gain2(self):
        try:
            return abs(self.new_nbw - self.get_rate()) / self.nbw_rate
        except ZeroDivisionError:
            return 1

    def set_bytes(self, bytes):
        self.bytes = bytes


    def update(self):
        self.nbw = self.new_nbw
        self.nbw_rate = abs(self.nbw - self.get_rate())
        self.nbw_bw = abs(self.nbw - self.bw)

    def sum_rate(self, num):
        if num > 0:
            num_str = Bcolors.change(Bcolors.OKBLUE, num)
        else:
            num_str = Bcolors.change(Bcolors.FAIL, num)

        Mlog.DEBUG('INCREASE BY: ', num_str)
        new_rate = int(self.get_rate()) + num
        #print(num, self.get_rate(), new_rate, self.bw)
        #if new_rate * 1000 >= self.bw:
        self.rapi.change_meter(self.dpid, self.id, new_rate)

    def set_nbw(self, nbw):
        self.new_nbw = int(nbw)

    def step(self, rp):
        clients = rp.clients
        rate = self.get_rate()
        self.rate = rate
        if math.isnan(rate):
            exit()
        print(f"CLIENT {self.id}:" + Bcolors.WARNING + f"{rate}" + Bcolors.ENDC)
        getattr(self.agent, settings.STRATEGY)(clients)


if __name__ == "__main__":
    DC = DC(cap=settings.MAX_SERVER_LOAD)
    c = Client(2, 50000, bs=False)
    print(c.get_rate())
