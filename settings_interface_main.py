from typing import Callable
from tkinter import ttk

from settings_interface.managers import (
    IntegerSettingsManager,
    FloatParamsSettingsManager,
)
from config import (
    INTEGER_VARS,
    FLOAT_VARS,
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
            config=SimulationSettings(),
            vars_array=list(INTEGER_VARS.keys()),
        )
        self.float_manager = FloatParamsSettingsManager(
            root_object=self, 
            column=1,
            config=SimulationSettings(),
            vars_array=list(FLOAT_VARS.keys()),
        )

        ttk.Button(
            self, 
            text='Submit', 
            command=self.submit_entries
        ).grid(row=0, column=3)

        self.pack()
    
    def submit_entries(self):
        self.integer_manager.submit_handler_entry()
        self.float_manager.submit_handler_entry()
        if callable(self.callback_submit):
            self.callback_submit()
        # TODO дев метод, выпилить когда проект будет закончен
        SimulationSettings()._representation()

        self.quit()

if __name__ == '__main__':
    frame_instance = SettingsFrame(width=400, height=300)
    frame_instance.mainloop()