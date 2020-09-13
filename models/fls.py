import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz
from .alert import scream
#from .utils import Bcolors
import matplotlib.pyplot as plt

# Fuzzy Black Box
class FLS(object):
    def __init__(self, bw, states):
        self.states = states + 1
        self.bw = bw

        # Input
        self.processing = ctrl.Antecedent(np.arange(0, 100, 0.5), 'cpu')
        self.bw = ctrl.Antecedent(np.arange(0, bw, 1), 'bandwidth')

        # Output
        self.state = ctrl.Consequent(np.arange(0, self.states, 1), 'state')

        # Abstractions
        self.abstractions = ["almost zero", "super low", "Very low", "low",
                             "medium", "high", "Very high", "super high","full"]

        # membership functions
        self.processing.automf(names=self.abstractions)
        self.bw.automf(names=self.abstractions)

        self.state.automf(names=[f"{i}" for i in range(self.states)])

        # Rules
        self.rules = [
            ctrl.Rule(self.processing[name] | self.bw[name],
                self.state_or_zero(name),)
            for name in self.abstractions
        ]


        # Controller
        self.controler = ctrl.ControlSystem(self.rules)

        # Simulator
        self.simulator = ctrl.ControlSystemSimulation(self.controler, cache=False)

    def get_state(self, cpu, bw):
        self.simulator.input['cpu'] = cpu
        self.simulator.input['bandwidth'] = bw
        self.simulator.compute()
        output = self.simulator.output['state']
        return output

    def state_or_zero(self, name):
        try:
            index = self.abstractions.index(name)
            #print(name)
            #print(self.states - 1/index, self.states - 1, index)
            #print(str(self.states - int((self.states - 1 )/ index)))
            return self.state[str(self.states - int((self.states - 1 )/ index))]
        except ZeroDivisionError:
            return self.state['0']


