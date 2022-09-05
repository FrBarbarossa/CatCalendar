from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO

IMAGE_SIZE = 256
BORDER_THICKNESS = 5
HEAD_HIGHT = 75
FONT_SIZE = 30


def draw_calendar_cell():
    hight = 5 * IMAGE_SIZE + 8 * BORDER_THICKNESS + HEAD_HIGHT
    width = 7 * IMAGE_SIZE + 8 * BORDER_THICKNESS
    img = Image.new('RGB',
                    (width, hight),
                    'white')
    idraw = ImageDraw.Draw(img)
    # idraw.rectangle((0, 0, width, hight), width=BORDER_THICKNESS, outline='black', fill='yellow')  # рамка
    idraw.rectangle((0, 0, width, HEAD_HIGHT), width=BORDER_THICKNESS, outline='black')  # заголовки
    for i in range(7):
        x_start_vert = IMAGE_SIZE * i + (BORDER_THICKNESS) * i
        idraw.rectangle((x_start_vert, 0, x_start_vert + IMAGE_SIZE + BORDER_THICKNESS, hight),
                        width=BORDER_THICKNESS,
                        outline='black')
        y_start_hor = HEAD_HIGHT + IMAGE_SIZE * i + (BORDER_THICKNESS * 2) * i
        idraw.rectangle((0, y_start_hor, width, y_start_hor + IMAGE_SIZE + BORDER_THICKNESS * 2),
                        width=BORDER_THICKNESS,
                        outline='black')

    font = ImageFont.truetype("arial.ttf", size=FONT_SIZE)
    # print(font.getsize(text='ПОНЕДЕЛЬНИК'))
    days = ['ПОНЕДЕЛЬНИК', "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
    for i in range(len(days)):
        x = (IMAGE_SIZE * i + BORDER_THICKNESS * (i)) + IMAGE_SIZE / 2 - font.getsize(days[i])[0] // 2
        idraw.text((x, HEAD_HIGHT / 2 - 16), text=days[i], font=font, fill='black')
    img.save('cell.jpg')


def fill_calendar(data: list, year: int):
    # today = datetime(year, data[0][1], data[0][0]).weekday()
    today = datetime(year,data[0][1], 1).weekday()
    img = Image.open('img/cell.jpg')
    idraw = ImageDraw.Draw(img)
    # x = (today) * IMAGE_SIZE + BORDER_THICKNESS * (today + 1)
    # y = 2 * BORDER_THICKNESS + HEAD_HIGHT - 5 + ((today+data[0][0]) // 7) * IMAGE_SIZE + (
    #             (data[0][0]+today) // 7) * BORDER_THICKNESS +5
    # first = False
    for day in range(1, 32):
        if data:
            if data[0][0] == day:
                # if first:
                x = ((day + today-1) % 7) * IMAGE_SIZE + BORDER_THICKNESS * (((day + today - 1) % 7) + 1)
                y = 2 * BORDER_THICKNESS + HEAD_HIGHT + ((day + today - 1) // 7) * IMAGE_SIZE + 2 * ((day + today - 1) // 7) * BORDER_THICKNESS
                # first = True
                img.paste(Image.open(data[0][2]), (x, y))
                data.pop(0)
    # img.show()
    bio = BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio


if __name__ == '__main__':
    # pass
    draw_calendar_cell()
    # fill_calendar([(2, 9, 'img/Sport.jpg'), (5, 9, 'img/Ill.jpg')], 2022)