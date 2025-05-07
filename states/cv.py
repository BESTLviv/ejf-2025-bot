from aiogram.fsm.state import State, StatesGroup

class CVStates(StatesGroup):
    position = State()
    languages = State()
    education = State()
    experience = State()
    skills = State()
    contacts = State()
    about = State() 
    confirmation = State()
