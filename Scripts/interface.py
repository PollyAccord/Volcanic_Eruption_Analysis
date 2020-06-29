"""
Цель: Модуль, отвечающий за интерфейс приложения
"""


import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb, filedialog

import pandas as pd

from Library import error_edit_windows as err
from Scripts import base_handling as hand_base
from Scripts import constants
from Scripts import globalvars as glob
from Scripts import new_map as mp
from Scripts import new_table as tb
from Scripts import statistics as stat



# events ---------------------------------------------------------------------------------------

def close_event(pane: ttk.Panedwindow, save):
    """
    Автор: Подкопаева П.
    Цель:   закрывает открытую базу и показывает приглашение
    к открытию новой на правой стороне pane,
                save вызывается для сохранения базы, по решению пользователя
    Вход: pane - растягивающийся виджет, save - объект функции save_event из main
    Выход: нет
    """

    # открыта ли база?
    if not glob.is_db_open():
        return "break"
    # сохранена ли база?
    if not glob.is_saved():
        ans = err.yes_no("Сохранить изменения?")
        if ans:
            save()
    glob.delete_current_base()
    pane.forget(1)
    pls_select_frame = show_invitation(pane)
    pane.add(pls_select_frame, weight=9)


def remove_inf():
    """
    Автор: Подкопаева П.
    Цель: удаляет строку из таблицы
    Вход: корневое окно tkinter для создания окна редактирования, список активных столбцов таблицы
    Выход: нет
    """
    # открыта ли база?
    if not glob.is_db_open():
        return "break"
    # пуста ли база?
    if glob.current_base.empty:
        err.error("База пуста")
        return "break"
    ans = err.yes_no("Вы точно хотите удалить данные?\n Это повлечёт полное удаление данных по выбранному вулкану.")
    if ans:
        index = glob.table4base.index(glob.table4base.selection())
        glob.table4base.delete(list(glob.current_base.index)[-1])
        glob.current_base = glob.current_base.drop(index=index)
        glob.current_base.reset_index(inplace=True, drop=True)
        glob.mark_changes()
        glob.update_workspace()
        glob.update_list()


def edit_event(root: tk.Tk):
    """
    Автор: Ковязин В.
    Цель: обработчик события кнопки изменения поля таблицы, открывает окно для изменения данных
    Вход: корневое окно tkinter для создания окна редактирования
    Выход: нет
    """
    # открыта ли база?
    if not glob.is_db_open():
        return "break"
    # пуста ли база?
    if glob.current_base.empty:
        err.error("База пуста")
        return "break"
    # получаем изменяемую строчку
    index = glob.table4base.index(glob.table4base.selection())
    curr_item = glob.current_base.iloc[index, :]
    # создаем дочернее окно
    edit_win = tk.Toplevel(root)
    edit_win.resizable(0, 0)
    edit_win.title("Изменения данных поля таблицы")
    # распологаем все необходимые элементы в этих фреймах
    frame4check4labels = tk.Frame(edit_win)
    frame4check4entries = tk.Frame(edit_win)
    frame4check4button = tk.Frame(edit_win)
    list4changes = {}
    for i in constants.origin_columns:
        # все значения будут строкой
        text = tk.StringVar()
        # если атрибут nan или 0, то вместо него отображаем пустую строчку
        if pd.isna(curr_item[i]) or (i in ['Year', 'Month', 'Day'] and curr_item[i] == 0):
            text.set("")
        else:
            text.set(curr_item[i])
        list4changes[i] = text
        label = tk.Label(frame4check4labels, text=i + ":", anchor="e")
        entry = tk.Entry(frame4check4entries, textvariable=text)
        if i not in glob.columns:
            label.configure(state=tk.DISABLED)
            entry.configure(state='readonly')
        entry.pack(side="top", fill="x", expand=True, pady=5)
        label.pack(side="top", fill="x", expand=True, pady=5)
    save_changes_button = tk.Button(frame4check4button, text="Сохранить")
    save_changes_button.pack(expand=False)
    save_changes_button.bind("<Button-1>",
                             lambda *args: make_changes_event(edit_win, index, list4changes))
    edit_win.rowconfigure(0, pad=5)
    edit_win.rowconfigure(1, pad=5)
    edit_win.columnconfigure(0, pad=5)
    edit_win.columnconfigure(1, pad=5)
    frame4check4labels.grid(row=0, column=0, sticky="NSW")
    frame4check4entries.grid(row=0, column=1, sticky="NSW")
    frame4check4button.grid(row=1, column=0, columnspan=2, sticky="NSEW")


def make_changes_event(win: tk.Toplevel, index: int, new_values: dict):
    """
    Автор: Баканов Г.
    Цель: обработчик события кнопки сохранения в окне редактирования поля таблицы
    Вход: объект окна редактирования tkinter для его закрытия после нажатия кнопки сохранить,
            текущий индекс выбранного поля таблицы,
            новые значения для записи в поле таблицы.
    Выход: нет
    """
    # приводим все числа к числовому типу
    glob.current_base.iloc[index, :] = [x.get() for x in new_values.values()]
    # заменяем пустые строчки на nan и приводим тип всех столбцов таблицы к нужному типу
    glob.current_base = glob.correct_base_values(glob.current_base)
    glob.work_list[glob.current_base_name] = glob.current_base
    item = glob.table4base.selection()
    for key, value in new_values.items():
        glob.table4base.set(item, column=key, value=value.get())
    glob.mark_changes()
    glob.update_list()
    glob.update_workspace()
    win.destroy()


def uncheck_all_event(*args):
    """
    Автор: Баканов Г.
    Цель: снимает метки со всех значений columns_selection
    Вход: нет
    Выход: нет
    """
    [x.set(0) for x in glob.columns_selection.values()]


