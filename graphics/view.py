import multiprocessing

import matplotlib.pyplot as plt
import json

from graphics.storage import OutputStatistic
from config import STATISTIC_PATH


def plot_statistics(data: OutputStatistic):
    plt.plot(data['rabbits'], data['foxes'], 'o-', color='red', label='amount')

    plt.xlabel('Rabbits')
    plt.ylabel('Foxes')
    plt.title('Scatter Plot ({0} ticks)'.format(len(data['rabbits'])))
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_statistics_per_tick(data: OutputStatistic):
    x_axis = [i for i in range(0, len(data['foxes']))]
    plt.plot(x_axis, data['foxes'], 'o-', color='red', label='foxes amount')
    plt.plot(x_axis, data['rabbits'], 'o-', color='blue', label='rabbits amount')
    plt.xlabel('tick')
    plt.ylabel('animals amount')
    plt.legend()
    plt.grid(True)
    plt.show()


def spawn_process_plot(plot_view_func: str = 'plot_statistics'):
    """
    Запуск процесса отрисовки графика
    """
    with open(STATISTIC_PATH, 'r') as f:
        data_to_process = json.load(f)

    
    match plot_view_func:
        case 'plot_statistics':
            plot_func = plot_statistics
        case 'plot_statistics_per_tick':
            plot_func = plot_statistics_per_tick
        case _:
            raise ValueError(f"Unknown plot view function: {plot_view_func}")
    
    process = multiprocessing.Process(
        target=plot_func,
        args=(data_to_process,),
        name='plot_process',
    )
    process.start()
    process.join()
