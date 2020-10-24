from matplotlib import pyplot as plt
import matplotlib
import time
import numpy as np
from models import settings

def plot_time(filename, number=0, output="XX", scale=.2):
    font = {'family': 'DejaVu Sans',
            # 'weight' : 'bold',
            'size': scale * 105, }
    matplotlib.rc('font', **font)
    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)
    filename = filename.replace("#", str(number))
    f = open(filename, 'r')
    cquit = ""
    x, y, cli = [], [], []
    for line in f.read().splitlines()[1::]:
        y.append(100*float(line.split(',')[-1])/settings.MAX_SERVER_LOAD)
        cli.append(len([float(k) for k in line.split(',')[:-1] if float(k) > 1000.0]))

    x = [i for i in range(len(y))]

    ax1.plot(range(len(x)),
             [100] * len(x),
             'k', linestyle='dotted',
             label="Cloud Load")

    ax1.plot(x, y, 'k', label="Cloud Load")
    if filename.count("cquit"):
        ax2 = ax1.twinx()
        cquit = "_cquit"
        ax2.plot(x, cli, 'b.-', label="Active Clients", )
        ax2.set_ylabel('Number of active clients')
    #else:
    ax1.set_ylim([0, max(y) if max(y) > 120 else 120])
    print(cli)
    ax1.set_ylabel('Cloud Load [%]')

    plt.xlabel('Interaction')




    plt.savefig(f"pdf/{output}_time{cquit}.pdf")
    #plt.show()










if __name__ == "__main__":
    sm = "-aw--trained"  # sm, -VT,

    elements = [
        #(f"results-dataset_fsl/fsl-compare{sm}#-5-1.txt", 'fsl', 1),
        #(f"results-dataset_fql/fql-compare{sm}#-5-1.txt", 'fql', 1),
        #(f"results-dataset_fuzzy/fuzzy-compare{sm}-2-#.txt", 'fis', 1),
        #(f"results-dataset_q/q-compare-aw--sm#-26-1--teststates.txt", 'q', 1),
        #(f"results-dataset_sarsa/sarsa-compare-aw--sm#-26-2--teststates.txt", 'sarsa', 1),

        (f"results-dataset_fuzzy/fuzzy-compare-cquit-w--sm-2-#.txt", 'fis', 2),
        #(f"results-dataset_q/q-compare-cquit-w--sm#-26-1.txt", 'q', 8),
        #(f"results-dataset_sarsa/sarsa-compare-cquit-w--sm#-26-1.txt", 'sarsa', 4),
        #(f"results-dataset_fsl/fsl-compare-cquit-w--sm#-5-1.txt", 'fsl', 13),
        #(f"results-dataset_fql/fql-compare-cquit-w--sm#-5-1.txt", 'fql', 6),
    ]
    for i in elements:
        #for n in range(19):
        #    plot_time(i[0], output=i[1], number=n)
        plot_time(i[0], output=i[1], number=i[2])
