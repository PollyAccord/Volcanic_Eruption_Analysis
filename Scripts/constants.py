"""
Цель: Модуль констант приложения
Автор: Баканов Г., Ковязин В.
"""

origin_columns = ['Year', 'Month', 'Day', 'Name', 'Location', 'Country', 'Latitude', 'Longitude',
                  'Elevation', 'Type', 'VEI', 'Agent', 'DEATHS', 'INJURIES', 'MISSING', 'DAMAGE_MILLIONS_DOLLARS',
                  'TSU', 'EQ']
"""
    origin_columns содержит название всех столбцов, которые должны быть в программе обязательно,
    Если в загружаемой в программу БД нет столбца(ов), то (придумать что будет)
"""

tree_rows_number: int = 45
"""количество отображаемых на экране строчек таблицы"""

first_form = ['Name', 'Latitude', 'Elevation', 'Longitude', 'Type']
second_form = ['Location', 'Country', 'Latitude', 'Longitude']
third_form = ['Year', 'Month', 'Day', 'Name', 'VEI', 'Agent', 'DEATHS', 'INJURIES', 'MISSING',
              'DAMAGE_MILLIONS_DOLLARS', 'TSU', 'EQ']

quality_columns = ['Name', 'Location', 'Country', 'Latitude', 'Longitude', 'Type', 'VEI', 'Agent', 'TSU', 'EQ']
quantity_columns = ['Elevation', 'DEATHS', 'INJURIES', 'MISSING', 'DAMAGE_MILLIONS_DOLLARS']

with open("../Library/config.ini", 'r', encoding='utf-8') as f:
    config = f.read()

style = eval(config)
