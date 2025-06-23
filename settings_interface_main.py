from typing import Callable
from tkinter import ttk, IntVar
from multiprocessing import Process

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
from graphics.view import spawn_process_plot


class SettingsFrame(ttk.Frame):
    def __init__(self, callback_submit: Callable = None, **kwargs):
        self.callback_submit = callback_submit
        self._simulation_vars_config = SimulationSettings()

        super().__init__(None, **kwargs)

        self.master.title('Simulation settings')

        self.integer_manager = IntegerSettingsManager(
            root_object=self, 
            column=0,
            config=self._simulation_vars_config, # noqa
            vars_array=list(INTEGER_VARS.keys()),
        )
        self.float_manager = FloatParamsSettingsManager(
            root_object=self, 
            column=1,
            config=self._simulation_vars_config, # noqa
            vars_array=list(FLOAT_VARS.keys()),
        )

        # точки запуска и общая конфигурация
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

        ttk.Button(
            self,
            text='Draw last statistics',
            command=lambda: spawn_process_plot()
        ).grid(row=2, column=3)

        ttk.Button(
            self,
            text='Draw last statistics per ticks',
            command=lambda: spawn_process_plot(
                plot_view_func='plot_statistics_per_tick',
            )
        ).grid(row=3, column=3)

        use_save_result_in_file_var = IntVar()
        ttk.Checkbutton(
            self,
            command=(
                lambda: self._simulation_vars_config.set_value(
                    var_name='save_result_in_file',
                    value=bool(use_save_result_in_file_var.get()),
                )
            ),
            variable=use_save_result_in_file_var,
            text='Save results in file',
        ).grid(row=4, column=3)

        self.pack()
    
    def submit_entries(self, status: str):
        self.integer_manager.submit_handler_entry()
        self.float_manager.submit_handler_entry()
        SimulationSettings().set_value('status', status)
        if callable(self.callback_submit):
            self.callback_submit()
        self.master.destroy()
        self.master.quit()

if __name__ == '__main__':
    frame_instance = SettingsFrame(width=400, height=300)
    frame_instance.mainloop()