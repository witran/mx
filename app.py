import mss
import mss.tools
import keyboard
import keyboard._darwinmouse
import time
import numpy as np
import cv2
import pytesseract
import math
import time
from lib import parse_query, parse_text, search

FILE_NAME = '.tmp/1911.02782.pdf.tei.xml'
OUTPUT_FILE = 'imgs/shot.png'
# heuristic values to be improved based on screen resolution
WIDTH = 5120
HEIGHT = 120
CORNER_PADDING = 40


def tess(img):
    d = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT)

    n_boxes = len(d['level'])

    for i in range(n_boxes):
        x, y, w, h = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h),
                      color=(255, 0, 0), thickness=1)

    # print(''.join([prop.ljust(12) for prop in d]))

    for i in range(n_boxes):
        props = []
        for prop in d:
            props.append(str(d[prop][i]).ljust(12))

        # print(''.join(props))

    return img, d


def auto_canny(img, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(img)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(img, lower, upper)
    # return the edged image
    return edged


def crop(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('shot-bw.png', gray)

    edges = auto_canny(gray)
    # cv2.imwrite('shot-edges.png', edges)

    # blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    # cv2.imwrite('shot-blurr.png', blurred)

    # edges = auto_canny(gray)
    # cv2.imwrite('shot-edges.png', edges)

    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, 1)
    # dilated = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)
    # cv2.imwrite('dilated.png', dilated)

    borders = np.zeros_like(img)

    # highlight horizontal lines
    minLineLength = 200
    maxLineGap = 1
    h_lines = cv2.HoughLinesP(dilated, 1, np.pi / 2, 1 * minLineLength,
                              minLineLength=minLineLength, maxLineGap=maxLineGap)

    if h_lines is None:
        print('none horizontal line')
    else:
        print('horizontal lines:', h_lines.shape[0])

        for line in h_lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(borders, (x1 - CORNER_PADDING, y1),
                     (x2 + CORNER_PADDING, y2), (0, 0, 255), 1)

    # highlight vertical lines
    minLineLength = int(0.5 * HEIGHT)
    maxLineGap = 0
    v_lines = cv2.HoughLinesP(dilated, 1, np.pi, 1 * minLineLength,
                              minLineLength=minLineLength, maxLineGap=maxLineGap)

    if v_lines is None:
        print('none vertical line')
    else:
        print('vertical lines:', v_lines.shape[0])

        for line in v_lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(borders, (x1, y1 + CORNER_PADDING),
                     (x2, y2 - CORNER_PADDING), (0, 0, 255), 1)

    # floodFill from mouse position, let highlighted lines be border
    # bounding rect returned from floodFill will be the area of interest
    # cv2.imwrite('shot-hough.png', img)
    h, w, _ = img.shape
    mx = int(w / 2)
    my = int(h / 2)
    _, _, _, rect = cv2.floodFill(
        borders, None, (mx, my), (255, 0, 0), flags=4 | (255 << 8))

    x1, y1, w, h = rect
    # cv2.imwrite('imgs/shot-masked.png', borders)
    # cv2.imwrite('shot-masked-2.png', img)

    crop = img[y1:y1+h, x1:x1+w]
    print(crop.shape)
    return crop, mx - x1, my - y1


def to_bgr(mss_img):
    img = np.array(mss_img, dtype=np.uint8)
    return img[:, :, :3]


def global_alignment_score(s1, s2):
    n1 = len(s1) + 1
    n2 = len(s2) + 1
    f = [[0 for _ in range(n2)] for _ in range(n1)]
    for i in range(n1):
        f[i][0] = -i

    for i in range(n2):
        f[0][i] = -i

    for i in range(1, n1):
        for j in range(1, n2):
            f[i][j] = max(
                f[i][j - 1] - 1,
                f[i - 1][j] - 1,
                f[i - 1][j - 1] + (1 if s1[i - 1] == s2[j - 1] else -2))

    # [print(''.join(map(lambda v: str(v).ljust(4), f[i]))) for i in range(n1)]

    return f[n1 - 1][n2 - 1]


def min_edit_alignment(pattern, text):
    # find a substring in text that has minimum edit distance to pattern
    pass


def handle_capture():
    print(keyboard._darwinmouse.get_position())
    left, top = keyboard._darwinmouse.get_position()

    start = time.time()
    viewport = {"top": top - HEIGHT/2, "left": left -
                WIDTH/2, "width": WIDTH, "height": HEIGHT}

    with mss.mss() as sct:
        mss_img = sct.grab(viewport)
        img = cv2.cvtColor(
            np.array(mss_img, dtype=np.uint8), cv2.COLOR_BGRA2BGR)
        rect, mx, my = crop(img)
        cv2.imwrite('.tmp/crop.png', rect)
        print(mx, my)
        print("crop time: {:.4f}s".format(time.time() - start))
        # tessed, text_data = tess(rect)

        # extract_line(text_data)

        # try:
        search.search(rect, mx, my, FILE_NAME)
        # except:
        # print('error')

        print("total handler time: {:.4f}s".format(time.time() - start))


# initialize tab session by querying grobid then pull data from query queue

keyboard.add_hotkey('command+e', handle_capture)
keyboard.wait()
