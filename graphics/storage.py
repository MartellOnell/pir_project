from typing import TypedDict, Final

import numpy as np
import numpy.typing as npt

from settings_interface.base import Singleton


RABBIT: Final[str] = "r"
FOX: Final[str] = "f"
STATISTIC_DATA_TYPES: tuple[str, str] = (RABBIT, FOX)
STATISTIC_DATA_TYPE_MISMATCH_ERR: Final[str] = "Такого типа данных не существует: {0}"


class OutputStatistic(TypedDict):
    rabbits: list
    foxes: list


class StatisticsStorage(metaclass=Singleton):
    """
    Статистика для отображения на графиках
    (statistcs per any tick amount)
    """

    def __init__(self):
        self._rabbits_statistic: npt.ArrayLike = np.array([], dtype=np.int8)
        self._foxes_statistic: npt.ArrayLike = np.array([], dtype=np.int8)

    def add_data(self, data_type: str, value: int) -> None:
        """
        Универсальный сеттер данных
        """
        match data_type:
            case "r":
                self._rabbits_statistic = np.append(self._rabbits_statistic, [value])
            case "f":
                self._foxes_statistic = np.append(self._foxes_statistic, [value])
            case _:
                raise ValueError(STATISTIC_DATA_TYPE_MISMATCH_ERR.format(data_type))

    def get_statistics(self) -> OutputStatistic:
        """
        Вывод статистики словарём
        """
        return OutputStatistic(
            rabbits=self._rabbits_statistic.tolist(),
            foxes=self._foxes_statistic.tolist(),
        )