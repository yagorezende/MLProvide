from matplotlib import pyplot as plt
import matplotlib
import time, os, re
import numpy as np
from models import settings
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h

def get_visitation(elements, output="visitation", scale=.2):
    font = {'family': 'DejaVu Sans',
            # 'weight' : 'bold',
            'size': scale * 95, }
    matplotlib.rc('font', **font)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)

    d = dict()
    err = dict()
    x, y = [], []
    all_values = []
    for e in elements:
        f = open(e, 'r')
        text = f.read()
        f.close()

        number = int(re.findall(r"\d+", e)[0])
        lines = text.splitlines()
        #x.append(number)
        visited = set()
        total = number + 1
        collection = []
        per_collection = 500
        count=0
        for line in lines:
            agent, state, total2 = line.split(":")
            if agent == '2':
                count += 1
                visited.add(state)
                if count >= per_collection:
                    collection.append(len(visited))
                    all_values.append(len(visited))
                    visited = set()
                    count = 0

        print(len(collection))
        d[total] = np.mean(collection)
        err[total] = mean_confidence_interval(collection)
        print(number, len(lines))

        #x = [i for i in range(len(y))]

    keys = list(d.keys())
    keys.sort()
    keys = keys[0:-1]
    print(keys)
    print([err[key] for key in keys])
    print([int(err[key]) for key in keys])
    print([int(d[key]) for key in keys])


    #plt.errorbar(keys,
    #         [d[key] for key in keys], yerr=[err[key] for key in keys],
    #         fmt='k',
#
    #         label="Visitation")
#
#
    #plt.ylabel('Number of Visited states')
    #plt.xlabel('Number of States')
    ##plt.xlim([0, max(keys)-1])
    #rng = range(4, 42, 5)
    #plt.plot(rng, rng,
    #         linestyle='dotted', label="Visitation")
#
    #plt.xticks(rng)
    #plt.yticks(rng)
#
    #plt.savefig(f"pdf/{output}_visitation.pdf")
    #plt.show()
    #-------------------------------------------------
    data = all_values
    # sort the data:
    data_sorted = np.sort(data)

    # calculate the proportional values of samples
    p = 1. * np.arange(len(data)) / (len(data) - 1)

    # plot the sorted data:
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(scale * 50, scale * 30), dpi=100)

    plt.plot(data_sorted, p)
    plt.ylabel('Probability')
    plt.xlabel('Visited States')
    plt.savefig("pdf/visitation.pdf")
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
