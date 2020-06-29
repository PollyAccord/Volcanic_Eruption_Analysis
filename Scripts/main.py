"""
Цель: Главный модуль, соединяющий остальные модули приложения
"""

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from Scripts import constants
from Scripts import base_handling as hand_base
from Scripts import globalvars as glob
from Scripts import interface as ui
from Library import error_edit_windows as err


def setup() -> tk.Tk:
    """
    Автор: Ковязин В. 
    Цель: создание главного окна и расстановка всех его компонентов
    Вход: Нет
    Выход: объект главного окна
    """
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Selection.TCheckbutton', anchor="w")
    glob.icons = {'save_icon': tk.PhotoImage(file="../Graphics/save_icon.gif",
                                             master=root),
                  'add_icon': tk.PhotoImage(file="../Graphics/add_icon.gif",
                                            master=root),
                  'edit_icon': tk.PhotoImage(file="../Graphics/edit_icon.gif",
                                             master=root),
                  'load_icon': tk.PhotoImage(file="../Graphics/load_icon.gif",
                                             master=root),
                  'close_icon': tk.PhotoImage(file="../Graphics/close_icon.gif",
                                              master=root),
                  'add_field_icon': tk.PhotoImage(file="../Graphics/add_field_icon.gif",
                                                  master=root),
                  'del_field_icon': tk.PhotoImage(file="../Graphics/del_field_icon.gif",
                                                  master=root)}

    root.title('Volcano Analyse')

    pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL, width=1)

    # создаем и заполняем строчку меню
    ui.create_menu(root, load_event)

    # фрейм кнопочек
    ui.create_toolbar(root, pane, load_event, save_event, create_event, glob.icons)

    # лист для баз данных
    frame = ui.create_list4db(root, pane)

    pane.add(frame, weight=1)
    pls_select_frame = ui.show_invitation(pane)
    pane.add(pls_select_frame, weight=9)
    pane.grid(row=1, column=0, columnspan=3, sticky="NSEW")

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=99)
    root.grid_rowconfigure(3, weight=1)

    root.grid_columnconfigure(0, weight=1, minsize=150)
    root.grid_columnconfigure(1, weight=99)
    return root


def load_event(*args):
    """
        Автор: Баканов Г.
        Цель: обработка события загрузки новой базы инструментами OS
        Вход: Нет
        Выход: нет
    """
    path = filedialog.askopenfilename(initialdir="../Data/",
                                      filetypes=(("Database files", "*.csv"), ("All files", "*.*")))
    path = path.replace('/', "\\")
    try:
        base_name = hand_base.read_base(path)
        glob.base_list.insert(tk.END, base_name)
    except FileNotFoundError:
        pass
    except Exception as error:
        message = str(error)
        err.error(message[message.find('['):message.find(']') + 1] + " нет в Базе Данных")
    return "break"


def create_event(*args):
    """
    Автор: Подкопаева П.
    Цель: создание новой базы, если база уже существует в рабочей директории
                 windows обеспечивает выбор, перезаписывать файл или нет.
    Вход: Нет
    Выход: объект главного окна
    """
    new_base_path = filedialog.asksaveasfilename(initialdir="../Data/",
                                                 filetypes=(("Database files", "*.csv"),
                                                            ("All files", "*.*")))
    new_base_name = hand_base.create_base(new_base_path)
    # если имя открытой базы совпадает с именем новой базы
    if glob.current_base_name == new_base_name:
        glob.clear_workspace()
        glob.current_base = glob.work_list[new_base_name]
    # если новой базы нет в листе - добавляем
    elif new_base_name not in glob.base_list.get(0, tk.END):
        glob.base_list.insert(tk.END, new_base_name)
    # если имя открытой базы уже есть в листе, то пользователь все равно выбрал перезаписывать файл
    # так что нам не нужно расматривать этот вариант и база уже перезаписалась на новую в work_list
    return "break"


def save_event(*args):
    """
    Автор: Баканов Г. 
    Цель: Сохранение текущей базы в файл
    Вход: Нет
    Выход: Нет (файл)
    """
    # открыта ли база?
    if not glob.is_db_open():
        return "break"
    # сохранена ли база?
    if not glob.is_saved():
        glob.unmark_changes()
        glob.work_list[glob.current_base_name] = glob.current_base
        glob.update_list()
        # сохраняем в файл
        hand_base.save_base()


ui.load_event = load_event
ui.create_event = create_event
ui.save_event = save_event
root = setup()

root.config(background="white")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.minsize(constants.style['app_width'], constants.style['app_height'])
root.maxsize(screen_width, screen_height)
root.geometry(str(constants.style['app_width']) + 'x' + str(constants.style['app_height']))
root.mainloop()
