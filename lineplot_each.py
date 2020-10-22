from matplotlib import pyplot as plt
import matplotlib
import time
import numpy as np
from models import settings

def plot_time(filename, number=0, output="XX", scale=.2):
    font = {'family': 'DejaVu Sans',
            # 'weight' : 'bold',
            'size': scale * 95, }
    matplotlib.rc('font', **font)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)
    filename = filename.replace("#", str(number))
    f = open(filename, 'r')
    x, y = [], []
    for line in f.read().splitlines()[1::]:
        y.append(100*float(line.split(',')[-1])/settings.MAX_SERVER_LOAD)
    x = [i for i in range(len(y))]

    plt.plot(range(len(x)),
             [100] * len(x),
             'k', linestyle='dotted',
             label="Cloud Load")

    plt.plot(x, y,
             'k', label="Cloud Load")

    plt.ylabel('Load [%]')
    plt.xlabel('Interaction')
    plt.ylim([0, 120])

    plt.savefig(f"pdf/{output}_time.pdf")
    plt.show()










if __name__ == "__main__":
    sm = "-aw--trained"  # sm, -VT,

    elements = [
        #(f"results-dataset_fsl/fsl-compare{sm}#-5-1.txt", 'fsl'),
        #(f"results-dataset_fql/fql-compaere{sm}#-5-1.txt", 'fql'),
        #(f"results-dataset_fuzzy/fuzzy-compare{sm}-2-#.txt", 'fis'),
        (f"results-dataset_fuzzy/fuzzy-compare-cquit-w--sm-2-#.txt", 'fis'),
        #(f"results-dataset_q/q-compare{sm}#-5-1.txt", 'q'),
        #(f"results-dataset_sarsa/sarsa-compare{sm}#-5-1.txt", 'sarsa'),
    ]
    for i in elements:
        plot_time(i[0], output=i[1], number=3)
