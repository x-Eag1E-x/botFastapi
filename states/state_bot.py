from aiogram.fsm.state import State, StatesGroup


class AddState(StatesGroup):
    name_task = State()
    date_task = State()