def check_all_event(*args):
    """
    Автор: Баканов Г.
    Цель: ставит метки на все значения columns_selection
    Вход: нет
    Выход: нет
    """
    [x.set(1) for x in glob.columns_selection.values()]


def apply_column_selection(root: tk.Tk, win: tk.Toplevel, pane: ttk.Panedwindow):
    """
    Автор: Баканов Г.
    Цель: применяет к программме выбор столбцов (изменяет рабочее пространство)
    Вход: главное окно, побочное окно выбора столбцов, растягивающийся виджет
    Выход: нет
    """
    if any(glob.columns_selection.values()):
        glob.columns = [x for x in glob.columns_selection.keys() if glob.columns_selection[x].get() == 1]
        open_base(root, pane, glob.current_base_list_id)
        win.destroy()
    else:
        err.error("Не выбран ни один столбец")
        return "break"


def select_columns_event(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Ковязин В.
    Цель: открывает окно для выбора столбцов, которые надо показать в программе
    Вход: главное окно, растягивающийся виджет
    Выход: нет
    """
    # открыта ли база?
    if not glob.is_db_open():
        return "break"
    win = tk.Toplevel(root)
    win.title("Выберите стобцы")
    glob.columns_selection = {k: v
                              for k in constants.origin_columns
                              for v in [tk.BooleanVar() for x in range(len(glob.constants.origin_columns))]
                              }
    frame4check = tk.Frame(win)
    frame4button = tk.Frame(win)

    i = 0
    # раставляем checkbutton'ы и устанавливаем их в активное (отмеченное)
    # положение по текущим показывающимся столбцам
    for text, value in glob.columns_selection.items():
        ttk.Checkbutton(frame4check,
                        style="Selection.TCheckbutton", text=text, variable=value, onvalue=True,
                        offvalue=False).grid(row=i, column=1, sticky='NSEW')
        value.set(True) if text in glob.columns else value.set(False)
        i += 1
    apply_button = tk.Button(frame4button, text="Применить")
    uncheck_all_button = tk.Button(frame4button, text="Снять выбор")
    check_all_button = tk.Button(frame4button, text="Выбрать все")

    apply_button.bind("<Button-1>", lambda *args: apply_column_selection(root, win, pane))
    uncheck_all_button.bind("<Button-1>", uncheck_all_event)
    check_all_button.bind("<Button-1>", check_all_event)

    uncheck_all_button.grid(row=0, column=0, sticky='NSE', padx=5, pady=2)
    check_all_button.grid(row=0, column=1, sticky='NSW', padx=5, pady=2)
    apply_button.grid(row=1, column=0, columnspan=2, sticky='NS', pady=2)
    frame4check.pack(side="top", fill="both", expand=True, padx=10, pady=5)
    frame4button.pack(side="top", fill="both", expand=True, padx=10, pady=5)


def open_base(root: tk.Tk, pane: ttk.Panedwindow, selected: int):
    """
    Автор: Баканов Г.
    Цель: открывает загруженную базу данных и
    создает для нее таблицу с полями, добавляя ее на главный экран
    Вход: объект главного окна,
            объект растягиваемого виджета,
            индекс базы в Listbox
    Выход: нет
    """

    glob.current_base_list_id = selected
    glob.current_base, glob.current_base_name = glob.work_list.get(
        glob.base_list.get(selected).replace('*', '')), glob.base_list.get(selected)
    work_frame4check = create_workspace(root, pane)
    pane.forget(1)
    pane.add(work_frame4check, weight=10000)


def workspace_onclick_event(root, event, mode: str):
    """
    Автор: Баканов Г.
    Цель: обработчик события нажатия на рабочее пространство таблицы данных
    Вход: объект главного окна,
    информация события,
    вид нажатия (одинарное, двойное)
    Выход: нет
    """
    glob.sort = not glob.sort
    tree = glob.table4base
    # одиночное нажатие по заголовку - сортировка
    if mode == "Single":
        if tree.identify_region(event.x, event.y) == "heading":
            column = tree.identify_column(event.x)
            index4column = int(column[1:])
            glob.current_base = glob.current_base.sort_values(by=glob.columns[index4column - 1],
                                                              axis=0,
                                                              ascending=glob.sort, ignore_index=True)
            glob.current_base = glob.correct_base_values(glob.current_base)
            glob.update_workspace()
    # двойное нажатие по полю - редактирование
    elif mode == "Double":
        edit_event(root)


def show_invitation(pane: ttk.Panedwindow) -> tk.Frame:
    """
    Автор: Ковязин В.
    Цель: создание фрейма с приглашением
    Вход: объект растягивающегося виджета
    Выход: фрейм с приглашением
    """
    # label приглашение к выбору
    pls_select_frame4check = tk.Frame(pane, bg=constants.style['bg'])
    lbl_select_pls = tk.Label(pls_select_frame4check,
                              text="Пожалуйста, выберите базу данных", bg=constants.style['bg'])
    lbl_select_pls.pack(expand=True, fill="both")
    return pls_select_frame4check


def show_form(root, pane, selector, form: str, save):
    """
    Автор: Подкопаева П.
    Цель: Выбор вида таблицы
    Вход: Нет
    Выход: нет
    """
    if not glob.is_db_open():
        selector.current(0)
        return
    if not glob.is_saved():
        ans = err.yes_no("Сохранить изменения?")
        if ans:
            save()
    if form == "Общий вид":
        glob.columns = constants.origin_columns
    elif form == "Вид первый":
        glob.columns = constants.first_form
    elif form == "Вид второй":
        glob.columns = constants.second_form
    elif form == "Вид третий":
        glob.columns = constants.third_form

    open_base(root, pane, glob.current_base_list_id)


def select_statistics_event(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Подкопаева П., Ковязин В.
    Цель: открывает окно для выбора данных, для которых нужно показать общую статистику
    Вход: главное окно, растягивающийся виджет
    Выход: нет
    """
    # открыта ли база?
    if not glob.is_db_open():
        return "break"

    win = tk.Toplevel(root)
    win.title("Выбор")
    win.geometry(constants.style['popup_width'] + 'x' + constants.style['popup_height'] + "+500+200")
    win.minsize(400, 600)
    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    lang = tk.StringVar()

    win.geometry("400x600+500+300")
    lbl = tk.Label(win)
    lbl.configure(bg=constants.style['bg'],
                  text="Выберите данные для общей статистики")
    lbl.place(relx=0.05, rely=0.02)

    Elevation_checkbutton = tk.Radiobutton(background,
                                           text="Высота", value="Elevation",
                                           bg=constants.style['bg'],
                                           variable=lang)
    Elevation_checkbutton.place(relx=0.25, rely=0.05)

    DEATHS_checkbutton = tk.Radiobutton(background,
                                        text="Количество смертей",
                                        value="DEATHS",
                                        variable=lang,
                                        bg=constants.style['bg'])
    DEATHS_checkbutton.place(relx=0.25, rely=0.1)

    DAMAGE_checkbutton = tk.Radiobutton(background,
                                        text="Ущерб в млн долларов",
                                        value="DAMAGE_MILLIONS_DOLLARS",
                                        variable=lang,
                                        bg=constants.style['bg'])
    DAMAGE_checkbutton.place(relx=0.25, rely=0.15)


    MISSING_checkbutton = tk.Radiobutton(background,
                                         text="Количество пропавших",
                                         value="MISSING",
                                         variable=lang,
                                         bg=constants.style['bg'])
    MISSING_checkbutton.place(relx=0.25, rely=0.2)

    INJURIES_checkbutton = tk.Radiobutton(background,
                                          text="Количество раненных",
                                          value="INJURIES",
                                          variable=lang,
                                          bg=constants.style['bg'])
    INJURIES_checkbutton.place(relx=0.25, rely=0.25)

    ttk.Separator(background, orient='horizontal').place(relx=0, rely=0.29,
                                                         relheight=0,
                                                         relwidth=1)

    Name_checkbutton = tk.Radiobutton(background,
                                      text="Имя", value="Name",
                                      bg=constants.style['bg'], variable=lang)
    Name_checkbutton.place(relx=0.25, rely=0.3)

    Location_checkbutton = tk.Radiobutton(background, text="Расположение",
                                          value="Location",
                                          variable=lang,
                                          bg=constants.style['bg'])
    Location_checkbutton.place(relx=0.25, rely=0.35)

    Country_checkbutton = tk.Radiobutton(background,
                                         text="Страна", value="Country",
                                         variable=lang,
                                         bg=constants.style['bg'])
    Country_checkbutton.place(relx=0.25, rely=0.4)

    Latitude_checkbutton = tk.Radiobutton(background,
                                          text="Широта", value="Latitude",
                                          variable=lang,
                                          bg=constants.style['bg'])
    Latitude_checkbutton.place(relx=0.25, rely=0.45)

    Longitude_checkbutton = tk.Radiobutton(background,
                                           text="Долгота", value="Longitude",
                                           variable=lang,
                                           bg=constants.style['bg'])
    Longitude_checkbutton.place(relx=0.25, rely=0.5)

    Type_checkbutton = tk.Radiobutton(background,
                                      text="Тип", value="Type",
                                      bg=constants.style['bg'], variable=lang)
    Type_checkbutton.place(relx=0.25, rely=0.55)

    VEI_checkbutton = tk.Radiobutton(background,
                                     text="Индекс взрывоопасности",
                                     value="VEI", variable=lang,
                                     bg=constants.style['bg'])
    VEI_checkbutton.place(relx=0.25, rely=0.6)

    Agent_checkbutton = tk.Radiobutton(background, text="Причина", value="Agent",
                                       variable=lang, bg=constants.style['bg'])
    Agent_checkbutton.place(relx=0.25, rely=0.65)

    TSU_checkbutton = tk.Radiobutton(background, text="Было ли цунами?", value="TSU",
                                     variable=lang, bg=constants.style['bg'])
    TSU_checkbutton.place(relx=0.25, rely=0.7)

    EQ_checkbutton = tk.Radiobutton(background,
                                    text="Было ли землетрясение?", value="EQ",
                                    variable=lang, bg=constants.style['bg'])
    EQ_checkbutton.place(relx=0.25, rely=0.75)

    apply_button = tk.Button(background, text="Выбрать",
                             font=3, bg=constants.style['apply_button'])
    apply_button.bind("<Button-1>",
                      lambda *args:
                      stat.statistics_base(root,
                                           pane,
                                           lang.get()) if lang.get() in constants.quantity_columns
                      else show_stat_report(root, lang.get()))
    apply_button.place(relx=0.5, rely=0.8, relheight=0.1, relwidth=0.25)
    background.pack(side="top", fill="both", expand=True, padx=10, pady=5)


def analysis_window_event(root: tk.Tk, pane: ttk.Panedwindow):

    """
    Автор: Ковязин В.
    Цель: Окно выбора метода анализа
    Вход: главное окно, растягивающийся виджет
    Выход: Нет
    """

    if not glob.is_db_open():
        return "break"

    win = tk.Toplevel(root)
    win.title("Выбор")
    win.geometry("400x400+500+200")

    background = tk.Frame(win, bg="#F8F8FF")
    background.place(x=0, y=0, relwidth=1, relheight=1)

    backgroundlabel = tk.Label(background, bg="#F8F8FF")
    backgroundlabel.place(relx=0.025, rely=0.025, relwidth=0.95, relheight=0.95)

    button_statistics = tk.Button(background, text='Сводная таблица', width=20,
                                  height=2, font=11, bg=constants.style['pivot_button'])
    button_statistics.bind("<Button-1>", lambda *args: tb.choice_table(root, pane))
    button_statistics.place(relx=0.25, rely=0.15, relheight=0.1, relwidth=0.5)

    button_map = tk.Button(background, bg=constants.style['map_button'],
                           text='Построение карты', font=11, width=20, height=2)
    button_map.bind("<Button-1>", lambda *args: mp.choice_map(root, pane))
    button_map.place(relx=0.25, rely=0.45, relheight=0.1, relwidth=0.5)

    button_graphics = tk.Button(background, bg=constants.style['plotsndiagrams_button'],
                                text='Построение диаграмм\n и графиков', font=11,
                                width=20, height=2)
    button_graphics.bind("<Button-1>", lambda *args: stat.graphics_choice(root, pane))
    button_graphics.place(relx=0.2, rely=0.75, relheight=0.2, relwidth=0.65)

    background.pack(side="top", fill="both", expand=True, padx=10, pady=5)


def save_report_event(table, columns, i):

    """
    Автор: Ковязин В.
    Цель: Сохранение в файл таблицы
    Вход: Таблица с данными
    Выход: Файл
    """

    data = pd.DataFrame(columns=columns)
    for index in range(i):
        data = data.append(table.set(index), ignore_index=True)
    path = filedialog.asksaveasfilename(initialdir="../Data/",
                                        filetypes=(("Database files", "*.csv"),
                                                   ("All files", "*.*")))
    if ".csv" not in path:
        path += ".csv"
    data.to_csv(path, index=False, encoding='cp1251')
    return "break"


def show_stat_report(root: tk.Tk, target: str):

    """
    Автор: Ковязин В.
    Цель: Формирование статистики по качественным переменным
    Вход: Выбранный параметр типа строка, главное окно
    Выход: Нет
    """

    win = tk.Toplevel(root)
    win.title(target)
    if target not in ['TSU', 'EQ']:
        columns = ["Атрибут " + target, "Частота", "Процент от общего числа"]
    else:
        columns = ["Было ли " + ('цунами' if target == 'TSU' else 'землетрясение'),
                   "Частота", "Процент от общего числа"]
    table = ttk.Treeview(win, height=20, show='headings', columns=columns)
    [table.heading('#' + str(x + 1), text=columns[x]) for x in range(3)]
    freq, whole = stat.stat_report(root, target)
    i = 0
    for name, number in freq.items():
        table.insert('', 'end', iid=i,
                     values=[name, number, str(round((number / whole) * 100, 2)) + '%'])
        i += 1
    vsb = ttk.Scrollbar(win, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=vsb.set)

    save_button = tk.Button(win, text='Сохранить')
    save_button.bind("<Button-1>", lambda *args: save_report_event(table, columns, i))
    vsb.pack(side='right', fill='both')
    save_button.pack(side='top')
    table.pack(side='top', fill='x')


def stat_report_event(root: tk.Tk):

    """
    Автор: Ковязин В.
    Цель: Показ статистики по качественным переменным
    Вход: главное окно
    Выход: нет
    """

    if not glob.is_db_open():
        return "break"
    win = tk.Toplevel(root)
    win.title("Статистический отчет")
    win.geometry('300x300')
    target = tk.StringVar()
    dropdown = ttk.Combobox(win, values=constants.quality_columns, state='readonly',
                            textvariable=target)
    dropdown.current(0)
    show_result = tk.Button(win, text="Показать")
    show_result.bind("<Button-1>", lambda *args: show_stat_report(root, target.get()))
    tk.Label(win, text="Атрибут").pack(side="top")
    dropdown.pack(side="top")
    show_result.pack(side="top")


#  ---------------------------------------------------------------------------------------
# frame4checks ===================================================================================


def create_toolbar(root: tk.Tk, pane: ttk.Panedwindow, load, save, create, icons: glob.Icons):
    """
    Автор: Подкопаева П., Баканов Г.
    Цель: создание панели инструментов в главном окне
    Вход: объект главного окна,
            объект растягивающегося виджета,
            объекты функций load_event, save_event, create_event
            словарь для иконок
    Выход: нет
    """

    tools_frame4check = tk.Frame(root, bg=constants.style['bg_accent'])
    add_button = tk.Button(tools_frame4check, image=icons['add_icon'], relief="groove", bd=0,
                           bg=constants.style['bg_accent'])
    save_button = tk.Button(tools_frame4check, image=icons['save_icon'], relief="groove", bd=0,
                            bg=constants.style['bg_accent'])
    edit_button = tk.Button(tools_frame4check, image=icons['edit_icon'], relief="groove", bd=0,
                            bg=constants.style['bg_accent'])
    load_button = tk.Button(tools_frame4check, image=icons['load_icon'], relief="groove", bd=0,
                            bg=constants.style['bg_accent'])
    add_field_button = tk.Button(tools_frame4check,
                                 image=icons['add_field_icon'], relief="groove", bd=0,
                                 bg=constants.style['bg_accent'])
    del_field_button = tk.Button(tools_frame4check, image=icons['del_field_icon'],
                                 relief="groove", bd=0,
                                 bg=constants.style['bg_accent'])
    select_columns = tk.Button(tools_frame4check, text="Столбцы", relief="raised", bd=2,
                               bg=constants.style['bg_accent'])
    close_button = tk.Button(tools_frame4check, image=icons['close_icon'], relief="groove", bd=0,
                             bg=constants.style['bg_accent'])
    table_normal_forms_selector = ttk.Combobox(tools_frame4check, state='readonly',
                                               values=["Общий вид",
                                                       "Вид первый", "Вид второй", "Вид третий"])

    statistics_select = tk.Button(tools_frame4check,
                                  text="Общая статистика за период наблюдений", relief="raised",
                                  bd=2, bg=constants.style['bg_accent'])
    analysis_window = tk.Button(tools_frame4check, text="Анализ данных", relief="raised", bd=2,
                                bg=constants.style['analyse_button'])

    global CHOSEN_option, GL_REQUEST

    search_data = tk.StringVar(value="Поиск")
    request = tk.Entry(tools_frame4check, textvariable=search_data, relief="raised", bd=2)
    request_menu = ttk.Combobox(tools_frame4check, state='readonly',
                                values=["Без фильтра",
                                        "По названию", "По типу", "По стране", "По цунами",
                                        "По землетрясению"])

    button_save_filter = tk.Button(tools_frame4check,
                                   relief="groove", bd=0, bg=constants.style['bg_accent'])

    analysis_window.bind("<Button-1>", lambda *args: analysis_window_event(root, pane))
    statistics_select.bind("<Button-1>", lambda *args: select_statistics_event(root, pane))

    table_normal_forms_selector.current(0)
    request_menu.current(0)
    add_button.bind("<Button-1>", create)
    save_button.bind("<Button-1>", save)
    edit_button.bind("<Button-1>", lambda *args: edit_event(root))
    load_button.bind("<Button-1>", load)
    add_field_button.bind("<Button-1>",
                          lambda *args: add_inf(root, table_normal_forms_selector.get(), save))
    del_field_button.bind("<Button-1>", lambda *args: remove_inf())
    table_normal_forms_selector.bind("<<ComboboxSelected>>",
                                     lambda event: show_form(root, pane,
                                                             table_normal_forms_selector,
                                                             table_normal_forms_selector.get(),
                                                             save))
    request_menu.bind("<<ComboboxSelected>>",
                      lambda event: search_call(root, pane, request_menu,
                                                request_menu.get(), search_data.get(),
                                                save, create))

    select_columns.bind("<Button-1>", lambda *args: select_columns_event(root, pane))
    close_button.bind("<Button-1>", lambda *args: close_event(pane, save))
    # button_save_filter.bind("<Button-1>", lambda *args: )

    add_button.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
    load_button.grid(row=0, column=1, padx=2, pady=2, sticky="NSEW")
    save_button.grid(row=0, column=2, padx=2, pady=2, sticky="NSEW")
    edit_button.grid(row=0, column=3, padx=2, pady=2, sticky="NSEW")
    add_field_button.grid(row=0, column=4, padx=2, pady=2, sticky="NSEW")
    del_field_button.grid(row=0, column=5, padx=2, pady=2, sticky="NSEW")
    table_normal_forms_selector.grid(row=0, column=6, padx=2, pady=2, sticky="NSEW")
    select_columns.grid(row=0, column=7, padx=2, pady=2, sticky="NSEW")
    close_button.grid(row=0, column=8, padx=2, pady=2, sticky="NSEW")
    button_save_filter.grid(row=0, column=18, padx=2, pady=2, sticky="NSEW")
    statistics_select.grid(row=0, column=16, padx=2, pady=2, sticky="NSEW")
    analysis_window.grid(row=2, column=16, padx=2, pady=2, sticky="NSEW")
    request.grid(row=0, column=17, padx=2, pady=2, sticky="NSEW")
    request_menu.grid(row=2, column=17, padx=2, pady=2, sticky="NSEW")
    tools_frame4check.grid_rowconfigure(0, minsize=20)
    tools_frame4check.grid(row=0, column=0, columnspan=12, sticky="NSEW")


def search_call(root: tk.Tk, pane: ttk.Panedwindow, selector, option: str,
                search_data, save, create):

    """
    Автор: Подкопаева П.
    Цель: Поиск в базе данных по ключевому слову
    Вход: Ключевое слово типа строка
    Выход: dataframe
    """

    if not glob.is_db_open():
        selector.current(0)
        return
    if not glob.is_saved():
        ans = err.yes_no("Сохранить изменения?")
        if ans:
            save()
    filter_option = ''
    if option == "Без фильтра":
        filter_option = 'all'
    elif option == "По названию":
        filter_option = 'Name'
    elif option == "По типу":
        filter_option = 'Type'
    elif option == "По стране":
        filter_option = 'Country'
    elif option == "По цунами":
        filter_option = 'TSU'
    elif option == "По землетрясению":
        filter_option = 'EQ'
    search_result = hand_base.searching(search_data, filter_option)
    if search_result.empty:
        err.warning('Ничего не найдено', True)
        return
    search_result.reset_index(inplace=True, drop=True)
    create()
    glob.work_list[glob.base_list.get(glob.base_list.size() - 1)] = search_result
    open_base(root, pane, glob.base_list.size() - 1)
    glob.mark_changes()
    save()



def create_list4db(root: tk.Tk, pane: ttk.Panedwindow) -> tk.LabelFrame:
    """
    Автор: Баканов Г.
    Цель: создание виджета Listbox для выбора базы
    Вход: объект главного окна,
            объект растягивающегося виджета
    Выход: фрейм с Listbox
    """
    list_frame4check = tk.LabelFrame(root, labelanchor='n',
                                     text='Базы данных', bd=0, padx=5, pady=5, relief=tk.RIDGE,
                                     bg='white')
    lsb_base = tk.Listbox(list_frame4check, selectmode='browse')
    for name, base in glob.work_list.items():
        lsb_base.insert(tk.END, name)
    glob.base_list = lsb_base
    lsb_base.bind('<Double-Button-1>',
                  lambda *args: open_base(root, pane, lsb_base.curselection()))
    lsb_base.pack(side="left", fill="both", expand=True)
    return list_frame4check


def create_menu(root: tk.Tk, load):
    """
    Автор: Ковязин В.
    Цель: создает меню на главном окне
    Вход: объект главного окна, объект функции load
    Выход: нет
    """
    menubar = tk.Menu(root)
    file = tk.Menu(menubar, tearoff=0)
    file.add_command(label="Load", command=load)
    file.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=file)
    root.config(menu=menubar)


