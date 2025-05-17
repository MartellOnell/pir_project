import matplotlib.pyplot as plt

from graphics.storage import OutputStatistic


def plot_statistics(data: OutputStatistic):
       plt.plot(data['rabbits'], data['foxes'], 'o-', color='red', label='amount')
       
       plt.xlabel('Rabbits')
       plt.ylabel('Foxes')
       plt.title('Scatter Plot ({0} ticks)'.format(len(data['rabbits'])))
       plt.legend()
       plt.grid(True)
       plt.show()