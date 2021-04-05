import paramiko
# from .ryuapi import RyuApi
import time
from controller.ryu_controller import RyuController
from configs import settings
from models.datacenter import DataCenter
from util import pomdp_mapper
import psutil
from threading import Thread
import traceback


class RewardProvider:
    def __init__(self, ip, clients, controller: RyuController, pomdp=False, filename=settings.MAIN_FILE):
        self.SERVER_IP = ip
        self.clients = clients
        self.current_bytes = 0
        self.current_time = time.time()
        self.api = controller.api
        self.datacenter: DataCenter = controller.api.datacenter
        self.filename = filename
        self.flush_data()
        self.pomdp = pomdp
        self.real_server_load = 0
        self.t = 0
        self.ref_dc_load = 0
        self.enabled = True

    def flush_data(self):
        f = open(self.filename, "w")
        f.close()

    def dump_data(self):
        f = open(self.filename, "a")
        server_load = self.datacenter.load
        #mean_rate = 0
        #for client in self.clients:
        #    mean_rate += client.get_rate()
        #mean_rate = mean_rate/len(self.clients)
        #dump_string = f"{server_load},{mean_rate*1000}"

        dump_string = ','.join([str(self.get_client(i+2).now_speed) for i in range(len(self.clients))]) + f",{self.real_server_load}"
        # print(dump_string + f"|| {self.get_client(2).get_rate()},{self.get_client(3).get_rate()},{self.get_client(4).get_rate()}")
        f.write(dump_string + "\n")
        f.close()

    def get_conn(self):
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname=self.SERVER_IP, username="root", password="ubuntu")
        self.conn = conn

    def check_conn(self):
        if not getattr(self, "conn", False):
            return self.get_conn()
        if self.conn.get_transport() is not None:
            if self.conn.get_transport().is_active():
                return True
        return self.get_conn()

    def check_nbw(self):
        speeds = 0
        #print("CLIENTS:", self.clients)
        for client in self.clients:
            if not client.c:
                client.c = 0
            #print("begin client")
            speed = client.speed()
            print(self.__class__.__name__, "CLIENT",client.id, int(speed), client.get_rate(), client.enabled)

            if speed < 700:

                client.c += 1
                if client.c >=2:
                    client.enabled = False
            else:
                client.c = 0
                client.enabled = True
            #print("speed")
            client.set_nbw(speed)
            speeds += speed
            #print(speed, client.nbw)
            # self.update_client_load(client)
        if not settings.POMDP:
            self.datacenter.load = speeds
        else:
            if self.t % settings.CORRECTION_RATE == 0:
                self.datacenter.load = pomdp_mapper.mirror(float(psutil.cpu_percent()), speeds)
            else:
                self.datacenter.load = pomdp_mapper.mirror(float(psutil.cpu_percent()))
        self.real_server_load = speeds
        #print("Done check nbw")

    def get_client(self, id):
        for c in self.clients:
            if str(c.id) == str(id):
                return c

    def update_server_load(self):
        try:
            old_time = self.current_time
            old_bytes = self.current_bytes
            self.current_bytes = self.api.get_port_stats()
            if old_bytes != 0:
                self.datacenter.load = int(((self.current_bytes - old_bytes) * 8) / (time.time() - old_time))
        except:
            print("HTTP ERROR")

    def update_client_load(self, client):
        try:
            old_time = self.current_time
            old_bytes = client.bytes
            current_bytes = self.api.get_port_stats(port_no=client.id)
            nbw = int(((current_bytes - old_bytes) * 8) / (time.time() - old_time))
            if old_bytes != 0:
                client.set_nbw(nbw)
            client.set_bytes(current_bytes)
            print(f"{client.id}-{nbw/1000} kbps")

        except Exception as e:
            print("HTTP ERROR", e)

    def check_client(self):
        self.check_conn()
        stdin, stdout, stderr = self.conn.exec_command('cat /tmp/test.txt')
        try:
            report = stdout.read().decode('utf-8')
            for line in report.splitlines():
                if line:
                    client_id, enabled = line.split("=")[0].replace("CLIENT", ""), line.split("=")[1]
                    client = self.get_client(int(client_id))
                    if int(enabled):
                        if not client.enabled:
                            self.get_client(int(client_id)).enabled = True
                            print("CLIENT", client_id, "enabled")
                    else:
                        if client.enabled:
                            self.get_client(int(client_id)).enabled = False
                            client.set_nbw(0)
                            print("CLIENT", client_id, "disabled")
        except Exception as e:
            print("EXCEPTION> ", e)
            pass

    def step(self):
        self.t += 1
        self.check_nbw()
        #self.check_client()
        if not settings.PARALLEL:
            for client in self.clients:
                if client.enabled:
                    client.step(self)
        self.current_time = time.time()
        self.dump_data()

    @staticmethod
    def start(rp, client):
        while 1:
            if not rp.enabled:
                #print("SERVER NOT ENABLED")
                break
            time.sleep(1)
            #print("CLIENTE INDO")
            if client.enabled:
                try:
                    #print("CLIENTE DENTRO DO IF")
                    client.step(rp)
                    #print("Cliente passou do step")
                except Exception as e:
                    client.error = True
                    traceback.print_exc()
                    #print("ERROR in CLient ", client)
                    #print(e)
            else:
                #print("O CLIENTE TA DESABILITADO")
                break


    def parallel_start(self):
        self.threads = []
        for client in self.clients:
            t = Thread(target=RewardProvider.start, args=(self, client))
            self.threads.append(t)
            t.start()

        #while 1:
        #    time.sleep(1)
        #    self.t += 1
        #    self.check_nbw()
        #    self.current_time = time.time()
        #    self.dump_data()