def create_workspace(root: tk.Tk, pane: ttk.Panedwindow) -> tk.LabelFrame:
    """
    Автор: Ковязин В.
    Цель: создает рабочее пространство таблицы
    Вход: объект главного окна,
                объект растягивающегося виджета,
    Выход: фрейм с таблицей
    """

    # создаем и заполняем нашу таблицу
    title = glob.columns
    frame = tk.LabelFrame(pane, labelanchor='n',
                          text='Данные', bd=0, pady=5, padx=5, relief=tk.RIDGE, bg='white')
    tree = ttk.Treeview(frame, columns=title,
                        height=constants.tree_rows_number, show="headings", selectmode='browse')
    [tree.heading('#' + str(x + 1), text=title[x]) for x in range(len(title))]
    for i in list(glob.current_base.index):
        insert = list(glob.current_base[glob.columns].iloc[i, :])
        tree.insert('', 'end', iid=i, values=insert)
    # меняем ширину столбца для красоты
    for i in range(1, len(title) + 1):
        tree.column('#' + str(i), width=100, stretch=False)
    # скроллбары для нее
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.bind("<Button-1>", lambda event, mode="Single": workspace_onclick_event(root, event, mode))
    tree.bind("<Double-Button-1>", lambda event,
              mode="Double": workspace_onclick_event(root, event, mode))
    tree.configure(yscrollcommand=vsb.set)
    tree.configure(xscrollcommand=hsb.set)

    # пакуем все в фрейм, а его по сетке в окно
    glob.table4base = tree
    hsb.pack(side='bottom', fill='both')
    vsb.pack(side='right', fill='both')
    tree.pack(side='top', fill='x')

    return frame


