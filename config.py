import pprint
from typing import Final

from settings_interface.base import Singleton


STATISTIC_PATH: Final[str] = "statistics.json"


class SimulationStatusChoices:
    SIMULATION = "simulation" # cтандартная симуляция с визуализацией
    SETUP = "setup" # настройка симуляции
    NAKED_SIMULATION = "naked_simulation" # голая симуляция без визуализации


STRING_VARS: dict[str, str] = {
    "status": SimulationStatusChoices.SETUP,
}

INTEGER_VARS: dict[str, int] = {
    'bush_amount': 0,
    'berries_random_from': 10,
    'berries_random_to': 20,
    'berries_regrowth_time': 50,
    'rabbit_amount': 200,
    'rabbit_max_age_random_from': 150,
    'rabbit_max_age_random_to': 200,
    'rabbit_min_breeding_age': 8,
    'rabbit_vision_radius': 15,
    'fox_amount': 50,
    'fox_max_age_random_from': 250,
    'fox_max_age_random_to': 350,
    'fox_min_breeding_age': 10,
    'fox_vision_radius': 30,
}

FLOAT_VARS: dict[str, float] = {
    'rabbit_breeding_probability': 1,
    'fox_breeding_probability': 0.6,
    'fox_move_speed': 6,
}


class SimulationSettings(metaclass=Singleton):
    def __init__(self):
        self.__data = {
            **INTEGER_VARS,
            **FLOAT_VARS,
            **STRING_VARS,
        }

    def set_value(self, var_name: str, value: any) -> None:
        """
        Сеттер для установки значения атрибута
        """
        if var_name not in self.__data:
            raise AttributeError(f"Attribute {var_name} not found")
        self.__data[var_name] = value
        print(f"Set {var_name} to {value}")

    def get_attr(self, var_name: str) -> any:
        """
        Геттер для получения значения атрибута
        """
        if var_name not in self.__data:
            raise AttributeError(f"Attribute {var_name} not found")
        return self.__data.get(var_name)
    
    def _representation(self) -> None:
        """
        Чисто дев метод для просмотра содержимого класса
        """
        pprint.pp(self.__data)
