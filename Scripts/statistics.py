"""
Цель: Модуль, содержащий функции для статистического анализа баз данных
"""
import math as m
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb, filedialog

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Scripts import base_handling as hand_base
from Scripts import globalvars as glob
from Scripts import new_table as tb
from Scripts import constants


def statistics_base(root: tk.Toplevel, pane: ttk.Panedwindow, string):
    """
    Автор: Баканов Г.
    Цель: Формирует и сохраняет отчёт по основным статистикам для количественных переменных
    Вход: dataframe
    Выход: Нет (файл)
    """

    win = tk.Toplevel(root, bg=constants.style['bg'])
    win.title("Статистические данные: " + string)
    win.geometry('600x400+500+300')


    bd = glob.current_base
    sortedSample = bd[string].sort_values()[bd[string] == bd[string]]  # get rid of nan
    average = m.ceil(sortedSample.mean())
    med = sortedSample.median()
    mode = sortedSample.mode().values[0]
    if average == med:
        s = 'симметрия'
    elif average > med:
        s = 'acимметрия вправо'
    else:
        s = 'acимметрия влево'
    disp = (sortedSample.apply(lambda x: (x - average) ** 2).sum()) / (len(sortedSample) - 1)

    tree = ttk.Treeview(win, height=20, show='headings')
    tree["columns"] = ("one", "two")
    tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
    tree.column("one", width=300, minwidth=300, stretch=tk.NO)
    tree.column("two", width=300, minwidth=300, stretch=tk.NO)

    i = 0

    tree.heading("#0", anchor=tk.W)
    tree.heading("one", text="Характеристика", anchor=tk.W)
    tree.heading("two", text="Значение", anchor=tk.W)
    tree.insert('', tk.END, iid=i, values=["Среднее арифметическое", average])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Медиана", med])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Мода", mode])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Форма плотности распределения", s])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Выборочная дисперсия", disp])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Нижняя квартиль", sortedSample.quantile(0.25)])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Верхняя квартиль", sortedSample.quantile(0.75)])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Межквартильный размах",
                                           sortedSample.quantile(0.75) - sortedSample.quantile(0.25)])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Максимум", sortedSample.max()])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Минимум", sortedSample.min()])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Размах", (sortedSample.max() - sortedSample.min())])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Стандартное отклонение (СКО)", sortedSample.std()])
    i += 1
    tree.insert('', tk.END, iid=i, values=["Коэффициент вариации",
                                           sortedSample.std() / sortedSample.mean()])

    vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='both')
    save_button = tk.Button(win, text='Сохранить', bg=constants.style['apply_button'])
    save_button.bind("<Button-1>", lambda *args: save_stat(tree, i))
    save_button.pack(side='top')
    tree.pack(side=tk.TOP, fill=tk.X)


def save_stat(tree, i):
    """
    Автор: Баканов Г.
    Цель: Функция сохраниения статистического отчёта в файл
    Вход: Статистический отчёт (tree)
    Выход: нет (файл)
    """

    data = pd.DataFrame()
    for index in range(i):
        data = data.append(tree.set(index), ignore_index=True)
    path = filedialog.asksaveasfilename(initialdir="../Output/",
                                        filetypes=(("Database files", "*.csv"),
                                                   ("All files", "*.*")))
    if ".csv" not in path:
        path += ".csv"
    data.to_csv(path, index=False, encoding='cp1251')
    return "break"


