import matplotlib.pyplot as plt

from graphics.storage import OutputStatistic


def plot_statistics(data: OutputStatistic):
       ticks = [i + 1 for i in range(len(data['rabbits']))]
       
       plt.scatter(ticks, data['foxes'], color='red', label='Foxes')
       plt.scatter(ticks, data['rabbits'], color='blue', label='Rabbits')
       
       plt.xlabel('Tick (Index)')
       plt.ylabel('Amount (Value)')
       plt.title('Scatter Plot of Two Lists')
       plt.legend()
       plt.grid(True)
       plt.show()