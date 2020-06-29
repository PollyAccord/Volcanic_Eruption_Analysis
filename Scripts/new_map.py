"""
Цель: Модуль для построения карты
"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb

import folium
from folium.plugins import MarkerCluster

from Scripts import base_handling as hand_base
from Scripts import globalvars as glob
from Scripts import constants


def choice_map(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Подкопаева П.
    Цель: Функция для выбора типа карты
    Вход: Главное окно, растягивающий виджет
    Выход: Нет
    """
    global CHOSEN_VALUE_MAP

    if not glob.is_db_open():
        return "break"

    win = tk.Toplevel(root)
    win.title("Выбор")
    win.geometry("300x300+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    choice = ("По высоте", "По смертности", "По ущербу")

    make_map = tk.Label(background, text='Это окно для построения карт', bg=constants.style['bg'])
    make_map.place(relx=0.1, rely=0.1)
    make_map.pack()
    CHOSEN_VALUE_MAP = tk.StringVar(value='Выберите тип карты')
    make_table_op = tk.OptionMenu(background, CHOSEN_VALUE_MAP, *choice)
    make_table_op.place(relx=0.25, rely=0.4)
    make_table_op.pack()

    button_statistics = tk.Button(background, text='Сохранить', bg=constants.style['plots_button'])

    button_statistics.bind("<Button-1>", lambda *args: new_map())
    button_statistics.place(relx=0.2, rely=0.5, relheight=0.1, relwidth=0.6)
    background.pack(side="top", fill="both", expand=True, padx=10, pady=5)


def new_map():
    """
    Автор: Подкопаева П.
    Цель: Функция для построения карты
    Вход: Нет
    Выход: Нет
    """
    global CHOSEN_VALUE_MAP

    lat = hand_base.bd['Latitude']
    lon = hand_base.bd['Longitude']

    if CHOSEN_VALUE_MAP.get() == 'Выберите тип карты':
        mb.showerror("Ошибка!", "Сначала выберите вариант карты!")

    elif CHOSEN_VALUE_MAP.get() == 'По высоте':
        map_elevation(lat, lon)
        mb.showinfo("Инфо", "Карта высот сохранена")

    elif CHOSEN_VALUE_MAP.get() == 'По смертности':
        map_deaths(lat, lon)
        mb.showinfo("Инфо", "Карта смертности сохранена")

    elif CHOSEN_VALUE_MAP.get() == 'По ущербу':
        map_damage(lat, lon)
        mb.showinfo("Инфо", "Карта ущерба сохранена")


# для высоты
def map_elevation(lat, lon):
    """
    Автор: Баканов Г.
    Цель: Функция для построения карты по высоте
    Вход: dataframe
    Выход: нет (файл)
    """
    elevation = hand_base.bd['Elevation']
    name = hand_base.bd['Name']

    def color_change(elevation):
        """
        Автор: Баканов Г.
        Цель: Функция, устанавливающая цвета
        Вход: Int высота
        Выход: Строка с цветом
        """
        if elevation < 500:
            return 'green'
        if 500 <= elevation < 1000:
            return 'yellow'
        if 1000 <= elevation < 3000:
            return 'red'
        if elevation > 3000:
            return 'black'

    map = folium.Map(location=[-6.2146200, 106.8451300], zoom_start=6, titles="Mapbox bright")
    marker_cluster = MarkerCluster().add_to(map)

    for lat1, lon1, elevation, name in zip(lat, lon, elevation, name):
        folium.Marker(location=[lat1, lon1], radius=9,
                      popup='Name: ' + str(name) + '\n' + 'Elevation: ' + str(elevation) + " m",
                      fill_color=color_change(elevation),
                      color="gray", fill_opacity=0.9).add_to(marker_cluster)

    map.save("../Output/map_elevation.html")


# для смертности
def map_deaths(lat, lon):
    """
    Автор: Ковязин В.
    Цель: Функция для построения карты по смертям
    Вход: dataframe
    Выход: нет(файл)
    """
    deaths = hand_base.bd['DEATHS'].fillna(0)
    name = hand_base.bd['Name']

    def color_change(deaths):
        """
        Автор: Ковязин В. 
        Цель: Функция, устанавливающая цвета
        Вход: Int смерти
        Выход: Строка с цветом
        """
        if deaths < 500:
            return 'green'
        if 500 <= deaths < 1000:
            return 'yellow'
        if 1000 <= deaths < 2000:
            return 'red'
        if deaths > 2000:
            return 'black'

    map = folium.Map(location=[-6.2146200, 106.8451300], zoom_start=6, titles="Mapbox bright")
    marker_cluster = MarkerCluster().add_to(map)

    for lat1, lon1, deaths, name in zip(lat, lon, deaths, name):
        folium.Marker(location=[lat1, lon1], radius=9,
                      popup='Name: ' + str(name) + '\n' + 'Deaths: ' + str(deaths),
                      fill_color=color_change(deaths),
                      color="gray", fill_opacity=0.9).add_to(marker_cluster)

    map.save("../Output/map_deaths.html")

    # для ущерба
def map_damage(lat, lon):
    """
    Автор: Подкопаева П. 
    Цель: Функция для построения карты по ущербу
    Вход: dataframe
    Выход: нет (файл)
    """
    damage = hand_base.bd['DAMAGE_MILLIONS_DOLLARS'].fillna(0)
    name = hand_base.bd['Name']

    def color_change(damage):
        """
        Автор: Подкопаева П.
        Цель: Функция, устанавливающая цвета
        Вход: Int ущерб
        Выход: Строка с цветом
        """
        if damage < 50:
            return 'green'
        if 50 <= damage < 100:
            return 'yellow'
        if 100 <= damage < 200:
            return 'red'
        if damage > 200:
            return 'black'

    map = folium.Map(location=[-6.2146200, 106.8451300], zoom_start=6, titles="Mapbox bright")
    marker_cluster = MarkerCluster().add_to(map)

    for lat1, lon1, damage, name in zip(lat, lon, damage, name):
        folium.Marker(location=[lat1, lon1], radius=9,
                      popup='Name: ' + str(name) + '\n' + 'Damage: ' + str(damage),
                      fill_color=color_change(damage),
                      color="gray", fill_opacity=0.9).add_to(marker_cluster)

    map.save("../Output/map_damage.html")
