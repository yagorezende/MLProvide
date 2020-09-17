from .datacenter import DC
import random
import numpy as np
from . import settings
from . import fls
import psutil
import time
from .utils import Bcolors, Mlog
import math
import functools
import json



class Agent(object):
    def __init__(self, client, dc, _range=settings.ACTIONS, max_percent=8, states=settings.STATES, q_table_index=settings.Q_TABLE_INDEX):
        """ Agente """
        "Nodes"
        self.client = client
        self.dc = dc

        "Max percent of max server load"
        self.max_percent = max_percent

        "File for dump data"
        self.file = f"client_{str(self.client.id)}.txt"
        f = open(self.file, "w+")
        f.write("")
        f.close()

        "Ambiente"
        self.ACTION_SPACE = len(self.action_map(_range=_range))
        self.OBSERVATION_SPACE = settings.STATES  # Increase or decrease
        self.old_dc_load = 0

        "Modelagem das recompensas"
        self.MAX_SERVER_LOAD = self.dc.cap  # Max msg/seg

        "Q-table"
        space = self.OBSERVATION_SPACE
        if settings.STRATEGY in ('fql_step', 'fsl_step'):
            "Caso seja usado FQL, o numero de estados usado precisa ser igual ao de regras"
            space = settings.FLS.RULE_SPACE
        self.reset_q_table()

        if q_table_index and settings.STRATEGY not in ['fuzzy_step']:
            self.q_table = self.fetch_q_table(index=q_table_index)
        else:
            self.q_table = np.random.rand(space, self.ACTION_SPACE)  # Creating the Q-table


        self.old_state = -1

        "Sistema de inferencia fuzzy"
        #self.bootstrap_fls()

        "Fuzzy Q Learning"
        self.fql_q_function = 0
        self.fql_v_function = 0

        "Parâmetros"
        self.ALPHA = settings.ALPHA  # A importancia da nova experiencia adquirida
        self.GAMMA = settings.GAMMA  # O peso das acoes futuras
        self.EPSILON = settings.EPSILON  # A Ganancia do agente
        self.TEMPERATURE = settings.TEMPERATURE  # A Temperatura do método de Boltzmann

        "Graficos"
        self.epochs = []
        self.server_loads = []
        self.legit_traffics = []

        "LOCK MODE"
        self.LOCK_MODE = False
        self.SLA_PROBLEM = 0

        self.first = True

    def reset_q_table(self):
        file = open(f'client{self.client.id}_q_table.txt', 'w+')
        file.write('')
        file.close()

    def dump_q_table(self, index):
        if not settings.Q_TABLE_INDEX:
            file = open(f'results-qtables/client{self.client.id}_q_table-{settings.STRATEGY}-{settings.EXPLORATION}-{index}', 'a+')
            #st = '\n'.join(['    '.join(['{:4}'.format(item) for item in row]) for row in self.q_table])

            try:
                file.write(str(self.q_table.tolist()) + '\n')
            except:
                pass
            file.close()

    def fetch_q_table(self, index):
        exploration = ""
        if settings.EXPLORATION == "softmax":
            exploration = "-softmax"

        file = open(
            f'results-qtables/client{self.client.id}_q_table-{settings.STRATEGY}{exploration}-{index}', 'r')
        content = file.read()
        file.close()
        qtable = json.loads(content.splitlines()[0])
        print(qtable)
        return qtable

    def action_map(self, _range=1):
        self.actions = set()
        for i in range(_range + 1):
            a = i*100/settings.ACTIONS
            Mlog.INFO("ACTION: ", a)
            self.actions.add(a)
            self.actions.add(-a)
        self.actions = tuple(self.actions)
        Mlog.INFO('THE ACTIONS: ', self.actions)
        return self.actions

    def get_reward(self, clients, old_action):
        """ recuperar a recompensa para uma mudança de estado """
        reward = 0
        gain1 = self.client.get_gain1()
        #gain2 = self.client.get_gain2()
        self.client.update()
        #print(self.dc.load, self.dc.cap, self.actions[self.old_action])
        if settings.STRATEGY in ('fql_step', 'fsl_step'):
            old_action = self.old_action
        else:
            old_action = self.actions[self.old_action]

        if self.dc.load >= self.dc.cap:
            Mlog.INFO("SERVER GREATER", self.dc.load, self.dc.cap)
            if old_action >= 0:
                reward = -3#*(self.dc.load/self.dc.cap)
                return reward
            else:
                reward = 1 #* (self.dc.load / self.dc.cap)
                return reward

        if self.client.nbw < 0.5*self.client.bw:
            Mlog.INFO('OLD ACTION', self.client.id, old_action)
            if old_action >= 0:
                reward = 0.7#*self.client.nbw/self.client.bw
            else:
                Mlog.INFO("NEGATIVE REWARD BY CLIENT UNDER SLA")
                reward = -4#*self.client.nbw/self.client.bw
                return reward

        if self.client.nbw < self.client.bw:
            if old_action >= 0:
                print()
                reward = 0.5 #* self.client.nbw / self.client.bw
                return reward
            else:
                Mlog.INFO("NEGATIVE REWARD BY CLIENT UNDER SLA 2")
                reward = -2 #* self.client.nbw / self.client.bw
                return reward

        #if self.SLA_PROBLEM:
            #return -0.7*self.client.nbw/self.client.bw
        return -0.7 * self.client.nbw / self.client.bw


        reward += gain1
        if gain1 < 1:
            return -reward
        return reward

    def dump_state(self, state):
        #print('QTDD ', self.OBSERVATION_SPACE)
        file = open(f'{settings.STATE_FILE}{settings.STATES}.txt', 'a+')
        file.write(f'{self.client.id}:{state}:{self.OBSERVATION_SPACE}\n')
        file.close()
        return state

    def get_current_state(self):
        if settings.STATE_TYPE == 'val':
            # OLD
            state = int(self.dc.load/(self.dc.cap/self.OBSERVATION_SPACE))
        elif settings.STATE_TYPE == 'diff':
            state = int(self.dc.load / (self.old_dc_load*self.dc.cap / self.OBSERVATION_SPACE))
            self.old_dc_load = self.dc.load
        elif settings.STATE_TYPE == 'fuzzy':
            cpu = psutil.cpu_percent()
            load = self.dc.load
            state = int(self.fls.get_state(cpu=psutil.cpu_percent(), bw=self.dc.load))
            Mlog.INFO('FUZZY INPUT: ' , cpu, load, state)
        if state > self.OBSERVATION_SPACE:
            return self.dump_state(self.OBSERVATION_SPACE)

        return self.dump_state(state)

    def do_action(self, action):
        increase_by = 0
        if self.actions[action] != 0:
            #percent = ((self.max_percent/100)*(self.dc.cap/1000))
            percent = 0.2
            increase_by = math.ceil(percent*(self.actions[action]/100)*self.client.rate)
        self.state = self.get_current_state()
        #print('doing')
        self.client.sum_rate(increase_by)
        self.state = self.get_current_state()
        self.old_state = self.state

    def do_fuzzy_action(self, value):
        increase_by = int((value/100)*0.3*settings.MAX_SERVER_LOAD/1000)
        Mlog.DEBUG("DO FUZZY ACTION, INCREASE BY =", increase_by)
        self.client.sum_rate(increase_by)

    def sample_action(self):
        """Toma uma decisão aleatoriamente (descobre)"""
        self.state = self.get_current_state()
        if self.state >= len(self.q_table):
            actions = [i for i in self.actions if i <= 0]
        elif self.state <= 1:
            actions = [i for i in self.actions if i >= 0]
        else:
            actions = self.actions
        chosen = random.choice(self.actions)
        return self.actions.index(chosen)

    def dump_data(self, *args):
        f = open(self.file, "a+")
        ex = ",".join([str(i) for i in args])
        data = f"{self.client.id},{self.dc.load},{self.client.get_rate()*1000},{ex}"
        #print(data)
        f.write(data + "\n")
        f.close()

    def choose_action(self):
        """Toma decisão embasada no que foi aprendido (Escolhe da Q-table)"""
        self.state = self.get_current_state()
        line = self.q_table[self.state - 1]
        Mlog.DEBUG([f"{i}:{line[i]}" for i in range(len(line))])

        if 0 in self.q_table[self.state - 1]:
            return self.sample_action()
        action = np.argmax(self.q_table[self.state - 1])
        if self.q_table[self.state - 1][action]:
            return action
        else:
            return self.sample_action()

    def force_down_action(self):
        #print(self.actions, min(self.actions))
        down_actions = [i for i in self.actions if i < 0]
        action = self.actions.index(random.choice(down_actions))
        #print(action, self.actions[action])
        return action

    def colored(self, number):
        if number < 0:
            ret = Bcolors.FAIL + str(number) + Bcolors.ENDC
        else:
            ret = Bcolors.OKBLUE + str(number) + Bcolors.ENDC
        return ret

    def softmax(self):
        """ Exploration/Exploitation Process """
        actions = self.q_table[self.get_current_state() -1]
        l = actions
        numerator = [math.exp(num / self.TEMPERATURE) for num in l]
        denominator = sum(numerator)
        prob = [num / denominator for num in numerator]
        probp = [0, prob[0]]
        for i in range(len(prob)):
            if i not in [0, len(prob) - 1]:
                probp.append(sum(prob[0:i + 1]))
        rand = random.random()
        for i in probp:
            if rand >= i:
                ret = probp.index(i)
                continue
            else:
                break
        return ret

    def eep(self):
        if random.uniform(0, 1) < self.EPSILON:
            action = self.sample_action()  # Explore action space
        else:
            action = self.choose_action()  # Exploit learned values
        return action


    def sarsa_step(self, clients):

        return self.q_step(clients)

    def q_step(self, clients):
        """O agente toma uma ação baseado no que aprendeu, com certa ganancia de apredizado, e verifica a efetividade de sua ultima decisão"""

        self.LOCK_MODE = False
        for client in clients:
            # self.client.nbw >= client.nbw and \
            if (client.nbw < client.bw and \
                    client.id != self.client.id and \
                    client.bw > self.client.bw and \
                    client.nbw < client.bw and self.client.nbw > self.client.bw and
                    client.enabled) or self.dc.load > self.dc.cap :
                if settings.LOCK_MODE:
                    self.LOCK_MODE = True
                self.SLA_PROBLEM = True

        if self.LOCK_MODE:
            pass
            #print(self.client.id, "LOCK MODE")

        # Escolha da ação baseada na taxa
        if not self.LOCK_MODE:
            self.ALPHA = 0.1
            # numpy.random.standard_cauchy()
            action = getattr(self, settings.EXPLORATION)()
        else:
            self.ALPHA = settings.LOCK_ALPHA
            action = self.force_down_action()

        #print(self.actions[action])

        if not hasattr(self, 'old_action'):
            self.old_action = action

        if self.old_state > 0:
            # Atualiza a Q-Table -> Aprendizado
            reward = self.get_reward(clients, self.old_action)
            next_state = self.get_current_state()
            old_value = self.q_table[self.old_state-1][self.old_action]

            if settings.STRATEGY.count("q_step"):
                next_max = np.argmax(self.q_table[next_state-1])
                new_value = (1 - self.ALPHA) * old_value + self.ALPHA * (reward + self.GAMMA * next_max)
            else:
                sarsa_value = self.q_table[next_state - 1][action]
                new_value = (1 - self.ALPHA) * old_value + self.ALPHA * (reward + self.GAMMA * sarsa_value)
            self.q_table[self.old_state - 1][self.old_action] = new_value
        else:
            reward = self.get_reward(clients, self.old_action)
            #print(self.client.id, "reward =", reward, self.old_state)]


        c_reward = self.colored(reward)
        c_action = self.colored(self.actions[self.old_action])
        dc_load_cap = self.colored(self.dc.load/self.dc.cap)

        print(
            f'POMDP={settings.POMDP}, '
            f'DC-LOAD/CAP={dc_load_cap}, '
            f'CLIENT={self.client.id}, '
            f'NOW-BW={self.client.nbw}, '
            f'BW={self.client.bw}, '
            f'LOCK-MODE={self.LOCK_MODE}, '
            f'LIMIT={self.client.get_rate()}, '
            f'reward={c_reward}, '
            f'ACTION={c_action}')

        self.old_action = action
        self.old_state = self.get_current_state()
        self.dump_data(reward)

        # tomar a ação vetorial
        self.do_action(action)

        #self.dump_q_table()

    def get_fuzzy_variables(self, clients):
        total_clients = len(clients)
        clients_using = 0
        clients_not_using = 0

        for client in clients:
            if client.nbw < client.bw and client.id != self.client.id:
                clients_using += 1
            else:
                clients_not_using += 1

        others_below = (clients_using - clients_not_using) * 100 / total_clients
        serverload = 100 * self.dc.load / self.dc.cap
        client_load = 100 * self.client.nbw / self.client.bw
        return others_below, serverload, client_load

    def fuzzy_step(self, clients):
        time.sleep(random.random())
        self.client.update()
        others_below, serverload, client_load = self.get_fuzzy_variables(clients)
        self.do_fuzzy_action(settings.FLS.get_bw(
            serverload=serverload,
            client_load=client_load,
            others_below=others_below,
            show_graphs=False,
        ))

    def fql_eep(self, index, force_max=False):
        actions = self.q_table[index]
        """ Exploration/Exploitation Process """
        if random.uniform(0, 1) < self.EPSILON and not force_max:
            action = random.randint(0, len(actions) -1)
        else:
            Mlog.DEBUG("Max action index: ", np.argmax(actions))
            action = np.argmax(actions)
        return action

    def fql_softmax(self, index, force_max=False):
        actions = self.q_table[index]
        """ Exploration/Exploitation Process """
        l = actions
        if not force_max:
            numerator = [math.exp(num / self.TEMPERATURE) for num in l]
            denominator = sum(numerator)
            prob = [num / denominator for num in numerator]
            probp = [0, prob[0]]
            for i in range(len(prob)):
                if i not in [0, len(prob) - 1]:
                    probp.append(sum(prob[0:i + 1]))
            rand = random.random()
            for i in probp:
                if rand >= i:
                    ret = probp.index(i)
                    continue
                else:
                    break
            return ret
        else:
            Mlog.DEBUG("Max action index: ", np.argmax(actions))
            action = np.argmax(actions)
        return action

    def fql_get_action(self, clients):
        others_below, serverload, client_load = self.get_fuzzy_variables(clients)
        firing = settings.FLS.get_rules_firing(others_below, serverload, client_load)
        indexes = []
        index_action = dict()
        takagi_sugeno = 0
        denominator = functools.reduce(lambda x, y: x + y, firing, 0)
        fql_q_function = 0
        fql_v_function = 0
        for i, v in enumerate(firing):
            if v > 0.0:
                indexes.append(i)
        for index in indexes:
            # index da regra, index do fql
            index_action[index] = getattr(self, f"fql_{settings.EXPLORATION}")(index)
            Mlog.DEBUG("FIRING:", firing,)
            Mlog.DEBUG("INDEX:", index, )
            Mlog.DEBUG("action_index:", index_action[index], self.actions)
            Mlog.DEBUG("INDEXES:", len(firing), len(self.actions), index_action[index])
            takagi_sugeno  += self.actions[index_action[index]] * firing[index]
            fql_q_function += self.q_table[index][index_action[index]] * firing[index]
            fql_v_function += self.q_table[index][getattr(self, f"fql_{settings.EXPLORATION}")(index, force_max=True)] * firing[index]


        takagi_sugeno /= denominator
        fql_q_function /= denominator
        fql_v_function /= denominator

        self.fql_q_function = fql_q_function
        self.fql_v_function = fql_v_function

        if self.first:
            self.first = False
        else:
            reward = self.get_reward(clients, self.old_action)
            if settings.STRATEGY.count("fsl"):
                delta_q = reward + self.GAMMA*self.fql_q_function - self.old_fql_q_function
            else:
                delta_q = reward + self.GAMMA*self.fql_v_function - self.old_fql_q_function
            for index in self.old_index_action:
                # tem que ser causal! O atualizado não é o q-value atual, é o anterior!
                self.q_table[index][self.old_index_action[index]] += delta_q*firing[index]

        self.old_fql_q_function = fql_q_function
        self.old_index_action = index_action
        self.old_action = takagi_sugeno
        return takagi_sugeno

    def fsl_step(self, clients):
        self.fql_step(clients)

    def fql_step(self, clients):
        time.sleep(random.random())
        self.client.update()
        action = self.fql_get_action(clients)
        self.do_fuzzy_action(action)















