import matplotlib.pyplot as plt

def save_fig(fig, fileName):
    fig.savefig(fileName + ".jpg")
    fig.savefig(fileName + ".pdf")