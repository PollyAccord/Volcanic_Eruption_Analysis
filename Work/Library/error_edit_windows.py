from tkinter import messagebox as mb


def error(string):
    """
    Автор:
    Цель: обрабатывает исключения
    Вход: объект исключения
    Выход: Строковое сообщение
    """
    mb.showerror("Ошибка", string)


def yes_no(string):
    """
    Автор: \n
    Цель: Выводит окно с вопросом и ответами yes/no \n
    Вход: сообщение \n
    Выход: принятое решение (да/нет) \n
    """
    answer = mb.askyesno(title="Вопрос", message=string)
    if answer:
        mb.showinfo("Cообщение", "Выполнено")
        return answer
    mb.showinfo("Сообщение", "Отменено")
    return answer


def warning(string, flag):
    """
    Автор:
    Цель: Открывает окно с текстом-предупреждением
    Вход: сообщение
    Выход: Нет
    """
    if not flag:
        mb.showwarning("Предупреждение", string)
    else:
        mb.showinfo("Cообщение", "OK")
