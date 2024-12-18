import random
import requests
from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboard.inline_kb import keyboard_delete
from states.state_bot import AddState

router = Router()
url = 'http://127.0.0.1:8000'
def fetch_data(request,url,params=None):
    try:
        if request == 'GET':
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        elif request == 'POST':
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.text
        else:
            response = requests.delete(url)
            response.raise_for_status()
            return response.text
    except requests.exceptions.HTTPError as err:
        print('Ошибка HTTP:', err)
    except requests.exceptions.RequestException as err:
        print('Ошибка запроса:', err)

@router.message(CommandStart())
async def start_bot(m: Message):
    await m.answer('Привет я диспечер задач! Для работы со мной введи команду: '
                   '\n/show - посмотеть все задачи'
                   '\n/add - добавить задачу'
                   '\n/delete - удалить задачу')

@router.message(Command('show'))
async def menu_func(m: Message):
    response = fetch_data('GET',f'{url}/tasks')
    if len(response) != 0:
        tasks = ''
        for num, d in enumerate(response, start=1):
            name, date, id = d.values()
            tasks += f'\n{num}. {name} (дедлайн: {date})'
        await m.answer(tasks)
    else:
        await m.answer("У вас пока нет задач")

@router.message(Command('delete'))
async def del_func(m: Message):
    response = fetch_data('GET', f'{url}/tasks')
    if len(response) == 0:
        await m.answer('У вас в списке нет задач!')
    else:
        await m.answer('Выберите какую задачу удалить: ', reply_markup=keyboard_delete(response))

@router.callback_query(lambda c: c.data and c.data.startswith('task_'))
async def del_task(cb: CallbackQuery):
    await cb.answer()
    task_id = int(cb.data.split('_')[1])
    response = fetch_data('DELETE', f'{url}/task/{task_id}')
    if response == '200':
        await cb.message.answer(f'Задача  удалена')
    else:
        await cb.message.answer(f'Произошла ошибка - {response}')
@router.message(Command('add'))
async def add_func(m: Message, state: FSMContext):
    await m.answer(f'Введите название задчи!')
    await state.set_state(AddState.name_task)

@router.message(StateFilter('AddState:name_task'))
async  def add_name(m: Message, state: FSMContext):
    await m.answer(f'Задача - {m.text} \n'
                   f'Теперь введите дату окончания задачи \n'
                   f'Например: 01.02.2024')
    await state.update_data(name=m.text)
    await state.set_state(AddState.date_task)

@router.message(StateFilter('AddState:date_task'))
async def add_date(m: Message, state: FSMContext):
    await state.update_data(date=m.text)
    task_data = await state.get_data()
    task_name, task_date = list(task_data.values())
    params = {
        "name": task_name,
        "date": task_date,
    }
    result = fetch_data('POST',f'{url}/task',params)
    if result == '200':
        await m.answer(f'Задача с парметрами: \n'
                       f'имя: {task_name} \n'
                       f'дата: {task_date} \n'
                       f'     СОЗДАНА')
    else:
        await m.answer(f'Ошибка в создании задачи')
    await state.clear()



