from matplotlib import pyplot as plt
import matplotlib
import time, os, re
import numpy as np
from models import settings

def get_visitation(elements, output="visitation", scale=.2):
    font = {'family': 'DejaVu Sans',
            # 'weight' : 'bold',
            'size': scale * 95, }
    matplotlib.rc('font', **font)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)

    x, y = [], []
    for e in elements:
        f = open(e, 'r')
        text = f.read()
        f.close()

        number = int(re.findall(r"\d+", e)[0])
        lines = text.splitlines()

        print(number, len(lines))

        #x = [i for i in range(len(y))]

    plt.plot(range(len(x)),
             [100] * len(x),
             'k', linestyle='dotted',
             label="Cloud Load")

    plt.plot(x, y,
             'k', label="Cloud Load")

    plt.ylabel('Load [%]')
    plt.xlabel('Interaction')
    plt.ylim([0, 120])

    plt.savefig(f"pdf/{output}_visitation.pdf")
    plt.show()










if __name__ == "__main__":
    tag = "q_step"

    directory = "results-states"
    elements = [f"{directory}/{st}" for st in os.listdir(directory) if tag in st]
    #for e in elements:
    #    print(e)

    get_visitation(elements)

    #elements = [
    #    (f"results-dataset_fsl/fsl-compare{sm}#-5-1.txt", 'fsl'),
    #    (f"results-dataset_fql/fql-compare{sm}#-5-1.txt", 'fql'),
    #    (f"results-dataset_fuzzy/fuzzy-compare{sm}-2-#.txt", 'fis'),
    #    (f"results-dataset_q/q-compare{sm}#-5-1.txt", 'q'),
    #    (f"results-dataset_sarsa/sarsa-compare{sm}#-5-1.txt", 'sarsa'),
    #]
    #for i in elements:
    #    plot_time(i[0], output=i[1])