#  =======================================================================================


def add_inf(win: tk.Tk, form: str, save):
    """
    Автор: Подкопаева П., Баканов Г.
    Цель: Добавление новых элементов в базу данных (окно)
    Вход: Нет
    Выход: Нет
    """

    if not glob.is_db_open():
        return "break"
    root = tk.Toplevel(win)
    root.title("Окно ввода данных")

    if form == "Общий вид":
        Year = tk.IntVar()
        Year_label = tk.Label(root, text="Год извержения:")
        Year_label.grid(row=0, column=0, sticky="w")
        Year_entry = tk.Entry(root, textvariable=Year)
        Year_entry.grid(row=0, column=1, padx=5, pady=5)

        cmb_month = ttk.Combobox(root)
        Month_label = tk.Label(root, text="Месяц извержения:")
        Month_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        cmb_month['values'] = ('1', '2', '3', '4', '5', '6', '7',
                               '8', '9', '10', '11', '12')
        cmb_month.current(0)
        cmb_month.grid(column=1, row=1)

        Day = tk.IntVar()
        Day_label = tk.Label(root, text="День извержения:")
        Day_label.grid(row=2, column=0, sticky="w")
        Day_entry = tk.Entry(root, textvariable=Day)
        Day_entry.grid(row=2, column=1, padx=5, pady=5)

        name = tk.StringVar()
        name_label = tk.Label(root, text="Название вулкана:")
        name_label.grid(row=3, column=0, sticky="w")
        name_entry = tk.Entry(root, textvariable=name)
        name_entry.grid(row=3, column=1, padx=5, pady=5)

        Type = tk.StringVar()
        Type_label = tk.Label(root, text="Тип вулкана:")
        Type_label.grid(row=4, column=0, sticky="w")
        Type_entry = tk.Entry(root, textvariable=Type)
        Type_entry.grid(row=4, column=1, padx=5, pady=5)

        Height = tk.IntVar()
        Height_label = tk.Label(root, text="Высота вулкана (в метрах):")
        Height_label.grid(row=5, column=0, sticky="w")
        Height_entry = tk.Entry(root, textvariable=Height)
        Height_entry.grid(row=5, column=1, padx=5, pady=5)

        country = tk.StringVar()
        country_label = tk.Label(root, text="Страна:")
        country_label.grid(row=6, column=0, sticky="w")
        country_entry = tk.Entry(root, textvariable=country)
        country_entry.grid(row=6, column=1, padx=5, pady=5)

        location = tk.StringVar()
        location_label = tk.Label(root, text="Расположение вулкана:")
        location_label.grid(row=7, column=0, sticky="w")
        location_entry = tk.Entry(root, textvariable=location)
        location_entry.grid(row=7, column=1, padx=5, pady=5)

        Latitude = tk.IntVar()
        Latitude_label = tk.Label(root, text="Широта:")
        Latitude_label.grid(row=8, column=0, sticky="w")
        Latitude_entry = tk.Entry(root, textvariable=Latitude)
        Latitude_entry.grid(row=8, column=1, padx=5, pady=5)

        Longtitude = tk.IntVar()
        Longtitude_label = tk.Label(root, text="Долгота:")
        Longtitude_label.grid(row=9, column=0, sticky="w")
        Longtitude_entry = tk.Entry(root, textvariable=Longtitude)
        Longtitude_entry.grid(row=9, column=1, padx=5, pady=5)

        cmb_VEI = ttk.Combobox(root)
        VEI_label = tk.Label(root, text="Индекс взрывоопасности:")
        VEI_label.grid(row=10, column=0, sticky="w", padx=5, pady=5)
        cmb_VEI['values'] = ('0', '1', '2', '3', '4', '5', '6', '7', '8')
        cmb_VEI.current(0)
        cmb_VEI.grid(column=1, row=10)

        cmb_agent = ttk.Combobox(root)
        Agent_label = tk.Label(root, text="Причина извержения:")
        Agent_label.grid(row=10, column=3, sticky="w", padx=5, pady=5)
        cmb_agent['values'] = ('A', 'E', 'F', 'G', 'I', 'L', 'M', 'm', 'P', 'S', 'T', 'W')
        cmb_agent.current(0)
        cmb_agent.grid(column=4, row=10)

        Deaths = tk.IntVar()
        Deaths_label = tk.Label(root, text="Количество смертей:")
        Deaths_label.grid(row=13, column=0, sticky="w")
        Deaths_entry = tk.Entry(root, textvariable=Deaths)
        Deaths_entry.grid(row=13, column=1, padx=5, pady=5)

        Injured = tk.IntVar()
        Injured_label = tk.Label(root, text="Количество пострадавших:")
        Injured_label.grid(row=14, column=0, sticky="w")
        Injured_entry = tk.Entry(root, textvariable=Injured)
        Injured_entry.grid(row=14, column=1, padx=5, pady=5)

        Lost = tk.IntVar()
        Lost_label = tk.Label(root, text="Количество пропавших:")
        Lost_label.grid(row=15, column=0, sticky="w")
        Lost_entry = tk.Entry(root, textvariable=Lost)
        Lost_entry.grid(row=15, column=1, padx=5, pady=5)

        Damage = tk.IntVar()
        Damage_label = tk.Label(root, text="Ущерб в млн долларов:")
        Damage_label.grid(row=16, column=0, sticky="w")
        Damage_entry = tk.Entry(root, textvariable=Damage)
        Damage_entry.grid(row=16, column=1, padx=5, pady=5)

        TSU = tk.BooleanVar()
        TSU.set(False)
        TSU1 = ttk.Checkbutton(root, text="Было цунами?", var=TSU)
        TSU1.grid(column=0, row=17)

        EQ = tk.BooleanVar()
        EQ.set(False)
        EQ1 = ttk.Checkbutton(root, text="Было землетрясение?", var=EQ)
        EQ1.grid(column=2, row=17)

        list4values = {'Year': Year, 'Month': cmb_month,
                       'Day': Day, 'Name': name, 'Location': location,
                       'Country': country,
                       'Latitude': Latitude, 'Longitude': Longtitude,
                       'Elevation': Height, 'Type': Type, 'VEI': cmb_VEI,
                       'Agent': cmb_agent, 'DEATHS': Deaths, 'INJURIES': Injured, 'MISSING': Lost,
                       'DAMAGE_MILLIONS_DOLLARS': Damage, 'TSU': TSU, 'EQ': EQ}
        message_button = tk.Button(root, text="Ввести",
                                   command=lambda *args: accept(root, list4values))
        message_button.grid(row=19, column=3, padx=5, pady=5, sticky="e")

    elif form == "Вид первый":

        name = tk.StringVar()
        name_label = tk.Label(root, text="Название вулкана:")
        name_label.grid(row=1, column=0, sticky="w")
        name_entry = tk.Entry(root, textvariable=name)
        name_entry.grid(row=1, column=1, padx=5, pady=5)

        Type = tk.StringVar()
        Type_label = tk.Label(root, text="Тип вулкана:")
        Type_label.grid(row=2, column=0, sticky="w")
        Type_entry = tk.Entry(root, textvariable=Type)
        Type_entry.grid(row=2, column=1, padx=5, pady=5)

        Height = tk.IntVar()
        Height_label = tk.Label(root, text="Высота вулкана (в метрах):")
        Height_label.grid(row=3, column=0, sticky="w")
        Height_entry = tk.Entry(root, textvariable=Height)
        Height_entry.grid(row=3, column=1, padx=5, pady=5)

        Latitude = tk.IntVar()
        Latitude_label = tk.Label(root, text="Широта:")
        Latitude_label.grid(row=4, column=0, sticky="w")
        Latitude_entry = tk.Entry(root, textvariable=Latitude)
        Latitude_entry.grid(row=4, column=1, padx=5, pady=5)

        Longtitude = tk.IntVar()
        Longtitude_label = tk.Label(root, text="Долгота:")
        Longtitude_label.grid(row=5, column=0, sticky="w")
        Longtitude_entry = tk.Entry(root, textvariable=Longtitude)
        Longtitude_entry.grid(row=5, column=1, padx=5, pady=5)

        list4values = {'Name': name, 'Latitude': Latitude,
                       'Longitude': Longtitude, 'Elevation': Height, 'Type': Type}
        message_button = tk.Button(root, text="Ввести",
                                   command=lambda *args: accept(root, list4values))
        message_button.grid(row=7, column=3, padx=5, pady=5, sticky="e")

    elif form == "Вид второй":

        country = tk.StringVar()
        country_label = tk.Label(root, text="Страна:")
        country_label.grid(row=1, column=0, sticky="w")
        country_entry = tk.Entry(root, textvariable=country)
        country_entry.grid(row=1, column=1, padx=5, pady=5)

        location = tk.StringVar()
        location_label = tk.Label(root, text="Расположение вулкана:")
        location_label.grid(row=2, column=0, sticky="w")
        location_entry = tk.Entry(root, textvariable=location)
        location_entry.grid(row=2, column=1, padx=5, pady=5)

        Latitude = tk.IntVar()
        Latitude_label = tk.Label(root, text="Широта:")
        Latitude_label.grid(row=3, column=0, sticky="w")
        Latitude_entry = tk.Entry(root, textvariable=Latitude)
        Latitude_entry.grid(row=3, column=1, padx=5, pady=5)

        Longtitude = tk.IntVar()
        Longtitude_label = tk.Label(root, text="Долгота:")
        Longtitude_label.grid(row=4, column=0, sticky="w")
        Longtitude_entry = tk.Entry(root, textvariable=Longtitude)
        Longtitude_entry.grid(row=4, column=1, padx=5, pady=5)

        list4values = {'Location': location, 'Country': country,
                       'Latitude': Latitude, 'Longitude': Longtitude}
        message_button = tk.Button(root, text="Ввести",
                                   command=lambda *args: accept(root, list4values))
        message_button.grid(row=6, column=3, padx=5, pady=5, sticky="e")

    elif form == "Вид третий":

        Year = tk.IntVar()
        Year_label = tk.Label(root, text="Год извержения:")
        Year_label.grid(row=0, column=0, sticky="w")
        Year_entry = tk.Entry(root, textvariable=Year)
        Year_entry.grid(row=0, column=1, padx=5, pady=5)

        cmb_month = ttk.Combobox(root)
        Month_label = tk.Label(root, text="Месяц извержения:")
        Month_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        cmb_month['values'] = ('1', '2', '3', '4', '5', '6', '7',
                               '8', '9', '10', '11', '12')
        cmb_month.current(0)
        cmb_month.grid(column=1, row=1)

        Day = tk.IntVar()
        Day_label = tk.Label(root, text="День извержения:")
        Day_label.grid(row=2, column=0, sticky="w")
        Day_entry = tk.Entry(root, textvariable=Day)
        Day_entry.grid(row=2, column=1, padx=5, pady=5)

        name = tk.StringVar()
        name_label = tk.Label(root, text="Название вулкана:")
        name_label.grid(row=3, column=0, sticky="w")
        name_entry = tk.Entry(root, textvariable=name)
        name_entry.grid(row=3, column=1, padx=5, pady=5)

        cmb_VEI = ttk.Combobox(root)
        VEI_label = tk.Label(root, text="Индекс взрывоопасности:")
        VEI_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        cmb_VEI['values'] = ('0', '1', '2', '3', '4', '5', '6', '7', '8')
        cmb_VEI.current(0)
        cmb_VEI.grid(column=1, row=4)

        cmb_agent = ttk.Combobox(root)
        Agent_label = tk.Label(root, text="Причина извержения:")
        Agent_label.grid(row=4, column=3, sticky="w", padx=5, pady=5)
        cmb_agent['values'] = ('A', 'E', 'F', 'G', 'I', 'L', 'M', 'm', 'P', 'S', 'T', 'W')
        cmb_agent.current(0)
        cmb_agent.grid(column=4, row=4)

        Deaths = tk.IntVar()
        Deaths_label = tk.Label(root, text="Количество смертей:")
        Deaths_label.grid(row=5, column=0, sticky="w")
        Deaths_entry = tk.Entry(root, textvariable=Deaths)
        Deaths_entry.grid(row=5, column=1, padx=5, pady=5)

        Injured = tk.IntVar()
        Injured_label = tk.Label(root, text="Количество пострадавших:")
        Injured_label.grid(row=6, column=0, sticky="w")
        Injured_entry = tk.Entry(root, textvariable=Injured)
        Injured_entry.grid(row=6, column=1, padx=5, pady=5)

        Lost = tk.IntVar()
        Lost_label = tk.Label(root, text="Количество пропавших:")
        Lost_label.grid(row=7, column=0, sticky="w")
        Lost_entry = tk.Entry(root, textvariable=Lost)
        Lost_entry.grid(row=7, column=1, padx=5, pady=5)

        Damage = tk.IntVar()
        Damage_label = tk.Label(root, text="Ущерб в млн долларов:")
        Damage_label.grid(row=8, column=0, sticky="w")
        Damage_entry = tk.Entry(root, textvariable=Damage)
        Damage_entry.grid(row=8, column=1, padx=5, pady=5)

        TSU = tk.BooleanVar()
        TSU.set(False)
        TSU1 = ttk.Checkbutton(root, text="Было цунами?", var=TSU)
        TSU1.grid(column=0, row=9)

        EQ = tk.BooleanVar()
        EQ.set(False)
        EQ1 = ttk.Checkbutton(root, text="Было землетрясение?", var=EQ)
        EQ1.grid(column=2, row=9)

        list4values = {'Year': Year, 'Month': cmb_month, 'Day': Day, 'Name': name, 'VEI': cmb_VEI,
                       'Agent': cmb_agent, 'DEATHS': Deaths, 'INJURIES': Injured, 'MISSING': Lost,
                       'DAMAGE_MILLIONS_DOLLARS': Damage, 'TSU': TSU, 'EQ': EQ}

        message_button = tk.Button(root, text="Ввести",
                                   command=lambda *args: accept(root, list4values))
        message_button.grid(row=11, column=3, padx=5, pady=5, sticky="e")


