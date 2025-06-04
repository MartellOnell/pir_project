import subprocess

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


def spawn_process_plot():
    """
    Запуск процесса отрисовки графика
    """
    with open(STATISTIC_PATH, 'r') as f:
        data_to_subprocess = json.dumps(json.load(f))
    subprocess_script: str = (
        "from graphics import plot_statistics; "
        "data = {0}; "
        "plot_statistics(data)".format(data_to_subprocess)
    )
    subprocess.run(
        [
            "python",
            "-c",
            subprocess_script,
        ]
    )
