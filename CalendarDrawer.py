from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO

IMAGE_SIZE = 256
BORDER_THICKNESS = 5
HEAD_HIGHT = 75
FONT_SIZE = 30
DAYS = ['ПОНЕДЕЛЬНИК', "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
FONT = ImageFont.truetype("arial.ttf", size=FONT_SIZE)


def get_cells_rect_coord(n: int) -> tuple:
    x1 = IMAGE_SIZE * n + (BORDER_THICKNESS) * n
    x2 = x1 + IMAGE_SIZE + BORDER_THICKNESS
    y1 = HEAD_HIGHT + IMAGE_SIZE * n + (BORDER_THICKNESS * 2) * n
    y2 = y1 + IMAGE_SIZE + BORDER_THICKNESS * 2
    return (x1, x2, y1, y2)


def draw_calendar_cell() -> None:
    hight = 5 * IMAGE_SIZE + 8 * BORDER_THICKNESS + HEAD_HIGHT
    width = 7 * IMAGE_SIZE + 8 * BORDER_THICKNESS
    img = Image.new('RGB',
                    (width, hight),
                    'white')
    idraw = ImageDraw.Draw(img)

    idraw.rectangle((0, 0, width, HEAD_HIGHT), width=BORDER_THICKNESS, outline='black')  # заголовки
    for i in range(7):
        x_start_vert, x_end_vert, y_start_hor, y_end_hor = get_cells_rect_coord(i)

        idraw.rectangle((x_start_vert, 0, x_end_vert, hight),
                        width=BORDER_THICKNESS,
                        outline='black')

        idraw.rectangle((0, y_start_hor, width, y_end_hor),
                        width=BORDER_THICKNESS,
                        outline='black')

    for i in range(len(DAYS)):
        x = (IMAGE_SIZE * i + BORDER_THICKNESS * (i)) + IMAGE_SIZE / 2 - FONT.getbbox(DAYS[i])[2] // 2
        print(FONT.getbbox(DAYS[i]))
        idraw.text((x, HEAD_HIGHT / 2 - 16), text=DAYS[i], font=FONT, fill='black')

    img.save('cell.jpg')


def fill_calendar(data: list, year: int) -> BytesIO:
    img = Image.open('img/cell.jpg')
    idraw = ImageDraw.Draw(img)
    bio = BytesIO()

    if not data:
        return bio

    today = datetime(year, data[0][1], 1).weekday()

    for day in range(1, 32):
        if data:
            if int(data[0][0]) == day:
                # Координаты левого верхнего угла клетки
                x_upleft = ((day + today - 1) % 7) * IMAGE_SIZE + BORDER_THICKNESS * (((day + today - 1) % 7) + 1)
                y = 2 * BORDER_THICKNESS + HEAD_HIGHT + ((day + today - 1) // 7) * IMAGE_SIZE + 2 * (
                        (day + today - 1) // 7) * BORDER_THICKNESS
                x_upright = x_upleft + IMAGE_SIZE - FONT_SIZE * len(str(data[0][0]))  # x-координата правого угла клетки
                img.paste(Image.open(data[0][2]), (x_upleft, y))
                idraw.text((x_upright, y), text=str(day), font=FONT,
                           fill='black')
                data.pop(0)

    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio


if __name__ == '__main__':
    pass
    # draw_calendar_cell()