def accept(root, list4values):

    """
    Автор: Баканов Г., Подкопаева П.
    Цель: Проверка правильности введённых данных в окно
    Вход: Значение переменной любого типа
    Выход: нет
    """

    flag = True
    if (list4values['Day'].get() > 29) and (list4values['Month'].get() == 2):
        flag = False
    elif list4values['Day'].get() > 31 or list4values['Day'].get() < 1:
        flag = False
    if list4values['Elevation'].get() > 6887:
        flag = False
    if (list4values['Latitude'].get() > 180) or (list4values['Latitude'].get() < -180):
        flag = False
    if (list4values['Longitude'].get() > 180) or (list4values['Longitude'].get() < -180):
        flag = False
    if flag:

        glob.current_base = glob.current_base.append({k: v.get() for k,
                                                      v in list4values.items()}, ignore_index=True)
        glob.current_base = glob.correct_base_values(glob.current_base)
        glob.work_list[glob.current_base_name] = glob.current_base
        new_item = glob.table4base.insert('', 'end', iid=len(glob.current_base.index) - 1)
        for i in glob.columns:
            glob.table4base.set(new_item, column=i, value=list4values[i].get())
        mb.showinfo("Сообщение", "Занесено в базу")
        glob.mark_changes()
        glob.update_list()
        root.destroy()
    else:
        err.error("Данные введены некорректно, повторите попытку")
