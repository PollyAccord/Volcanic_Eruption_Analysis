"""
Цель: Модуль, содержащий основные глобальные переменные программы
Автор: Ковязин В., Баканов Г., Подкопаева П.
"""
from tkinter import BooleanVar
from tkinter import Listbox
from tkinter import PhotoImage
from tkinter.ttk import Treeview
from typing import Dict
from typing import List

import numpy as np
from pandas import DataFrame

from Library import error_edit_windows as err
from Scripts import constants

# просто типы данных для удобства исипользования в подсказках
Icons = Dict[str, PhotoImage]
BaseRecord = Dict[str, DataFrame]
SelectionDict = Dict[str, BooleanVar]
Columns = List[str]

columns: Columns = constants.origin_columns
"""
В columns будут храниться все столбцы, отображаемые в данный момент в программе.
Программа будет автоматически отображать новые столбцы и убирать удаленные.
"""

work_list: BaseRecord = {}
"""
Словарь со значениями (Имя БД: объект БД).
В нем хранятся все базы данных, которые были загруженны в программу.
При сохранении будет сохраняться именно базы из словаря.
"""

current_base: DataFrame = None
"""Текущий dataframe, с которым работает пользователь."""

current_base_name: str = None
"""Имя текущего dataframe, с которым работает пользователь."""

current_base_list_id: int = None
"""id текущего dataframe в ListBox, с которым работает пользователь."""

table4base: Treeview = None
"""
    Объект TreeView, данные из которого отображаются в workspace.
    В TreeView хранятся все данные из выбранной базы данных.
"""

base_list: Listbox = None
"""
    Объект Listbox, который отображается в программе.
    в нем хранятся все имена загруженных баз
    с помощью него осуществляется выбор пользователем
"""

columns_selection: SelectionDict = None
"""
    Словарь для выбора столбцов, которые должны отображаться в программе,\n
    {Столбец: Значение}, где значение отвечает, будет ли отображаться столбец
"""

icons: Icons = {}
"""для иконок, нужна для того,
чтобы garbage collector не съедал их из-за отсутствия ссылки на них"""

sort = True
"""переключатель для сортировки таблицы"""


def is_saved() -> bool:
    """
    Автор: Ковязин В. 
    Цель: проверяет, сохранена ли база
    Вход: нет
    Выход: true, false
    """
    global current_base_name
    if "*" in current_base_name:
        return False
    return True


def is_db_open() -> bool:
    """
    Автор: Ковязин В. 
    Цель: проверка, окрыта ли база
    Вход: Нет
    Выход: true, false
    """
    if current_base is None:
        err.error("База не выбранна!")
        return False
    return True


def delete_current_base():
    """
    Автор: Подкопаева П. 
    Цель: удаляет базу из программы
    Вход: нет
    Выход: нет
    """
    global work_list, current_base_name, current_base_list_id, current_base
    del work_list[current_base_name]
    current_base = None
    current_base_name = None
    base_list.delete(current_base_list_id)
    current_base_list_id = None


def mark_changes():
    """
    Автор: Подкопаева П.
    Цель: убирает пометку в имени текущей базы наличие несохраненных изменений
    Вход: нет
    Выход: нет
    """
    global current_base_name
    if is_saved():
        current_base_name += "*"


def unmark_changes():
    """
    Автор: Подкопаева П.
    Цель: помечает в имени текущей базы наличие несохраненных изменений
    Вход: нет
    Выход: нет
    """
    global current_base_name
    if not is_saved():
        current_base_name = current_base_name.replace('*', '')


def correct_base_values(base: DataFrame) -> DataFrame:
    """
    Автор: Ковязин В.
    Цель: при добавлении в таблицу измененных пользователем данных могут возникнуть nan значения,
            их мы меняем на пустые строки или на 0, так же nan меняет типы столбцов на другой,
            здесь мы обратно приводим тип столбцов к нужному
    Вход: нет
    Выход: нет
    """
    base = base.replace('', np.nan)
    base[['Year', 'Month', 'Day']] = base[['Year', 'Month', 'Day']].replace(np.nan, 0)
    base[['Name', 'Location', 'Country', 'Type', 'Agent']] = base[
        ['Name', 'Location', 'Country', 'Type', 'Agent']].replace(np.nan, " ")
    base[['TSU']] = base[['TSU']].replace('TSU', '+')
    base[['EQ']] = base[['EQ']].replace('EQ', '+')
    base[['TSU']] = base[['TSU']].replace(np.nan, '-')
    base[['EQ']] = base[['EQ']].replace(np.nan, '-')
    base = base.astype({'Year': 'int32', 'Month': 'int32', 'Day': 'int32',
                        'Latitude': 'float64', 'Longitude': 'float64', 'VEI': 'float64',
                        'DEATHS': 'float64', 'INJURIES': 'float64', 'MISSING': 'float64',
                        'DAMAGE_MILLIONS_DOLLARS': 'float64'})
    base[['Name', 'Location', 'Country',
          'Type', 'Agent', 'TSU',
          'EQ']] = base[['Name', 'Location', 'Country',
                         'Type', 'Agent', 'TSU',
                         'EQ']].astype(str)
    base = base.astype({'Name': 'str', 'Location': 'str', 'Country': 'str',
                        'Type': 'str', 'Agent': 'str', 'TSU': 'str',
                        'EQ': 'str'})
    return base


def update_workspace():
    """
    Автор: Баканов Г.
    Цель: обновляет содержимое рабочего пространства
    Вход: нет
    Выход: нет
    """
    global current_base
    global columns
    assert current_base is not None
    for i in list(current_base.index):
        insert = current_base.iloc[i, :]
        for j in columns:
            table4base.set(i, column=j, value=insert[j])


def clear_workspace():
    """
    Автор: Баканов Г.
    Цель: очищает рабочее пространство
    Вход: нет
    Выход: нет
    """
    global current_base
    global columns
    assert current_base is not None
    table4base.delete(*list(range(len(current_base.index))))


def update_list():
    """
    Автор: Баканов Г.
    Цель: заново добавляет текущую базу в base_list
    Вход: нет
    Выход: нет
    """
    global current_base
    global current_base_list_id
    base_list.delete(current_base_list_id)
    base_list.insert(current_base_list_id, current_base_name)
