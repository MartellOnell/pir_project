from tkinter import ttk

from .base import AbstractSettingsManager


class IntegerSettingsManager(AbstractSettingsManager):
    ENTRY_AMOUNT_TEMPLATE: str = "entry_integer_{0}"
    ENTRY_LABEL_TEMPLATE: str = "integer param \"{0}\" (default: {1})"

    def generate_entry_instance(self) -> ttk.Entry:
        vcmd = (self.root_object.register(self.value_number_validate))
        return ttk.Entry(self.root_object, validate='all', validatecommand=(vcmd, '%P'))

    def value_number_validate(self, value) -> bool:
        return value.isdigit() or value == ""

    def submit_handler_entry(self) -> None:
        for variable in self.vars_array:
            value_to_set: str = self.get_entry_amount_var(variable).get()
            if self.value_number_validate(value_to_set) and value_to_set != "":
                self.config.set_value(variable, int(value_to_set))


class FloatParamsSettingsManager(AbstractSettingsManager):
    ENTRY_AMOUNT_TEMPLATE: str = "entry_float_param_{0}"
    ENTRY_LABEL_TEMPLATE: str = "float param \"{0}\" (default: {1})"

    def generate_entry_instance(self) -> ttk.Entry:
        vcmd = (self.root_object.register(self.value_number_validate))
        return ttk.Entry(self.root_object, validate='key', validatecommand=(vcmd, '%P'))

    def value_number_validate(self, value) -> bool:
        try:
            float(value)
        except ValueError:
            return False
        return True

    def submit_handler_entry(self) -> None:
        for variable in self.vars_array:
            value_to_set: str = self.get_entry_amount_var(variable).get()
            if self.value_number_validate(value_to_set) and value_to_set != "":
                self.config.set_value(variable, float(value_to_set))
