import os
import sys
import time
import traceback
import psutil

from ai.agent import Agent
from ai.reward_provider import RewardProvider
from configs import settings
from util import pomdp_mapper
from util.utils import FileHandler
from controller.ryu_controller import RyuController
from models.datacenter import DataCenter
from models.client import Client

RESULTS_PATH = settings.OUTPUT_PATH + "results/"
STRATEGY = settings.STRATEGY.split('_')[0]
SM = ""
TRAINED = ""
if settings.EXPLORATION == "softmax":
    SM = "-sm"
if settings.Q_TABLE_INDEX:
    TRAINED = "-trained"
TRAIN_OUTPUT_PATH = f"{RESULTS_PATH}results-dataset_{STRATEGY}/{STRATEGY}-compare-cquit-w-{SM}{TRAINED}"


class FuzzyTester:
    """
    Run this script to execute all the tests
    """

    def __init__(self, turns=20):
        # define paramethers
        self.turns = turns
        self.fuzzy_times = [2, 5]  # this should be
        self.file: FileHandler = None
        self.controller = RyuController()

    def run(self):
        """
        This code will execute a loop of @turns times
        """
        # loop through fuzzy steps.
        for step in self.fuzzy_times:
            for count in range(0, self.turns):
                self.file = FileHandler(f'{TRAIN_OUTPUT_PATH}-{step}-{count}.txt', 'r')
                if os.path.isfile(self.file.file_path):
                    self.file.open().read().close()
                    if len(self.file.content.splitlines()) > 99:
                        print(f"{self.__class__.__name__} run: File line counter bigger then 99")
                        continue
                print(f"{self.__class__.__name__} run: Filename: {self.file.file_path}")
                print(count,
                      "TAKE ########################################################################")
                self._execute(step)
            exit()

    def _execute(self, step: int):
        ## Initilizing variables
        max_turns = settings.LOOP
        cpus = []  # no idea what it is
        differ = pomdp_mapper.NetProcDiff()
        clients = []
        turns = 0  # i think this t is for step
        # Get datacenter tenants
        try:
            # tenants counter
            client_count = self.controller.api.client_count()
        except Exception as e:
            print("RYU DOWN")
            # Ignoring this, cuz we are not using SSH here
            # write_ryu_status(False)
            sys.exit()

        datacenter = DataCenter(cap=settings.MAX_SERVER_LOAD)
        self.controller.api.datacenter = datacenter
        print("CLIENT COUNT: ", client_count)

        # Filling clients lists
        # I think this loop
        for i in range(client_count):
            # Maybe this is not necessary, cuz this is just for testing cpu usage
            clients.append(Client(i + 2, settings.CLIENT1_BW + i * settings.BW_STEP, self.controller))
        rp = RewardProvider(settings.SERVER_IP, clients, self.controller, pomdp=settings.POMDP)

        try:
            rp.enabled = True
            if settings.PARALLEL:
                rp.parallel_start()
            print("START REWARD PROVIDER")
            # [BEGIN OF WHILE 1]
            error = False
            errors = 0
            # Check if all the executions has taken place
            # or
            while turns < max_turns and errors != len(rp.clients) and not error:
                turns += 1  # update counter
                # Dont know what it is
                # I think this line is to register CPU, memory and Datacenter occupation
                usage = (psutil.cpu_percent(), psutil.virtual_memory().percent, rp.datacenter.load)
                cpus.append(usage)
                # This will dump into a file this records
                differ.dump_diff(*usage)
                # TODO: Check if this is necessary
                time.sleep(step)
                try:
                    rp.step()
                except Exception as e:
                    error = True
                    print("DEU ERRO NO STEP")
                    traceback.print_exc()
                errors = 0  # reset errors count
                for client in rp.clients:
                    if client.error:
                        errors += 1
            # [END OF WHILE 1]
            # [BEGIN OF SAVE STATUS]
            for c in rp.clients:
                c.agent.dump_q_table()
            # copy tmp file to persistent file
            data_file = FileHandler(settings.MAIN_FILE, "r").open()
            data_file.copy_file(self.file.file_path)
            data_file.close()
            data_file.mode = "w+"
            data_file.open()
            # reset tmp file (write blank)
            data_file.content = ""
            data_file.write().close()
            # Turn off reward provider
            rp.enabled = False
            for thread in rp.threads:
                thread.join()
                print("TERMINARAM AS THREADS!!!")
            # [END OF SAVE STATUS]

        except Exception as e:
            traceback.print_exc()
            print(cpus)


if __name__ == "__main__":
    FuzzyTester(turns=5).run()