def graphics_choice(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Подкопаева П.
    Цель: Выбор фильтров для построения графического отчёта
    Вход: главное окно, растягивающийся виджет
    Выход: нет
    """

    global CHOSEN_VALUE1, CHOSEN_VALUE2, CHOSEN_VALUE3, CHOSEN_VALUE4, CHOSEN_VALUE5, CHOSEN_VALUE6


    if not glob.is_db_open():
        return "break"

    win = tk.Toplevel(root)
    win.title("Выбор")
    win.geometry("700x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    choice_graph = ("Фильтры для линейного графика", "Год - Средняя смертность")

    CHOSEN_VALUE1 = tk.StringVar(value='Фильтры для линейного графика')
    make_gr = tk.OptionMenu(background, CHOSEN_VALUE1, *choice_graph)
    make_gr.place(relx=0.1, rely=0.1)
    make_gr.pack()
    button_graph = tk.Button(background,
                             text='Построить график',
                             bg=constants.style['plots_button'])

    button_graph.bind("<Button-1>", lambda *args: draw_graph(root, pane))
    button_graph.place(relx=0.0, rely=0.5, relheight=0.1, relwidth=0.2)

    choice_diagram = (
        "Фильтры для столбчатой диаграммы",
        "Страна - Средняя смертность",
        "Страна - Средняя высота вулкана",
        "Расположение - Средняя смертность",
        "Тип вулкана - Средняя смертность",
        "Тип вулкана - Количество пропавших")

    CHOSEN_VALUE2 = tk.StringVar(value='Фильтры для столбчатой диаграммы')
    make_dgrm = tk.OptionMenu(background, CHOSEN_VALUE2, *choice_diagram)
    make_dgrm.place(relx=0.3, rely=0.1)
    make_dgrm.pack()

    button_diagram = tk.Button(background,
                               text='Построить диаграмму',
                               bg=constants.style['plots_button'])

    button_diagram.bind("<Button-1>", lambda *args: draw_diagram(root, pane))
    button_diagram.place(relx=0.4, rely=0.5, relheight=0.1, relwidth=0.2)

    choice_pie = (
        "Фильтры для круговой диаграммы",
        "Страна - Средняя смертность",
        "Тип - Средняя смертность", "Тип - Ранения")

    CHOSEN_VALUE3 = tk.StringVar(value='Фильтры для круговой диаграммы')
    make_pie = tk.OptionMenu(background, CHOSEN_VALUE3, *choice_pie)
    make_pie.place(relx=0.5, rely=0.1)
    make_pie.pack()

    button_pie = tk.Button(background, text='Построить "пирог"', bg=constants.style['plots_button'])

    button_pie.bind("<Button-1>", lambda *args: draw_pie(root, pane))
    button_pie.place(relx=0.8, rely=0.5, relheight=0.1, relwidth=0.2)

    choice_viskers = ("Фильтры для диаграммы Бокса-Вискера", "Высота - Тип")

    CHOSEN_VALUE4 = tk.StringVar(value='Фильтры для диаграммы Бокса-Вискера')
    make_box = tk.OptionMenu(background, CHOSEN_VALUE4, *choice_viskers)
    make_box.place(relx=0.7, rely=0.1)
    make_box.pack()

    button_box = tk.Button(background,
                           text='Построить \n "Бокса-Вискера"',
                           bg=constants.style['plots_button'])

    button_box.bind("<Button-1>", lambda *args: draw_box(root, pane))
    button_box.place(relx=0.0, rely=0.7, relheight=0.1, relwidth=0.2)

    choice_scatter = (
        "Фильтры для диаграммы рассеяния",
        "Высота - Смерти - Индекс взрывоопасности", "Высота - Смерти - Тип")
    CHOSEN_VALUE5 = tk.StringVar(value='Фильтры для диаграммы рассеяния')
    make_scatter = tk.OptionMenu(background, CHOSEN_VALUE5, *choice_scatter)
    make_scatter.place(relx=0.7, rely=0.1)
    make_scatter.pack()

    button_scatter = tk.Button(background,
                               text='Построить \n диаграмму \n рассеяния',
                               bg=constants.style['plots_button'])

    button_scatter.bind("<Button-1>", lambda *args: draw_scatter(root, pane))
    button_scatter.place(relx=0.4, rely=0.7, relheight=0.1, relwidth=0.2)

    choice_hist = ("Фильтры для гистограммы", "Высота - Количество смертей", "Высота - Ущерб")
    CHOSEN_VALUE6 = tk.StringVar(value='Фильтры для гистограммы')
    make_hist = tk.OptionMenu(background, CHOSEN_VALUE6, *choice_hist)
    make_hist.place(relx=0.8, rely=0.1)
    make_hist.pack()

    button_scatter = tk.Button(background,
                               text='Построить гистограмму', bg=constants.style['plots_button'])

    button_scatter.bind("<Button-1>", lambda *args: draw_hist(root, pane))
    button_scatter.place(relx=0.8, rely=0.7, relheight=0.1, relwidth=0.2)

    background.pack(side="top", fill="both", expand=True, padx=2, pady=3)


def draw_graph(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Ковязин В. 
    Цель: Функция для построения линейного графика
    Вход: главное окно, растягивающийся виджет
    Выход: Нет (файл)
    """

    global CHOSEN_VALUE1

    win = tk.Toplevel(root)
    win.title("График")
    win.geometry("600x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    name_lab = tk.Label(background, text='График\n' + CHOSEN_VALUE1.get(), bg=constants.style['bg'])
    name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

    if CHOSEN_VALUE1.get() == 'Фильтры для линейного графика':
        mb.showerror("Ошибка!", "Сначала выберите фильтр! (графики)")
        win.destroy()

    elif CHOSEN_VALUE1.get() == 'Год - Средняя смертность':

        fig = plt.Figure(figsize=(7, 5), dpi=100)
        ax1 = fig.add_subplot(1, 1, 1)
        # win.fillna(0)
        hand_base.bd = hand_base.bd.fillna(0)
        graph = FigureCanvasTkAgg(fig, background)
        graph.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)

        df1 = hand_base.bd[["Year", "DEATHS"]].groupby("Year").mean()
        df1.plot(kind='line', legend=True,
                 ax=ax1, color='r', title="График \n Год-Средняя смертность")

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/year_deaths_graph.png'))

        def save(string):
            """
            Автор: Ковязин В.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)



def draw_diagram(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Баканов Г.
    Цель: Функция для построения столбчатой диаграмммы
    Вход: главное окно, растягивающийся виджет
    Выход: Нет (файл)
    """

    global CHOSEN_VALUE2

    win = tk.Toplevel(root)
    win.title("Диаграммы")
    win.geometry("600x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    name_lab = tk.Label(background,
                        text='Диаграмма\n' + CHOSEN_VALUE2.get(),
                        bg=constants.style['bg'])
    name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

    if CHOSEN_VALUE2.get() == 'Фильтры для столбчатой диаграммы':
        mb.showerror("Ошибка!", "Сначала выберите фильтр (столбчатые диаграммы)!")
        win.destroy()

    elif CHOSEN_VALUE2.get() == 'Тип вулкана - Средняя смертность':

        bd = tb.type_deaths_mean()
        fig = plt.figure(figsize=(7, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Тип вулкана -\n Средняя смертность')
        # fig.set_figwidth(3)
        bd.plot(kind='bar', ax=ax, y='Средняя смертность', x='Type', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = plt.NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/type_deaths_bar.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)



    elif CHOSEN_VALUE2.get() == 'Страна - Средняя смертность':

        bd = tb.country_deaths_mean()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Страна -\n Средняя смертность')
        bd.plot(kind='bar', ax=ax, y='Средняя смертность', x='Country', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/country_deaths_bar.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

    elif CHOSEN_VALUE2.get() == 'Страна - Средняя высота вулкана':

        bd = tb.country_elevation_mean()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Страна -\n Средняя высота вулкана')
        bd.plot(kind='bar', ax=ax, y='Средняя высота вулкана', x='Country', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/country_elevation_bar.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)


    elif CHOSEN_VALUE2.get() == 'Расположение - Средняя смертность':

        bd = tb.location_deaths_mean()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Расположение -\n Средняя смертность')
        bd.plot(kind='bar', ax=ax, y='Средняя смертность', x='Location', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/location_deaths_bar.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

    elif CHOSEN_VALUE2.get() == 'Тип вулкана - Количество пропавших':

        bd = tb.type_missing_num()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Тип вулкана -\n Количество пострадавших')
        bd.plot(kind='bar', ax=ax, y='Количество известных пропавших', x='Type', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/type_missing_bar.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)


def elevation_type():
    """
    Автор: Подкопаева П.
    Цель: Создание dataframe по фильтрам
    Вход: нет
    Выход: dataframe
    """

    General = pd.DataFrame(hand_base.bd)
    General['Elevation'] = General['Elevation'].apply(pd.to_numeric, errors='coerce')

    rat = General.groupby(['Type']).agg({'Elevation': "mean"})

    rat.rename(columns={'Type': 'Тип вулкана', 'Elevation': 'Высота вулкана'}, inplace=True)
    rat = rat.reset_index()
    rat = rat.round({'Elevation': 2})
    # print(rat.fillna(0))
    return rat.fillna(0)


def draw_box(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Подкопаева П., Баканов Г.
    Цель: Построение диаграммы размаха Бокса-Вискера
    Вход: главное окно, растягивающийся виджет
    Выход: нет (файл)
    """
    global CHOSEN_VALUE4
    win = tk.Toplevel(root)
    win.title("Диаграммы размаха (Бокса-Вискера)")
    win.geometry("600x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    name_lab = tk.Label(background,
                        text='Диаграмма размаха\n' + CHOSEN_VALUE4.get(),
                        bg=constants.style['bg'])
    name_lab.place(relx=0.01, rely=0.01, relwidth=2, relheight=0.1)

    if CHOSEN_VALUE4.get() == 'Фильтры для диаграммы Бокса-Вискера':
        mb.showerror("Ошибка!", "Сначала выберите фильтр для диаграммы Бокса-Вискера!")
        win.destroy()

    elif CHOSEN_VALUE4.get() == 'Высота - Тип':

        type1 = hand_base.bd.loc[hand_base.bd['Type'] == 'Stratovolcano', 'Elevation'].values
        type2 = hand_base.bd.loc[hand_base.bd['Type'] == 'Shield volcano', 'Elevation'].values
        type3 = hand_base.bd.loc[hand_base.bd['Type'] == 'Caldera', 'Elevation'].values
        type4 = hand_base.bd.loc[hand_base.bd['Type'] == 'Pyroclastic shield', 'Elevation'].values
        type5 = hand_base.bd.loc[hand_base.bd['Type'] == 'Submarine volcano', 'Elevation'].values
        type6 = hand_base.bd.loc[hand_base.bd['Type'] == 'Complex volcano', 'Elevation'].values
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Высота - Тип')
        ax.boxplot([type1, type2, type3, type4, type5, type6],
                   labels=['Stratovolcano', 'Shield \n volcano', 'Caldera', 'Pyroclastic \n shield',
                           'Submarine \n volcano', 'Complex \n volcano'])

        # тут вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/type_elevation_box.png'))

        def save(string):
            """
            Автор: Подкопаева П.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")
        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

def draw_pie(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Ковязин В., Подкопаева П.
    Цель: Построение круговой диаграммы
    Вход: главное окно, растягивающийся виджет
    Выход: нет (файл)
    """
    global CHOSEN_VALUE3

    win = tk.Toplevel(root)
    win.title("Круговая диаграмма")
    win.geometry("600x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)

    name_lab = tk.Label(background,
                        text='Круговая диаграмма\n' + CHOSEN_VALUE3.get(),
                        bg=constants.style['bg'])
    name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

    if CHOSEN_VALUE3.get() == 'Фильтры для круговой диаграммы':
        mb.showerror("Ошибка!", "Сначала выберите фильтр для круговой диаграммы!")
        win.destroy()

    elif CHOSEN_VALUE3.get() == 'Тип - Средняя смертность':

        dictionary = {}
        dictionary['others'] = 0
        for x in set(hand_base.bd.Type):
            deaths = hand_base.bd['DEATHS'][hand_base.bd['Type'] == x].mean()
            if deaths > 200:
                dictionary[x] = deaths
            else:
                dictionary['others'] = deaths

        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Тип - Средняя смертность')
        ax.pie(dictionary.values(), labels=dictionary.keys(), autopct='%1.1f%%')


        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/type_deaths_pie.png'))

        def save(string):
            """
            Автор: Ковязин В.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

    elif CHOSEN_VALUE3.get() == 'Страна - Средняя смертность':

        dictionary = {}
        dictionary['others'] = 0
        for x in set(hand_base.bd.Country):
            deaths = hand_base.bd['DEATHS'].fillna(0)[hand_base.bd['Country'] == x].mean()
            if deaths > 500:
                dictionary[x] = deaths
            else:
                dictionary['others'] = deaths

        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Страна - Средняя смертность')
        ax.pie(dictionary.values(), labels=dictionary.keys(), autopct='%1.1f%%')

        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/country_deaths_pie.png'))

        def save(string):
            """
            Автор: Подкопаева П.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

    elif CHOSEN_VALUE3.get() == 'Тип - Ранения':

        dictionary = {}
        dictionary['others'] = 0
        for x in set(hand_base.bd.Type):
            deaths = hand_base.bd['INJURIES'][hand_base.bd['Type'] == x].sum()
            if deaths > 200:
                dictionary[x] = deaths

        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Тип - Ранения')
        ax.pie(dictionary.values(), labels=dictionary.keys(), autopct='%1.1f%%')

        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/type_injuries_pie.png'))

        def save(string):
            """
            Автор: Ковязин В. 
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)


def draw_scatter(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Баканов Г., Подкопаева П.
    Цель: Построение диаграммы рассеяния
    Вход: главное окно, растягивающийся виджет
    Выход: нет
    """

    global CHOSEN_VALUE5
    if CHOSEN_VALUE5.get() == 'Фильтры для диаграммы рассеяния':
        mb.showerror("Ошибка!", "Сначала выберите фильтр для диаграммы рассеяния")

    elif CHOSEN_VALUE5.get() == 'Высота - Смерти - Индекс взрывоопасности':

        win = tk.Toplevel(root)
        win.title("Диаграммы рассеяния")
        win.geometry("600x500+500+200")

        background = tk.Frame(win, bg=constants.style['bg'])
        background.place(x=0, y=0, relwidth=1, relheight=1)

        name_lab = tk.Label(background,
                            text='Диаграмма рассеяния\n' + CHOSEN_VALUE5.get(),
                            bg=constants.style['bg'])
        name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Высота - Смерти - Индекс \n взрывоопасности')
        flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = flag7 = flag8 = False

        for n in range(0, 808):
            if (hand_base.bd['VEI'][n] == 7.0) and (flag1 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='red', label="7.0")
                flag1 = True

            elif hand_base.bd['VEI'][n] == 7.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='red')

            elif hand_base.bd['VEI'][n] == 6.0 and (flag2 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='blue', label="6.0")
                flag2 = True

            elif hand_base.bd['VEI'][n] == 6.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='blue')

            elif hand_base.bd['VEI'][n] == 5.0 and (flag3 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='green', label="5.0")
                flag3 = True

            elif hand_base.bd['VEI'][n] == 5.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='green')

            elif hand_base.bd['VEI'][n] == 4.0 and (flag4 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#FF69B4', label="4.0")
                flag4 = True

            elif hand_base.bd['VEI'][n] == 4.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#FF69B4')


            elif hand_base.bd['VEI'][n] == 3.0 and flag5 is False:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#00FFFF', label="3.0")
                flag5 = True

            elif hand_base.bd['VEI'][n] == 3.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#00FFFF')

            elif hand_base.bd['VEI'][n] == 2.0 and flag6 is False:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#FF7F50', label="2.0")
                flag6 = True

            elif hand_base.bd['VEI'][n] == 2.0:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#FF7F50')

            elif hand_base.bd['VEI'][n] == 1.0 and flag7 is False:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#7B68EE', label="1.0")
                flag7 = True
            elif hand_base.bd['VEI'][n] == 1.0 and flag7:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#7B68EE')

            elif flag8 is False:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#008080', label="Others")
                flag8 = True
            else:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#008080')

        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        ax.legend(loc="upper right", title="", frameon=True)
        ax.set_xlabel('Высота')
        ax.set_ylabel('Количество смертей')

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>",
                         lambda *args: save('../Graphics/type_deaths_elevation_scat.png'))

        def save(string):
            """
            Автор: Подкопаева П.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)


    elif CHOSEN_VALUE5.get() == 'Высота - Смерти - Тип':

        win = tk.Toplevel(root)
        win.title("Диаграммы рассеяния")
        win.geometry("600x500+500+200")

        background = tk.Frame(win, bg=constants.style['bg'])
        background.place(x=0, y=0, relwidth=1, relheight=1)

        name_lab = tk.Label(background,
                            text='Диаграмма рассеяния\n' + CHOSEN_VALUE5.get(),
                            bg=constants.style['bg'])
        name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Высота - Смерти - Тип')

        flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = flag7 = flag8 = False

        for n in range(0, 808):
            if (hand_base.bd['Type'][n] == 'Shield volcano') and (flag1 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='red', label="Shield volcano")
                flag1 = True

            elif hand_base.bd['Type'][n] == 'Shield volcano':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='red')

            elif (hand_base.bd['Type'][n] == 'Caldera') and (flag2 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='blue', label="Caldera")
                flag2 = True

            elif hand_base.bd['Type'][n] == 'Caldera':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='blue')

            elif (hand_base.bd['Type'][n] == 'Maar') and (flag3 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='green', label="Maar")
                flag3 = True

            elif hand_base.bd['Type'][n] == 'Maar':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='green')

            elif (hand_base.bd['Type'][n] == 'Lava dome') and (flag4 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#FF69B4', label="Lava dome")
                flag4 = True

            elif hand_base.bd['Type'][n] == 'Lava dome':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#FF69B4')

            elif (hand_base.bd['Type'][n] == 'Pyroclastic shield') and (flag5 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#00FFFF', label="Pyroclastic shield")
                flag5 = True

            elif hand_base.bd['Type'][n] == 'Pyroclastic shield':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#00FFFF')

            elif (hand_base.bd['Type'][n] == 'Subglacial volcano') and (flag6 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#FF7F50', label="Subglacial volcano")
                flag6 = True

            elif hand_base.bd['Type'][n] == 'Subglacial volcano':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#FF7F50')

            elif (hand_base.bd['Type'][n] == 'Complex volcano') and (flag7 is False):
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#7B68EE', label="Complex volcano")
                flag7 = True

            elif hand_base.bd['Type'][n] == 'Complex volcano':
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#7B68EE')

            elif flag8 is False:
                ax.scatter(hand_base.bd['Elevation'][n],
                           hand_base.bd['DEATHS'][n], color='#008080', label='Others')
                flag8 = True
            else:
                ax.scatter(hand_base.bd['Elevation'][n], hand_base.bd['DEATHS'][n], color='#008080')

        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        ax.legend(loc="upper right", title="", frameon=True)
        ax.set_xlabel('Высота')
        ax.set_ylabel('Количество смертей')

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>",
                         lambda *args: save('../Graphics/type_deaths_elevation_scat.png'))

        def save(string):
            """
            Автор: Баканов Г.
            Цель: Сохранение в файл
            Вход: Путь формата строка
            Выход: нет
            """
            fig.savefig(string)
            mb.showinfo("Инфо!", "Картинка сохранена")

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)


def elevation_deaths():
    """
    Автор: Баканов Г.
    Цель: Создание dataframe по фильтрам
    Вход: нет
    Выход: dataframe
    """
    General = pd.DataFrame(hand_base.bd)
    General['DEATHS'] = General['DEATHS'].apply(pd.to_numeric, errors='coerce')

    rat = General.groupby(['Elevation']).agg({'DEATHS': "sum"})
    rat.rename(columns={'Elevation': 'Высота вулкана',
                        'DEATHS': 'Количество смертей'}, inplace=True)
    rat = rat.reset_index()
    rat = rat.round({'Number of deaths': 2})
    # print(rat.fillna(0))
    return rat.fillna(0)


def elevation_damage():
    """
    Автор: Баканов Г.
    Цель: Создание dataframe по фильтрам
    Вход: нет
    Выход: dataframe
    """
    General = pd.DataFrame(hand_base.bd)
    General['DAMAGE_MILLIONS_DOLLARS'] = General['DAMAGE_MILLIONS_DOLLARS'].apply(pd.to_numeric,
                                                                                  errors='coerce')

    rat = General.groupby(['Elevation']).agg({'DAMAGE_MILLIONS_DOLLARS': "sum"})

    rat.rename(columns={'Elevation': 'Высота вулкана',
                        'DAMAGE_MILLIONS_DOLLARS': 'Ущерб'}, inplace=True)
    rat = rat.reset_index()
    rat = rat.round({'Damage in million dollars': 2})
    # print(rat.fillna(0))
    return rat.fillna(0)


def draw_hist(root: tk.Tk, pane: ttk.Panedwindow):
    """
    Автор: Ковязин В.
    Цель: Построение гистограммы
    Вход: главное окно, растягивающийся виджет
    Выход: нет
    """

    global CHOSEN_VALUE6

    win = tk.Toplevel(root)
    win.title("Гистограммы")
    win.geometry("600x500+500+200")

    background = tk.Frame(win, bg=constants.style['bg'])
    background.place(x=0, y=0, relwidth=1, relheight=1)
    def save(string):
        """
        Автор: Ковязин В.
        Цель: Сохранение в файл
        Вход: Путь формата строка
        Выход: нет
        """
        fig.savefig(string)
        mb.showinfo("Инфо!", "Картинка сохранена")

    name_lab = tk.Label(background, text='Гистограмма\n' + CHOSEN_VALUE6.get(),
                        bg=constants.style['bg'])
    name_lab.place(relx=0.01, rely=0.01, relwidth=0.95, relheight=0.1)

    if CHOSEN_VALUE6.get() == 'Фильтры для гистограммы':
        mb.showerror("Ошибка!", "Сначала выберите фильтр (гистограммы)!")
        win.destroy()

    if CHOSEN_VALUE6.get() == 'Высота - Количество смертей':
        bd = elevation_deaths()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Высота - Количество смертей')
        bd.plot(kind='hist', ax=ax, y='Количество смертей', x='Elevation', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.draw()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/elevation_deaths_hist.png'))

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

    if CHOSEN_VALUE6.get() == 'Высота - Ущерб':
        bd = elevation_damage()
        fig = plt.figure(figsize=(4, 5), dpi=70)
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle('Высота - Ущерб')
        bd.plot(kind='hist', ax=ax, y='Ущерб', x='Elevation', rot=45, fontsize=9)
        # тут он вставка в интерфейс
        CANVAS = FigureCanvasTkAgg(fig, background)
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar = NavigationToolbar2Tk(CANVAS_1, background)
        # toolbar.update()
        CANVAS.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        button_save = tk.Button(background, font=12, text='Сохранить')
        button_save.bind("<Button-1>", lambda *args: save('../Graphics/elevation_damage_hist.png'))

        button_save.place(relx=0.1, rely=0.0, relheight=0.0495, relwidth=0.22)

def stat_report(root: tk.Tk, target: str) -> tuple:
    """
    Автор: Ковязин В. 
    Цель: Подсчёт количества вхождений атрибута target
    Вход: главное окно, target типа строка
    Выход: количество вхождений и значение процента
    """
    freq = glob.current_base[target].value_counts()
    whole = 0
    for x in freq.values:
        whole += x
    return freq, whole
