import numpy as np
import matplotlib.pyplot as plt

def draw_cdf(data, ls, lg):
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data))/float(len(sorted_data))
    plt.plot(sorted_data, yvals, ls, label=lg, linewidth=2.0)