class FLSAction:
    def __init__(self):
        serverload = ctrl.Antecedent(np.arange(0, 200, 1), 'Server Load [%]')
        client_load = ctrl.Antecedent(np.arange(0, 200, 1), 'Client Load [%]')
        others_below = ctrl.Antecedent(np.arange(-100, 100, 1), 'Existence of Clients Below Threshold')
        bw = ctrl.Consequent(np.arange(-100, 100, 1), 'bandwidth')

        antecedent_lv = ["Very Lower", "Lower", "Threshold", "Higher", "Very Higher"]
        consequent_lv = ["High Decrease", "Decrease", "Light Adjust", "Increase", "High Increase"]

        # Cria automaticamente o mapeamento entre valores nítidos e difusos
        # usando uma função de pertinência padrão (triângulo)
        client_load.automf(names=antecedent_lv)
        serverload['Lower'] = fuzz.trapmf(serverload.universe, [0, 0, 0, 120])
        serverload['Higher'] = fuzz.trimf(serverload.universe, [99, 125, 200])
        serverload['Critical'] = fuzz.trapmf(serverload.universe, [125, 150, 200, 200])
        others_below['Exist'] = fuzz.trimf(others_below.universe, [0, 100, 100])
        others_below['Not Exist'] = fuzz.trimf(others_below.universe, [-101, -100, 1])
        bw.automf(names=consequent_lv)

        rules = [
            ctrl.Rule(serverload['Critical'], bw["High Decrease"]),
            ctrl.Rule(serverload['Higher'], bw["Decrease"]),
            ctrl.Rule(serverload['Lower'] & client_load['Very Lower']  & others_below['Not Exist'], bw["High Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Very Lower']  & others_below['Exist']    , bw["Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Lower']       & others_below['Not Exist'], bw["Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Lower']       & others_below['Exist']    , bw["High Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Threshold']   & others_below['Not Exist'], bw["Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Threshold']   & others_below['Exist']    , bw["Light Adjust"]),
            ctrl.Rule(serverload['Lower'] & client_load['Higher']      & others_below['Not Exist'], bw["Increase"]),
            ctrl.Rule(serverload['Lower'] & client_load['Higher']      & others_below['Exist']    , bw["Decrease"]),
            ctrl.Rule(serverload['Lower'] & client_load['Very Higher'] & others_below['Not Exist'], bw["Light Adjust"]),
            ctrl.Rule(serverload['Lower'] & client_load['Very Higher'] & others_below['Exist']    , bw["High Decrease"]),
        ]



        self.rules = rules

        self.RULE_SPACE = len(rules)
        controller = ctrl.ControlSystem(rules)
        self.serverload = serverload
        self.client_load = client_load
        self.others_below = others_below
        self.bw = bw
        self.simulator = ctrl.ControlSystemSimulation(controller)

    def get_bw(self, serverload, client_load, others_below, show_graphs=False):
        if serverload > 200:
            serverload = 200
        if client_load > 200:
            client_load = 200

        if serverload > 100:
            self.bw.defuzzify_method = 'mom'
        else:
            self.bw.defuzzify_method = 'centroid'


        self.simulator.input['Server Load [%]'] = serverload
        self.simulator.input['Client Load [%]'] = client_load
        self.simulator.input['Existence of Clients Below Threshold'] = others_below

        self.simulator.compute()
        if show_graphs:
            self.serverload.view(sim=self.simulator)
            self.others_below.view(sim=self.simulator)
            self.client_load.view(sim=self.simulator)
            self.bw.view(sim=self.simulator)
        out = self.simulator.output['bandwidth']
        #print(f'SERVER_LOAD={serverload} || CLIENT_LOAD={client_load} || OTHERS_BELOW={others_below} || OUTPUT={Bcolors.change(Bcolors.OKGREEN, out)}')
        return out

    def get_rules_firing(self, serverload, client_load, others_below):
        self.bw.defuzzify_method = 'centroid'
        self.simulator.input['Server Load [%]'] = serverload
        self.simulator.input['Client Load [%]'] = client_load
        self.simulator.input['Existence of Clients Below Threshold'] = others_below
        self.simulator.compute()
        rule_firing = []
        for r in self.rules:
            rule_firing.append(r.antecedent.membership_value[self.simulator])
        return rule_firing






if __name__ == '__main__':

    pass
    #import matplotlib
    #scale = 0.3
    #font = {'family': 'DejaVu Sans',
    #        # 'weight' : 'bold',
    #        'size': scale * 100, }
    #matplotlib.rc('font', **font)
    #plt.rc('figure', figsize=(scale * 50, scale * 30))
    #
    #fls = FLSAction()
    #fig = fls.others_below.view()
    #plt.legend(loc=4)
    #plt.savefig('others_below.pdf')
    #fls.serverload.view()
    #plt.legend(loc=4)
    #plt.savefig('severload.pdf')
    #fls.client_load.view()
    #plt.legend(loc=4)
    #plt.savefig('client_load.pdf')
    #print(fls.bw.graph)
    #
    #
    ##plt.figure(figsize=(scale * 50, scale * 30))
    #
    #
    #
    #fls.bw.view()
    #plt.legend(loc=4)
    ##matplotlib.rc('figsize', (scale * 50, scale * 30))
    #plt.savefig('bw.pdf')
    #import random
    #from matplotlib import pyplot as plt
    #values = []
    #sl = []
    #for i in range(2):
    #    server_load = random.randint(0,200)
    #    client_load = random.randint(0, 200)
    #    others_below = random.randint(-100, 100)
    #    #print(server_load, client_load, others_below)
    #    v = fls.get_bw(server_load, client_load, others_below, True)
    #    values.append(v)
    #    sl.append(server_load)
    #plt.plot(np.arange(0, len(values)), values)
    #
    #plt.plot(np.arange(0, len(values)), sl)
    #plt.show()
    #fls.bw.













