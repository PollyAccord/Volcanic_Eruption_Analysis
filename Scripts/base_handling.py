"""
Цель: Модуль для обработки базы данных
"""

import pandas as pd
from Scripts import constants
from Scripts import globalvars as glob

# ['Year', 'Month', 'Day', 'Name', 'Location', 'Country', 'Latitude',
# 'Longitude', 'Elevation', 'Type', 'VEI', 'Agent',
# 'DEATHS', 'INJURIES', 'MISSING', 'DAMAGE_MILLIONS_DOLLARS', 'TSU', 'EQ']
bd = pd.read_csv('../Data/volcano.csv', header=0)[['Year', 'Month', 'Day', 'Name', 'Location',
                                                   'Country', 'Latitude', 'Longitude', 'Elevation',
                                                   'Type', 'VEI', 'Agent',
                                                   'DEATHS', 'INJURIES', 'MISSING',
                                                   'DAMAGE_MILLIONS_DOLLARS', 'TSU', 'EQ']]
glob.work_list['Volcano Eruption'] = glob.correct_base_values(bd)

def read_base(path: str) -> str:
    """
    Автор: Ковязин В. 
    Цель: загружает базу из файла
    Вход: путь
    Выход: новая база
    """
    # если при создании базы возникло исключение, то перебрасываем исключение дальше
    try:
        # в прочитанной базе может не оказаться всех нужных нам столбцов
        base = pd.read_csv(path, header=0)[constants.origin_columns]
    except Exception:
        raise
    base_name = path[path.rfind('\\') + 1:path.rfind('.')]
    i = 0
    # если база уже загружена в программу, то в программу добавляется ее копию с постфиксом
    if base_name in glob.work_list.keys():
        while base_name + "(" + str(i) + ")" in glob.work_list.keys():
            i += 1
        base_name += "(" + str(i) + ")"
    base = glob.correct_base_values(base)
    glob.work_list[base_name] = base
    return base_name

def create_base(path: str) -> str:

    """
    Автор: Подкопаева П.
    Цель: создает новую чистую базу
    Вход: путь
    Выход: новая база
    """
    if ".csv" in path:
        base_name = path[path.rfind('/') + 1:path.rfind('.')]
    else:
        base_name = path[path.rfind('/') + 1:]
        path += ".csv"
    new_base = pd.DataFrame(columns=constants.origin_columns)
    new_base = glob.correct_base_values(new_base)
    glob.work_list[base_name] = new_base
    new_base.to_csv(path, index=False)
    return base_name


def save_base() -> None:

    """
    Автор: Ковязин В.
    Цель: сохраняем текущую базу
    Вход: нет
    Выход: нет
    """
    glob.work_list[glob.current_base_name].to_csv("../Data/" + glob.current_base_name + ".csv",
                                                  index=False)


def searching(search_data, filter_option) -> pd.DataFrame:

    """
    Автор: Ковязин В.
    Цель: поиск по базе
    Вход: запрос и фильтр
    Выход: результат поиска
    """
    if filter_option != 'all':
        founded = glob.current_base.loc[glob.current_base[filter_option] == search_data]
        return founded
