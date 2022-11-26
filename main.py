from tkinter import *
from PIL import Image, ImageTk
import time
import random

"""Настройки игры"""
HEIGHT_WINDOW = 600
WIDTH_WINDOW = 500
HEIGHT_JUMP = 110
SPEED_MOVE_DOUDLE = 5
SPEED_JUMP_DOUDLE = 3
PATH_IMG_DOODLE = './img/underwater-right@2x.png'
PATH_IMG_PLATFORM = './img/greenplatform.png'

"""Создаем игровое поле"""
window = Tk()
window.title("Doodle Jump")
canvas = Canvas(window, width=WIDTH_WINDOW, height=HEIGHT_WINDOW, highlightthickness=0)
canvas.pack()
window.update()


class ObjectAll:
    """"Определяем родительский класс с общими свойствами для создаваемых на поле объектов"""
    def __init__(self, x, y, path_img, anchor, canvas):
        self.canvas = canvas
        self.path = path_img  # путь к изображению
        self.anchor = anchor  # от какого угла считать координаты
        self.x, self.y = x, y  # координаты для вставки объекта
        self.pil_img = Image.open(self.path)
        self.img = ImageTk.PhotoImage(self.pil_img)
        self.img_width, self.img_height = self.pil_img.size  # вычисляем высоту и ширину изображения
        self.id = canvas.create_image(self.x, self.y, anchor=anchor, image=self.img)  # помещаем объект на конву

    def moove(self, x, y):
        """Метод перемещения объекта"""
        self.canvas.move(self.id, x, -y)  # для удобства инвертируем ось y

    def get_position(self):
        """Метод получения текущих координат объекта"""
        return self.canvas.coords(self.id)


class Doodle(ObjectAll):
    """Класс для создания персонажа"""
    def __init__(self, x, y, path_img, anchor, canvas):
        super().__init__(x, y, path_img, anchor, canvas)
        """Расширяем параметры класса (добавляем дополнительные)"""
        self.canvas = canvas
        self.x = x
        self.y = y
        self.direction_moove_x = "stop"  # указывает на направление движения или отсутствие движения
        self.canvas.bind_all('<KeyPress-d>', self.moove_right)
        self.canvas.bind_all('<KeyPress-a>', self.moove_left)
        self.canvas.bind_all('<KeyRelease>', self.moove_stop)


    def moove_left(self, event):
        """Вызывается по событию - нажата клавиша a"""
        self.direction_moove_x = "left"

    def moove_right(self, event):
        """Вызывается по событию - нажата клавиша d"""
        self.direction_moove_x = "right"

    def moove_stop(self, event):
        """Вызывается по событию - клавиша отжата"""
        self.direction_moove_x = "stop"


class Platform(ObjectAll):
    """Класс для создания платформ - сейчас не пригодился с заделом на будущее"""
    pass


class Count():
    """"Класс для создание счетчика"""
    def __init__(self, canvas, x, y, anchor):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.anchor = anchor
        self.id = canvas.create_text(self.x, self.y, text='0', anchor=self.anchor, fill="black", font=("Verdana", 20, 'bold'))

    def update(self, txt):
        """Метод обновления информации в счетчике"""
        self.canvas.itemconfigure(self.id, text=txt)


def generation_platform(heght_jump, height_window, width_window, start_pos=50):
    """Функция генерирует платформы рандомно по условиям"""
    pl = []  # Сюда добавляем объекты Platform
    y_inc = heght_jump / 2  # высота между платформами ровна половине высоты прыжка
    y = start_pos  # высота первой платформы
    while y < height_window:  # создаем платформы до тех пор пока не упремся в "потолок"
        x = random.randint(0, width_window-100)
        pl.append(Platform(x=x, y=height_window-y, path_img=PATH_IMG_PLATFORM, anchor='nw', canvas=canvas))
        y += y_inc
    return pl


def get_position_all(platform):
    """Позволяет получить список координат для всех платформ на экране"""
    pos = []
    for p in platform:
        pos.append(p.get_position())
    return pos


