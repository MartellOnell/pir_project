from typing import Self

from datetime import datetime


class Timer:
    def __init__(self) -> None:
        self._amount_ticks: int = 0
        self.start_datetime: datetime
        self.end_datetime: datetime

    def __enter__(self) -> Self:
        self.start_datetime = datetime.now()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.end_datetime = datetime.now()
        print(f'{(self.end_datetime - self.start_datetime).total_seconds()} <- {self._amount_ticks} ticks for')

    def set_amount_ticks(self, amount_ticks: int) -> None:
        self._amount_ticks = amount_ticks