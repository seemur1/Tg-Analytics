import tkinter as tk
from io import StringIO

import customtkinter as ctk
import re
import datetime
import os
from functools import cmp_to_key
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
          "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

class User:
    def __init__(self, name, path_to_file):
        self.name = name
        self.path_to_file = path_to_file
        self.min_date = datetime.datetime(2030, 5, 10)
        self.max_date = datetime.datetime(2001, 5, 10)
        self.amount_of_words_to = 0
        self.amount_of_words_from = 0
        self.amount_of_words = 0
        self.char_count_from = 0
        self.char_count_to = 0
        self.mutuality = 0.0
        self.voice_dist = 0
        self.call_dist = 0
        self.voice_amount = 0
        self.call_amount = 0
        self.discuss_time = 0
        self.vals_to_csv = [name[:-1]]

# Если mode == True - выгружаются заранее скачанные истории. Если двойке - истории подгружаются из Telegram.
# Если is_multiple == True - анализируемых переписок - несколько. Иначе - одна.
is_archived, is_multiple, time_bounds = True, False, True
dir_path = ""


def single_generation():
    min_date, max_date = datetime.datetime(2030, 5, 10), datetime.datetime(2001, 5, 10)
    start_date, finish_date = max_date, min_date
    if entry2.get() != "":
        start_dates = [int(x) for x in entry2.get().split('.')]
        start_date = datetime.datetime(start_dates[2], start_dates[1], start_dates[0])
    if entry3.get() != "":
        finish_dates = [int(x) for x in entry3.get().split('.')]
        finish_date = datetime.datetime(finish_dates[2], finish_dates[1], finish_dates[0])
    # Параметры, которые указываются перед запуском скрипта.
    border = 0
    for path in os.listdir(dir_path):
        if path.title()[-5:] == ".Html" and os.path.isfile(os.path.join(dir_path, path)):
            border += 1

    # Определяем имя пользователя:
    user_name = ''
    your_name = ''
    with open(dir_path + '/messages.html') as f:
        lines = f.readlines()
        user_name = lines[26]
        checker = True
        counter = 28
        while checker and counter < len(lines):
            if lines[counter - 1] == '       <div class="from_name">\n' and lines[counter] != user_name:
                your_name = lines[counter]
                checker = False
            counter += 1

    mode = False
    getter_word_count, your_word_count, voices_count, calls_count, calls_dist, char_tmp = 0, 0, 0, 0, 0, 0
    char_count_to, char_count_from, dist = 0, 0, 0
    days_period = 0
    weight, old_weight = 1, 0
    labels = ['']
    for i in range(2, border + 1):
        labels.append(str(i))
    for label in labels:
        with open(dir_path + '/messages' + label + '.html') as f:
            lines = f.readlines()
            for line in lines:
                if line == user_name:
                    mode = True
                if line == your_name:
                    mode = False
                if weight == -5:
                    words = line.split()
                    # Обрабатываем звонки иначе:
                    if start_date <= date <= finish_date:
                        calls_count += 1
                        calls_dist += int(words[1][1:])
                        getter_word_count += int(words[1][1:])
                        your_word_count += int(words[1][1:])
                    weight = 0
                if weight == -4 and line == '          <div class="status details">\n':
                    weight = -5
                if line == '        <div class="media clearfix pull_left media_call success">\n':
                    weight = -4
                if weight == -2:
                    line = line.replace('<br>', ' ')
                    char_tmp = len(line)
                    weight = len(line.split())
                if line == '       <div class="text">\n':
                    weight = -2
                if weight == -3:
                    dates = line.split()
                    # Иногда в детали пеерписки попадают не только даты, но ещё и закрепленные сообщения.
                    if len(dates) == 3:
                        date = datetime.datetime(int(dates[2]), months[dates[1]], int(dates[0]))
                    weight = old_weight
                if line == '      <div class="body details">\n':
                    old_weight = weight
                    weight = -3
                if line == 'Video message\n' or line == 'Voice message\n':
                    weight = -1
                if weight == -1 and len(line) > 6 and line[1] == ':':
                    if start_date <= date <= finish_date:
                        if date < min_date:
                            min_date = date
                        if date > max_date:
                            max_date = date
                        voices_count = voices_count + 1
                        dist += int(line[0:1]) * 3600 + int(line[2:4]) * 60 + int(line[5:7])
                    weight = int(line[0:1]) * 7200 + int(line[2:4]) * 120 + int(line[5:7]) * 2
                if weight == -1 and len(line) > 6 and line[2] == ':':
                    if start_date <= date <= finish_date:
                        if date < min_date:
                            min_date = date
                        if date > max_date:
                            max_date = date
                        voices_count = voices_count + 1
                        dist += int(line[3:5]) + int(line[0:2]) * 60
                    weight = int(line[3:5]) * 2 + int(line[0:2]) * 120
                if mode and len(line) == 6 and line[2] == ':' and line[5] == '\n':
                    if start_date <= date <= finish_date:
                        if date < min_date:
                            min_date = date
                        if date > max_date:
                            max_date = date
                        char_count_from += char_tmp
                        getter_word_count += weight
                    weight = 1
                    char_tmp = 0
                if not mode and len(line) == 6 and line[2] == ':' and line[5] == '\n':
                    if start_date <= date <= finish_date:
                        if date < min_date:
                            min_date = date
                        if date > max_date:
                            max_date = date
                        char_count_to += char_tmp
                        your_word_count += weight
                    weight = 1
                    char_tmp = 0
    textbox2.delete("0.0", "end")
    text1 = ""
    if scrollable_frame1_switches[0].get():
        text1 += 'Ваше количество слов: ' + str(your_word_count) + '\n'
    if scrollable_frame1_switches[1].get():
        text1 += 'Количество слов собеседника: ' + str(getter_word_count) + '\n'
    if scrollable_frame1_switches[2].get():
        text1 += 'Общее количество слов: ' + str(getter_word_count + your_word_count) + '\n'
    if scrollable_frame1_switches[3].get():
        if your_word_count + getter_word_count > 0:
            text1 += 'Степень взаимности: ' + str(getter_word_count / (your_word_count + getter_word_count)) + '\n'
        else:
            text1 += 'Степень взаимности: 0%\n'
    if scrollable_frame2_switches[0].get():
        text1 += 'Суммарная продолжительность голосовых: ' + str(dist // 60) + ' минут\n'
    if scrollable_frame2_switches[1].get():
        text1 += 'Суммарная продолжительность звонков: ' + str(calls_dist // 60) + ' минут\n'
    if scrollable_frame2_switches[2].get():
        text1 += 'Суммарная продолжительность звонков и голосовых: ' + str((dist + calls_dist) // 60) + ' минут\n'
    if scrollable_frame2_switches[3].get():
        text1 += 'Cуммарное количество минут, потраченных на написание сообщений собеседнику: ' + str(
            char_count_to // 200) + ' минут\n'
    if scrollable_frame2_switches[4].get():
        text1 += 'Суммарное количество времени, потраченное на собеседника: ' + str(
            (dist + calls_dist) // 60 + char_count_to // 200) + ' минут\n'
    if scrollable_frame2_switches[5].get():
        if max_date == datetime.datetime(2001, 5, 10) and min_date == datetime.datetime(2030, 5, 10):
            text1 += 'Суммарная продолжительность анализируемой переписки: 0 дней.\n'
        else:
            text1 += 'Суммарная продолжительность анализируемой переписки: ' + str((max_date - min_date).days) + ' дней.\n'

    if scrollable_frame3_switches[0].get():
        if max_date == datetime.datetime(2001, 5, 10) and min_date == datetime.datetime(2001, 5, 10):
            text1 += 'Суммарное количество времени, тратящееся на собеседника в день: 0 минут.\n'
        else:
            days_period = (max_date - min_date).days
            text1 += 'Суммарное количество времени, тратящееся на собеседника в день: ' + \
                     str(((dist + calls_dist) / 60 + char_count_to / 200) / days_period) + ' минут.\n'
    if scrollable_frame3_switches[1].get():
        if voices_count == 0:
            text1 += 'Средняя продолжительность голосового: 0 секунд\n'
        else:
            text1 += 'Средняя продолжительность голосового: ' + str(dist // voices_count) + ' cекунды\n'
    if scrollable_frame3_switches[2].get():
        if calls_count == 0:
            text1 += 'Средняя продолжительность звонка: 0 секунд\n'
        else:
            text1 += 'Средняя продолжительность звонка: ' + str(calls_dist // calls_count) + ' cекунды\n'
    textbox2.insert("0.0", text1)

def multiple_generation():
    names = []
    usernames = textbox1.get("0.0", "end").split()

    min_date, max_date = datetime.datetime(2030, 5, 10), datetime.datetime(2001, 5, 10)
    start_date, finish_date = max_date, min_date
    if entry4.get() != "":
        start_dates = [int(x) for x in entry4.get().split('.')]
        start_date = datetime.datetime(start_dates[2], start_dates[1], start_dates[0])
    if entry5.get() != "":
        finish_dates = [int(x) for x in entry5.get().split('.')]
        finish_date = datetime.datetime(finish_dates[2], finish_dates[1], finish_dates[0])
    # Параметры, которые указываются перед запуском скрипта.
    border = 0
    for path in os.listdir(dir_path):
        if path.title()[-5:] == ".Html" and os.path.isfile(os.path.join(dir_path, path)):
            border += 1
    your_name = ''
    for path in usernames:
        with open(dir_path + path + '/messages.html') as f:
            lines = f.readlines()
            name = lines[26]
            names.append(name)

    # Ищем своё имя по перепискам:
    checker = True
    pos = 0
    while checker and pos < len(usernames):
        with open(dir_path + usernames[pos] + '/messages.html') as f:
            lines = f.readlines()
            counter = 28
            while checker and counter < len(lines):
                if lines[counter - 1] == '       <div class="from_name">\n' and lines[counter] != names[pos]:
                    your_name = lines[counter]
                    checker = False
                counter += 1

    users = []
    for i in range(len(usernames)):
        users.append(User(names[i], dir_path + usernames[i]))

    for user in users:
        # Параметры, которые указываются перед запуском скрипта.
        border = 0
        for path in os.listdir(user.path_to_file):
            if path.title()[-5:] == ".Html" and os.path.isfile(os.path.join(user.path_to_file, path)):
                border += 1

        mode = False
        char_tmp, days_period = 0, 0
        weight, old_weight = 1, 0
        labels = ['']
        for i in range(2, border + 1):
            labels.append(str(i))
        for label in labels:
            with open(user.path_to_file + '/messages' + label + '.html') as f:
                lines = f.readlines()
                for line in lines:
                    if line == user.name:
                        mode = True
                    if line == your_name:
                        mode = False
                    if weight == -5:
                        words = line.split()
                        # Обрабатываем звонки иначе:
                        if start_date <= date <= finish_date:
                            user.call_amount += 1
                            user.call_dist += int(words[1][1:])
                            user.amount_of_words_to += int(words[1][1:])
                            user.amount_of_words_from += int(words[1][1:])
                        weight = 0
                    if weight == -4 and line == '          <div class="status details">\n':
                        weight = -5
                    if line == '        <div class="media clearfix pull_left media_call success">\n':
                        weight = -4
                    if weight == -2:
                        line = line.replace('<br>', ' ')
                        char_tmp = len(line)
                        weight = len(line.split())
                    if line == '       <div class="text">\n':
                        weight = -2
                    if weight == -3:
                        dates = line.split()
                        # Иногда в детали переписки попадают не только даты, но ещё и закрепленные сообщения.
                        if len(dates) == 3:
                            date = datetime.datetime(int(dates[2]), months[dates[1]], int(dates[0]))
                        weight = old_weight
                    if line == '      <div class="body details">\n':
                        old_weight = weight
                        weight = -3
                    if line == 'Video message\n' or line == 'Voice message\n':
                        weight = -1
                    if weight == -1 and len(line) > 6 and line[1] == ':':
                        if start_date <= date <= finish_date:
                            if date < user.min_date:
                                user.min_date = date
                            if date > user.max_date:
                                user.max_date = date
                            user.voice_amount += 1
                            user.voice_dist += int(line[0:1]) * 3600 + int(line[2:4]) * 60 + int(line[5:7])
                        weight = int(line[0:1]) * 7200 + int(line[2:4]) * 120 + int(line[5:7]) * 2
                    if weight == -1 and len(line) > 6 and line[2] == ':':
                        if start_date <= date <= finish_date:
                            if date < user.min_date:
                                user.min_date = date
                            if date > user.max_date:
                                user.max_date = date
                            user.voice_amount += 1
                            user.voice_dist += int(line[3:5]) + int(line[0:2]) * 60
                        weight = int(line[3:5]) * 2 + int(line[0:2]) * 120
                    if mode and len(line) == 6 and line[2] == ':' and line[5] == '\n':
                        if start_date <= date <= finish_date:
                            if date < user.min_date:
                                user.min_date = date
                            if date > user.max_date:
                                user.max_date = date
                            user.char_count_from += char_tmp
                            user.amount_of_words_to += weight
                        weight = 1
                        char_tmp = 0
                    if not mode and len(line) == 6 and line[2] == ':' and line[5] == '\n':
                        if start_date <= date <= finish_date:
                            if date < user.min_date:
                                user.min_date = date
                            if date > user.max_date:
                                user.max_date = date
                            user.char_count_to += char_tmp
                            user.amount_of_words_from += weight
                        weight = 1
                        char_tmp = 0
        user.amount_of_words = user.amount_of_words_from + user.amount_of_words_to
        if user.amount_of_words == 0:
            user.mutuality = 0.0
        else :
            user.mutuality = user.amount_of_words_to / user.amount_of_words
    textbox3.delete("0.0", "end")
    text1, csvtext = "", ""
    colnames = []
    colnames.append('Имя')
    # Анализ процента от количества сообщений:
    amount_of_words, voices_dist, calls_dist, mutuality, sum_dist, medium_dist = 0, 0, 0, 0, 0, 0
    # Подсчёт всех сумммарных статистик по всем выбранным перепискам:
    for user in users:
        amount_of_words += user.amount_of_words
        voices_dist += user.voice_dist
        calls_dist += user.call_dist
        mutuality += user.mutuality
        sum_dist += (user.call_dist + voices_dist) // 60 + (user.char_count_to // 200)
        if (user.max_date - user.min_date).days > 0:
            medium_dist += ((user.voice_dist + user.call_dist) / 60 + user.char_count_to / 200) / (user.max_date - user.min_date).days
        else:
            medium_dist += 0

    if len(users) > 0:
        mutuality /= len(users)

    users.sort(key=cmp_to_key(lambda item1, item2: item2.amount_of_words - item1.amount_of_words))
    # Доля по количеству слов:
    if scrollable_frame4_switches[0].get():
        colnames.append('Доля')
        if amount_of_words == 0:
            for user in users:
                user.vals_to_csv.append(0)
        else:
            for user in users:
                user.vals_to_csv.append((user.amount_of_words / amount_of_words) * 100)
    # Ранжирование по количеству слов:
    if scrollable_frame5_switches[0].get():
        colnames.append('Слова')
        for user in users:
            user.vals_to_csv.append(user.amount_of_words)
    # Ранжирование по взаимности:
    if scrollable_frame5_switches[1].get():
        users.sort(key=cmp_to_key(lambda item1, item2: item2.mutuality - item1.mutuality))
        colnames.append('Взаимность')
        for user in users:
            user.vals_to_csv.append(user.mutuality * 100)
    # Ранжирование по длительности аудиодиалогов:
    if scrollable_frame5_switches[2].get():
        users.sort(key=cmp_to_key(
            lambda item1, item2: (item2.voice_dist + item2.call_dist) - (item1.voice_dist + item1.call_dist)))
        colnames.append('ОбщаяПродолжительность')
        for user in users:
            user.vals_to_csv.append((user.voice_dist + user.call_dist) // 60)
    # Ранжирование по длительности голосовых:
    if scrollable_frame5_switches[3].get():
        users.sort(key=cmp_to_key(lambda item1, item2: item2.voice_dist - item1.voice_dist))
        colnames.append('ПродолжительностьГолосовых')
        for user in users:
            user.vals_to_csv.append(user.voice_dist // 60)
    # Ранжирование по длительности звонков:
    if scrollable_frame5_switches[4].get():
        users.sort(key=cmp_to_key(lambda item1, item2: item2.call_dist - item1.call_dist))
        colnames.append('ПродолжительностьЗвонков')
        for user in users:
            user.vals_to_csv.append(user.call_dist // 60)
    # Подсчёт сумммарной продолжительности всех голосовых сообщений:
    if scrollable_frame6_switches[0].get():
        text1 += 'Суммарное кол-во потраченного времени на голосовые сообщения в этих переписках: ' + str(voices_dist // 60) + ' минут.\n'
    # Подсчёт сумммарной продолжительности всех звонков:
    if scrollable_frame6_switches[1].get():
        text1 += 'Суммарное кол-во потраченного времени на звонки в этих переписках: ' + str(calls_dist // 60) + ' минут.\n'
    # Подсчёт сумммарной продолжительности всех аудиодиалогов:
    if scrollable_frame6_switches[2].get():
        text1 += 'Суммарное кол-во потраченного времени на аудиодиалоги в этих переписках: ' + str((voices_dist + calls_dist) // 60) + ' минут.\n'
    # Подсчёт средней взаимности:
    if scrollable_frame6_switches[3].get():
        text1 += 'Средняя взaимность в выбранных переписках: ' + str(mutuality * 100) + '%.\n'
    # Подсчёт суммарного кол-ва слов в выбранных переписках:
    if scrollable_frame6_switches[4].get():
        text1 += 'Суммарное кол-во написанных слов в выбранных переписках: ' + str(amount_of_words) + ' слов.\n'
    # Подсчёт суммарного потраченного времени на собеседников в выбранных переписках:
    if scrollable_frame6_switches[5].get():
        text1 += 'Суммарное кол-во потраченного времени на собеседников в выбранных переписках: ' + str(sum_dist) + ' минут.\n'
    # Подсчёт среднего потраченного времени в день на собеседников в выбранных переписках:
    if scrollable_frame6_switches[6].get():
        text1 += 'Среднее потраченное время в день на собеседников в выбранных переписках: ' + str(medium_dist) + ' минут.\n'
    textbox3.insert("0.0", text1)
    csvtext += '\n'
    for user in users:
        for value in user.vals_to_csv:
            csvtext += str(value) + ','
        csvtext = csvtext[:-1] + '\n'
    csvStringIO = StringIO(csvtext)
    df = pd.read_csv(csvStringIO, sep=",", header=None, names=colnames)
    for i in range(len(colnames) - 1):
        secondary_window = ctk.CTkToplevel()
        secondary_window.title("График соотношения " + colnames[i + 1])
        secondary_window.config(width=300, height=200)
        figure = Figure(figsize=(6, 4), dpi=100)
        figure_canvas = FigureCanvasTkAgg(figure, secondary_window)
        NavigationToolbar2Tk(figure_canvas, secondary_window)
        axes = figure.add_subplot()
        axes.bar(df[colnames[0]], df[colnames[i + 1]])
        axes.set_title(colnames[0])
        axes.set_ylabel(colnames[i + 1])
        figure_canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=1)

def first_switch(frame, entry):
    global dir_path
    frame.tkraise()
    dir_path = entry.get()
    root.title("Choose Your starting settings!")


def second_switch(fr1, fr2):
    root.title("Choose Your Statistics!")
    if not is_multiple:
        if not time_bounds:
            entry2.grid_forget()
            entry3.grid_forget()
            label4.grid_forget()
            label5.grid_forget()
        fr1.tkraise()
        root.geometry("700x750")
    else:
        fr2.tkraise()
        root.geometry("800x750")
        if not time_bounds:
            entry4.grid_forget()
            entry5.grid_forget()
            label7.grid_forget()
            label8.grid_forget()


def archived_callback(selected):
    global is_archived
    is_archived = (selected == "Обработка ранее выгружаемых историй")


def multiple_callback(selected):
    global is_multiple
    is_multiple = (selected == "Несколько")


def time_callback(selected):
    global time_bounds
    time_bounds = (selected == "Да, будет")


# Создание главного окна
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.geometry("500x300")
root.title("Choose Your mode!")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

frame1 = ctk.CTkFrame(root)
frame2 = ctk.CTkFrame(root)
frame3 = ctk.CTkFrame(root)
frame4 = ctk.CTkFrame(root)

for frame in (frame1, frame2, frame3, frame4):
    frame.grid(row=0, column=0, sticky='nsew')

# -------------------Первое окно-------------------

label1 = ctk.CTkLabel(master=frame1, text="Выберите режим работы", font=("Roboto", 20))
label1.pack(pady=12, padx=10)

optionmenu_1 = ctk.CTkOptionMenu(master=frame1,
                                 values=["Обработка ранее выгружаемых историй", "Обработка через telegram API"],
                                 command=archived_callback)
optionmenu_1.pack(pady=12, padx=10)

entry1 = ctk.CTkEntry(master=frame1, placeholder_text="Путь к папке с выгрузками", width=350)
entry1.pack(pady=12, padx=10)

button1 = ctk.CTkButton(master=frame1, text="Done!", width=250, command=lambda: first_switch(frame2, entry1))
button1.pack(pady=10, padx=10)

# -------------------Второе Окно-------------------

label2 = ctk.CTkLabel(master=frame2, text="Сколько переписок анализируется?", font=("Roboto", 20))
label2.pack(pady=12, padx=10)

optionmenu_2 = ctk.CTkOptionMenu(master=frame2, values=["Одна", "Несколько"], command=multiple_callback)
optionmenu_2.pack(pady=12, padx=10)

label3 = ctk.CTkLabel(master=frame2, text="Будет ли ограничение во времени?", font=("Roboto", 20))
label3.pack(pady=12, padx=10)

optionmenu_3 = ctk.CTkOptionMenu(master=frame2, values=["Да, будет", "Нет, не будет"], command=time_callback)
optionmenu_3.pack(pady=12, padx=10)

button2 = ctk.CTkButton(master=frame2, text="Done!", width=250, command=lambda: second_switch(frame3, frame4))
button2.pack(pady=10, padx=10)

# -------------------Третье Окно-------------------

label4 = ctk.CTkLabel(frame3, text="Дата начала:", font=("Roboto", 20))
label5 = ctk.CTkLabel(frame3, text="Дата конца:", font=("Roboto", 20))
label9 = ctk.CTkLabel(frame3, text="Результаты:", font=("Roboto", 20))

entry2 = ctk.CTkEntry(frame3, placeholder_text="10.05.2001", width=350)
entry3 = ctk.CTkEntry(frame3, placeholder_text="10.05.2023", width=350)
textbox2 = ctk.CTkTextbox(frame3, width=700, height=250)
textbox2.insert("0.0", "Здесь будет вывод результатов работы парсера!\n")

scrollable_frame1 = ctk.CTkScrollableFrame(frame3, label_text="Оценки количества слов:", width=350)
scrollable_frame2 = ctk.CTkScrollableFrame(frame3, label_text="Оценки продолжительностей:", width=350)
scrollable_frame3 = ctk.CTkScrollableFrame(frame3, label_text="Средние оценки:", width=350)

button3 = ctk.CTkButton(frame3, text="Сгенерировать выгрузку!", width=500, command=lambda: single_generation())

frame3.grid_columnconfigure((0, 1, 2), weight=1)

label4.grid(row=0, column=0, sticky='w', padx=10)
label5.grid(row=0, column=2, sticky='w', padx=10)
label9.grid(row=4, column=1, sticky='w', padx=10)

entry2.grid(row=1, column=0, sticky='ew', padx=10)
entry3.grid(row=1, column=2, sticky='ew', padx=10)
textbox2.grid(row=5, column=0, columnspan=3, sticky='nsew', padx=10)

# Описываем расположение настроек:
scrollable_frame1.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
scrollable_frame1.grid_columnconfigure(0, weight=1)
scrollable_frame1_switches = []
scrollable_frame2.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
scrollable_frame2.grid_columnconfigure(0, weight=1)
scrollable_frame2_switches = []
scrollable_frame3.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
scrollable_frame3.grid_columnconfigure(0, weight=1)
scrollable_frame3_switches = []

button3.grid(row=3, column=0, columnspan=3, padx=10, sticky="nsew")

texts1 = ["Ваши слова:", "Слова собеседника:", "Общее количество слов:", "Взаимность:"]

# Cобираем переключатели режимов работы:
for i in range(len(texts1)):
    switch = ctk.CTkSwitch(master=scrollable_frame1, text=texts1[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame1_switches.append(switch)

texts2 = ["Время на голосовые:", "Время на звонки:", "Время на звонки и голосовые:",
          "Время на текст:", "Время на собеседника:", "Продолжительность переписки:"]

for i in range(len(texts2)):
    switch = ctk.CTkSwitch(master=scrollable_frame2, text=texts2[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame2_switches.append(switch)

texts3 = ["Время в день:", "Среднее голосовое:", "Средний звонок:"]

for i in range(len(texts3)):
    switch = ctk.CTkSwitch(master=scrollable_frame3, text=texts3[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame3_switches.append(switch)

#--------------------Четвертое Окно-----------------

label6 = ctk.CTkLabel(frame4, text="Список чатов:", font=("Roboto", 20))
label7 = ctk.CTkLabel(frame4, text="Дата начала:", font=("Roboto", 20))
label8 = ctk.CTkLabel(frame4, text="Дата конца:", font=("Roboto", 20))

entry4 = ctk.CTkEntry(frame4, placeholder_text="10.05.2001", width=350)
entry5 = ctk.CTkEntry(frame4, placeholder_text="10.05.2023", width=350)
textbox1 = ctk.CTkTextbox(frame4, width=350, height=125)
textbox1.insert("0.0", "username1\nusername2\n")
textbox3 = ctk.CTkTextbox(frame4, width=800, height=250)
textbox3.insert("0.0", "Здесь будет вывод результатов работы парсера!\n")

scrollable_frame4 = ctk.CTkScrollableFrame(frame4, label_text="Доли:", width=350)
scrollable_frame5 = ctk.CTkScrollableFrame(frame4, label_text="Ранжирования:", width=350)
scrollable_frame6 = ctk.CTkScrollableFrame(frame4, label_text="Общие оценки:", width=350)

button4 = ctk.CTkButton(frame4, text="Сгенерировать выгрузку!", width=500, command=lambda:multiple_generation())

frame4.grid_columnconfigure((0,1,2), weight= 1)

label6.grid(row=0, column=1, sticky='ws', padx=10)
label7.grid(row=2, column=0, sticky='ws', padx=10)
label8.grid(row=2, column=2, sticky='ws', padx=10)

entry4.grid(row=3, column=0, sticky='ew', padx=10)
entry5.grid(row=3, column=2, sticky='ew', padx=10)
textbox1.grid(row=1, column=1, rowspan=3, sticky='nsew', padx=10)
textbox3.grid(row=6, column=0, columnspan=3, sticky='nsew', padx=10)

#Описываем расположение настроек:
scrollable_frame4.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
scrollable_frame4.grid_columnconfigure(0, weight=1)
scrollable_frame4_switches = []
scrollable_frame5.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")
scrollable_frame5.grid_columnconfigure(0, weight=1)
scrollable_frame5_switches = []
scrollable_frame6.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")
scrollable_frame6.grid_columnconfigure(0, weight=1)
scrollable_frame6_switches = []

button4.grid(row=5, column=0, columnspan=3, padx=10, sticky="nsew")

texts4 = ["Доля по словам:"]

#Cобираем переключатели режимов работы:
for i in range(len(texts4)):
    switch = ctk.CTkSwitch(master=scrollable_frame4, text=texts4[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame4_switches.append(switch)

texts5 = ["Ранжирование по словам:", "Ранжирование по взаимности:", "Ранжирование по аудио:",
          "Ранжирование по голосовым:", "Ранжирование по звонкам:"]

for i in range(len(texts5)):
    switch = ctk.CTkSwitch(master=scrollable_frame5, text=texts5[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame5_switches.append(switch)

texts6 = ["Продолжительность голосовых:", "Продолжительность звонков:", "Продолжительность аудио:",
          "Средняя взаимность:", "Общее кол-во слов:", "Общее время:", "Среднее время:"]

for i in range(len(texts6)):
    switch = ctk.CTkSwitch(master=scrollable_frame6, text=texts6[i])
    switch.grid(row=i, column=0, padx=10, pady=(0, 20))
    switch.toggle()
    scrollable_frame6_switches.append(switch)

# -------------------Итоговый вывод-----------------

frame1.tkraise()

root.mainloop()
