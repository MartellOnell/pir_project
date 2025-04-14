import abc
from tkinter import ttk


class Singleton(type):
    """
    Мета класс для синглтона
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSimulationConfig(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def set_value(self, var_name: str, value: any) -> None:
        """
        Сеттер для установки значения атрибута
        """

    @abc.abstractmethod
    def get_attr(self, var_name: str) -> any:
        """
        Геттер для получения значения атрибута
        """
    
    @abc.abstractmethod
    def _representation(self) -> None:
        """
        Чисто дев метод для просмотра содержимого класса
        """

class AbstractSettingsManager(metaclass=abc.ABCMeta):
    """
    """
    ENTRY_AMOUNT_TEMPLATE: str = "entry_{0}"
    ENTRY_LABEL_TEMPLATE: str = "{0} (default: {1})"

    def __init__(
        self,
        root_object: ttk.Frame,
        column: int,
        config: AbstractSimulationConfig,
        vars_array: list[str],
    ) -> None:
        self.root_object = root_object
        self.column = column
        self.config = config
        self.vars_array = vars_array
        self.generate_blocks()
    
    def get_entry_amount_var(self, var_name: str) -> ttk.Entry:
        """
        Геттер для amount инпутов
        """

        return getattr(self, self.ENTRY_AMOUNT_TEMPLATE.format(var_name), None)
    
    def get_entry_label(self, var_name: str, default_value: any) -> str:
        return " ".join(self.ENTRY_LABEL_TEMPLATE.format(var_name, default_value).split("_"))
    
    def create_entry_amount_var(self, var_name: str, row: int) -> None:
        """
        Сеттер для amount инпутов
        """

        if self.get_entry_amount_var(var_name) is not None:
            raise AttributeError(f"Entry {var_name} already exists")
        
        entry: ttk.Entry = self.generate_entry_instance()
        entry.grid(row=row, column=self.column, padx=5, pady=5)
        
        setattr(
            self,
            self.ENTRY_AMOUNT_TEMPLATE.format(var_name),
            entry,
        )

        return entry

    def generate_blocks(self) -> None:
        """
        Инициализация и отрисовка виджетов для ввода количественных параметров
        """

        count_row_index: int = 0
        for var_name in self.vars_array:
            var_entry_label: str = self.get_entry_label(var_name=var_name, default_value=self.config.get_attr(var_name))

            ttk.Label(self.root_object, text=var_entry_label).grid(row=count_row_index, column=self.column, padx=5, pady=5)
            count_row_index += 1
            self.create_entry_amount_var(var_name=var_name, row=count_row_index)
            count_row_index += 1

    @abc.abstractmethod
    def generate_entry_instance(self) -> ttk.Entry:
        """
        Функция для генерации инстанса ввода с определёнными параметрами
        """
        pass

    @abc.abstractmethod
    def submit_handler_entry(self) -> None:
        """
        Хэндлер подтверждения для обработки количественных параметров
        """
        pass

    @abc.abstractmethod
    def value_number_validate(self, value) -> bool:
        """
        Валидация для инпутов
        """
        pass
