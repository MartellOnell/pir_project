from typing import Callable
from tkinter import ttk

from settings_interface.managers import (
    IntegerSettingsManager,
    FloatParamsSettingsManager,
)
from config import (
    INTEGER_VARS,
    FLOAT_VARS,
    SimulationStatusChoices,
    SimulationSettings,
)


class SettingsFrame(ttk.Frame):
    def __init__(self, callback_submit: Callable = None, **kwargs):
        self.callback_submit = callback_submit

        super().__init__(None, **kwargs)

        self.master.title('Simulation settings')

        self.integer_manager = IntegerSettingsManager(
            root_object=self, 
            column=0,
            config=SimulationSettings(), # noqa
            vars_array=list(INTEGER_VARS.keys()),
        )
        self.float_manager = FloatParamsSettingsManager(
            root_object=self, 
            column=1,
            config=SimulationSettings(), # noqa
            vars_array=list(FLOAT_VARS.keys()),
        )

        ttk.Button(
            self, 
            text='Start simulation',
            command=lambda: self.submit_entries(SimulationStatusChoices.SIMULATION)
        ).grid(row=0, column=3)

        ttk.Button(
            self,
            text='Start naked simulation',
            command=lambda: self.submit_entries(SimulationStatusChoices.NAKED_SIMULATION)
        ).grid(row=1, column=3)

        self.pack()
    
    def submit_entries(self, status: str):
        self.integer_manager.submit_handler_entry()
        self.float_manager.submit_handler_entry()
        SimulationSettings().set_value('status', status)
        if callable(self.callback_submit):
            self.callback_submit()
        # TODO дев метод, выпилить когда проект будет закончен
        SimulationSettings()._representation()
        self.master.destroy()
        self.master.quit()

if __name__ == '__main__':
    frame_instance = SettingsFrame(width=400, height=300)
    frame_instance.mainloop()