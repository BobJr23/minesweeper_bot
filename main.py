import pyautogui
import mss
import mss.tools
import cv2
import numpy as np
import time
import mouse
import sys
import keyboard

# t = time.time()
# print(pyautogui.pixel(100, 100))
# print(time.time() - t)
# exit()
TAN = ((229, 194, 159), (215, 184, 153))
GREEN = ((191, 225, 125), (185, 221, 119))
grid = np.zeros((20, 24))

methods = [
    cv2.TM_CCOEFF_NORMED,
    cv2.TM_CCORR_NORMED,
    cv2.TM_SQDIFF_NORMED,
    cv2.TM_SQDIFF,
    cv2.TM_CCORR,
    cv2.TM_CCOEFF,
]


def grayscale(img):
    return cv2.imread(img, cv2.IMREAD_GRAYSCALE)


TEMPLATES = list(
    map(
        grayscale,
        [
            r"img\flag.png",
            r"img\1.png",
            r"img\2.png",
            r"img\3.png",
            r"img\4.png",
            r"img\5.png",
            r"img\6.png",
        ],
    )
)
# import pyautogui

# pyautogui.mouseInfo()
# exit()
WIDTH, HEIGHT = 600, 500
TILE_SIZE = 19


# 24x20 grid
def screenshot(coords=[180, 0, WIDTH, HEIGHT], test=False):
    with mss.mss() as sct:
        if coords != [180, 0, WIDTH, HEIGHT]:
            coords = [
                180 + 25 * (coords[1] - 1) + 4,
                25 * (coords[0] - 1) + 3,
                TILE_SIZE,
                TILE_SIZE,
            ]
        top, left, width, height = coords
        monitor = {"top": top, "left": left, "width": width, "height": height}

        output = rf"img\{'test' if test else str(coords)}.png"
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, (width, height), output=output)


def match_picture(img):
    img_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(img)
    x = TEMPLATES[-1]
    for i, x in enumerate(TEMPLATES):
        res = cv2.matchTemplate(img_gray, x, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.8)
        for pt in zip(*loc[::-1]):
            # cv2.rectangle(img, pt, (pt[0] + TILE_SIZE, pt[1] + TILE_SIZE), (0, 0, 255), 2)
            # cv2.imshow(str(0), img)
            # cv2.waitKey(0)
            x1, y1 = round((pt[0] - 3) / 25), round((pt[1] - 3) / 25)
            grid[y1, x1] = i + 1
    for i, x in enumerate(grid):
        for z, y in enumerate(x):
            if y == 0 and (img[i * 25 + 10, z * 25 + 10][0] > 110):
                grid[i, z] = -1


def check_neighbors(x, y):
    neighbors = []
    value = grid[y, x]

    for z in [
        (y + 1, x + 1),
        (y + 1, x - 1),
        (y - 1, x + 1),
        (y - 1, x - 1),
        (y + 1, x),
        (y - 1, x),
        (y, x + 1),
        (y, x - 1),
    ]:
        if (z[0] < 0) or (z[0] > 19) or (z[1] < 0) or (z[1] > 23):
            continue
        neighbors.append((grid[z[0], z[1]], z))
    nvalues = [_[0] for _ in neighbors]
    flag_count = nvalues.count(1)
    open_spots = nvalues.count(0)
    if open_spots == 0:
        return "no open spots"
    if flag_count == value - 1:
        # left click all neighbors
        locs = list(filter(lambda x: x[0] == 0, neighbors))
        for x in locs:
            click_pos = (10 + x[1][1] * 25, 190 + x[1][0] * 25)
            mouse.move(*click_pos, absolute=True)
            time.sleep(0.1)
            mouse.click("left")

        return "placed"
    if flag_count + open_spots == value - 1:
        locs = list(filter(lambda x: x[0] == 0, neighbors))
        for x in locs:
            click_pos = (10 + x[1][1] * 25, 190 + x[1][0] * 25)
            mouse.move(*click_pos, absolute=True)
            # time.sleep(0.1)

            mouse.click("right")

        return "placed"
    return "nothing happened"


def exit_on_esc():
    if keyboard.is_pressed("esc"):
        exit()


def check():
    exit_on_esc()
    time.sleep(0.2)
    screenshot(test=True)
    match_picture(
        r"img\test.png",
    )

    for x in range(20):
        for y in range(24):
            if (grid[x, y] > 1) and check_neighbors(y, x) == "placed":
                check()


# 13x5, 13x8
if __name__ == "__main__":
    check()
