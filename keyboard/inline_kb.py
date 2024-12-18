from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def keyboard_delete(data):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for num, task in enumerate(data,start=1):
        button = InlineKeyboardButton(
            text=f'Удалить {num}',
            callback_data=f'task_{task['id']}'
        )
        kb.inline_keyboard.append([button])
    return kb