def touch_platform(pos_platform, width_platform, pos_doodle):
    """Проверяет косанулся ли персонаж платформы"""
    for i in pos_platform:
        if i[0] - 60 <= pos_doodle[0] <= i[0] + width_platform - 40 and i[1] - 2 <= pos_doodle[1] <= i[1] + 2:
            return i  # Если было касание возвращаются координаты платформы
    return None

"""Генерируем платформы"""
platform = generation_platform(HEIGHT_JUMP, HEIGHT_WINDOW, WIDTH_WINDOW)
"""Получаем и сохраняем позиции сгенерированных платформ"""
platform_position = get_position_all(platform)

"""Создаем персонажа над первой платформой"""
doodle = Doodle(x=platform_position[0][0], y=platform_position[0][1]-50, path_img=PATH_IMG_DOODLE, anchor='sw', canvas=canvas)

"""Создаем объект счетчика"""
counter = Count(canvas, 0, 0, 'nw')

witdh_doodle = doodle.img_width  # сохраняем ширину изображения doodle
width_platform = platform[0].img_width  # сохраняем ширину изображения platform
flag_drop = True  # флаг определяет будет ли персонаж падать - смещаться вниз
count = 0  # сюда запишем количество пройденных платформ

while True:
    doodle_position = doodle.get_position()  # постоянно получаем координаты персонажа

    if flag_drop:
        y = -SPEED_JUMP_DOUDLE - 1  # устанавливаем скорость падения персонажа
        platform_position = get_position_all(platform)  # обновляем координаты платформ
        p = touch_platform(platform_position, width_platform, doodle_position)  # запрашиваем было ли касание в момент падения персонажа
        if p is not None:  # Выполнится если было касание
            flag_drop = False
    else:
        y = SPEED_JUMP_DOUDLE  # устанавливаем скорость прыжка (подъема)
        if doodle_position[1] <= p[1]-HEIGHT_JUMP:  # поднимаемся на высоту прыжка над платформой которой коснулись
            flag_drop = True

    doodle.moove(0, y)  # постоянно перемещаем персонажа по оси y в зависимости от условий выше

    """Если Doodle пересекает середину экрана"""
    if doodle_position[1] < HEIGHT_WINDOW/2:
        for i in range(len(platform)):  # Сдвигаем каждую платформу вниз
            platform[i].moove(0, -2)
        # list(map(lambda i: i.moove(0, -2), platform))  # Так запись короче, но время исполнения выше((

    """Если платформа ушла за экран"""
    if platform_position[0][1] > HEIGHT_WINDOW:
        platform.pop(0)  # Удаляем эту платформу
        platform_position.pop(0)  # Удаляем ее координаты
        count += 1  # Засчитываем платформу как пройденную
        counter.update(count)  # Обновляем значение счетчика на экране и генерируем новую платформу
        platform.append(Platform(x=random.randint(0, WIDTH_WINDOW-width_platform), y=platform_position[-1][1] - HEIGHT_JUMP/2, path_img=PATH_IMG_PLATFORM, anchor='nw',canvas=canvas))

    """Если Doodle коснулся низа экрана - завершаем цикл"""
    if doodle_position[1] > HEIGHT_WINDOW:
        print("Game over")
        break

    """Перемещаем Doodle влево-право кнопками"""
    if doodle.direction_moove_x == "right":
        doodle.moove(SPEED_MOVE_DOUDLE, 0)
    elif doodle.direction_moove_x == "left":
        doodle.moove(-SPEED_MOVE_DOUDLE, 0)

    """Если Doodle коснулся стены он появится с другой стороны"""
    if doodle_position[0] < 0:
        doodle.moove(WIDTH_WINDOW - witdh_doodle, 0)
    elif doodle_position[0] > WIDTH_WINDOW - witdh_doodle:
        doodle.moove(-WIDTH_WINDOW + witdh_doodle, 0)


    """Обновляем окно"""
    window.update()
    time.sleep(0.005)


