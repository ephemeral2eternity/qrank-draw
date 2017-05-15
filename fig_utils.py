from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

def save_fig(fig,fileName):
    pdf = PdfPages(fileName + '.pdf')
    pdf.savefig(fig)