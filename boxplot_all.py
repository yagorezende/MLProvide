from matplotlib import pyplot as plt
import matplotlib
import time
import numpy as np
from models import settings
from time import sleep
import scipy.stats
from pprint import pprint
import matplotlib
import math


class BoxPlot(object):
    def __init__(self, client_num=3, repetitions=20, even_adjust=5, verbose=True, tenant="Tenant",
                 thb="THB", ylim=120,
                 ylabel="'Bandwidth Usage [Kb/s]'", cloudload_label="Max Cloud Load"):
        self.client_num = client_num
        self.repetitions = repetitions
        self.all_data = {}
        self.server_load = settings.MAX_SERVER_LOAD/1000
        self.scale = 0.2
        self.hatches = ["||", "//", "\\\\", "xx", "++", "..", "o", "*"]
        self.even_adjust = even_adjust
        self.verbose=verbose
        self.tenant = tenant
        self.ylim = ylim
        self.ylabel = ylabel
        self.thb = thb
        self.cloudload_label = cloudload_label

    def mean_adequacy(self, measured, expected):
        """Adequação, do Diogo"""
        return abs(np.mean(measured) / expected)

    def get_all_data_for_boxplot(self):
        ret = []
        d = self.all_data
        for n in range(self.client_num):
            for label in d:
                ret.append(d[label][n])
        return ret

    def print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)


    def format_label(self, st):
        """Formatando as labels dos gráficos"""
        d = dict(
            mdp='OC',
            LMmdp='OC\n(SR)',
            pomdp='POC',
            LMpomdp='POC\n(SR)',
            inter='Mixed',
            LMinter='Mixed\n(SR)',
            # mdp='Observable\ncase',
        )
        if st in d:
            return d[st]
        return st

    def add_data_collection(self, label="any", file="file-##.txt", excludes=tuple(), includes=tuple()):
        """Adicionando uma coleção de dados. formato ##,##,##"""

        if includes and excludes:
            raise Exception("Ou excludes ou includes, decide")
        self.all_data[label] = []

        # data collection
        dc = self.all_data[label]

        # Associando os receptores dos dados
        for i in range(self.client_num + 1):
            dc.append([])

        # main loop
        for i in range(0, self.repetitions):
        #T = 12
        #for i in range(T, T+1):
            if i in excludes or (includes and i not in includes):
                continue
            try:
                # abrindo o #ésimo arquivo
                f = open(file.replace("#", str(i)), "r")
            except:
                continue
            print(file.replace("#", str(i)))
            for line in f.read().splitlines()[1::]:
                if line != (",".join(["0"]*self.client_num)) and line:
                    total = 0
                    for k in range(self.client_num):
                        partial = float(line.split(',')[k]) / 1000
                        dc[k].append(partial)
                        total += partial
                    dc[self.client_num].append(total)
            f.close()

    def plot(self, spaces=12):
        font = {'family': 'DejaVu Sans',
                # 'weight' : 'bold',
                'size': self.scale * 95, }
        matplotlib.rc('font', **font)
        lenght = len(self.all_data)
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(self.scale * 50, self.scale * 30), dpi=100)
        labels = []
        global_x = lenght*self.client_num
        labels_pos = [math.ceil(lenght/2 + lenght*i) for i in range(self.client_num)]
        self.print(labels_pos)
        for i in range(global_x):
            if i + 1 in labels_pos:
                sp = ""
                self.print("label:", i)
                if (i) % 2 == 0 and math.ceil(lenght/2) + 1 % 2 == 0:
                    sp = " "*self.even_adjust
                labels.append(f"{sp}{self.tenant} {int(2 + (i-lenght/2)/lenght)}")
            else:
                labels.append("")



        # rectangular box plot
        meanpointprops = dict(marker='D', markeredgecolor='black',
                              markerfacecolor='firebrick')
        flierprops = dict(markersize=3, marker='+')

        all_data = self.get_all_data_for_boxplot()


        for i in range(self.client_num):
            kw = {}
            if i == 0:
                kw['label'] = self.thb
            plt.bar(
                1 + (lenght-1)/2 + (lenght)*i, # center
                [getattr(settings, f"CLIENT{i+1}_BW") / 1000] * 2, #height
                lenght-1, #length
                color="lightblue",
                edgecolor='black',#
                **kw
            )


        bplot = axes.boxplot(all_data,
                             vert=True,  # vertical box alignment
                             patch_artist=True, notch=2,
                              flierprops=flierprops,
                             meanprops=meanpointprops,
                             labels=labels,
                             )  # will be used to label x-ticks

        # fill with colors


        colors = ['white'] * lenght * self.client_num
        hatches = self.hatches[0:lenght] * self.client_num
        for patch, color, hatch in zip(bplot['boxes'], colors, hatches):
            patch.set_facecolor(color)
            patch.set_hatch(hatch)

        h = 0
        for label in self.all_data:
            plt.bar([0], [0], 0, label=label, color=colors[0], edgecolor='black', hatch=hatches[h])
            h += 1

        plt.plot(range(lenght * self.client_num + 1),
                 [self.server_load for i in range(lenght * self.client_num + 1)],
                 'k', linestyle='dotted',
                 label=self.cloudload_label)


        plt.ylabel(self.ylabel)
        plt.ylim([0, self.ylim])
        legend = plt.legend(frameon=False, ncol=2)

    def savefig(self, filename="pdf/any.pdf"):
        plt.savefig(filename)


    def infinite_loop(self, interval=30, filename="pdf/any.pdf"):
        while 1:
            time.sleep(interval)
            self.plot()
            self.savefig(filename)



if __name__ == "__main__":

    bp = BoxPlot(
        ylabel='Vazão [Kb/s]',
        ylim=2000,
        cloudload_label='Limite Superior de Tráfego',
        tenant='Inquilino',
        thb='Banda Contratada',
    )

    sm = "--trained" # sm, -VT,

    #sm = ""
    bp.add_data_collection(
        label="FIS",
        file=f"results-dataset_fuzzy/fuzzy-compare--2-#.txt",
        #excludes=(5,)
    )
    bp.add_data_collection(
        label="FSL",
        file=f"results-dataset_fsl/fsl-compare{sm}#-5-1.txt",
        #includes=(10, 9, 8, 7, 3, 2,),
    )
    #bp.add_data_collection(
    #    label="FQL",
    #    file=f"results-states_fql/fql-compare{sm}#-5-1.txt",
    #    #excludes=(,),
    #)
    #bp.add_data_collection(
    #    label="Q-Learning",
    #    file=f"results-states_q/q-compare{sm}#-5-1.txt",
    #    #includes=(1,)
    #    excludes=(5,),
    #)
    #bp.add_data_collection(
    #    label="SARSA",
    #    file=f"results-states_sarsa/sarsa-compare{sm}#-5-1.txt",
    #    #excludes=(1, 2, 3)
    #)


    bp.plot()
    bp.savefig(f"pdf/boxplot{sm}.pdf")






