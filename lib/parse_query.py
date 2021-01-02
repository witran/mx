import cv2
import pytesseract
import time
import math


def get_item(d, i):
    item = {}
    for prop in d:
        item[prop] = d[prop][i]
    item['id'] = i
    return item


def is_inside(mx, my, x, y, width, height):
    return x <= mx <= x + width and y <= my <= y + height


def rect_distance(px, py, x1, y1, x2, y2):
    dx = max(x1 - px, 0, px - x2)
    dy = max(y1 - py, 0, py - y2)
    return math.sqrt(dx * dx + dy * dy)


def point_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def is_same_paragraph(w1, w2):
    same_props = ['page_num', 'block_num', 'par_num']
    return all(map(lambda prop: w1[prop] == w2[prop], same_props))


def get_text_from_words(words):
    return ' '.join(map(lambda o: o['text'], words))


def get_queries(img, mx, my):
    start_time = time.time()

    d = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT)

    n_boxes = len(d['level'])

    for i in range(n_boxes):
        x, y, w, h = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h),
                      color=(255, 0, 0), thickness=1)

    cv2.line(img, (mx - 25, my), (mx + 25, my),
             (0, 0, 255), thickness=4)
    cv2.line(img, (mx, my - 25), (mx, my + 25),
             (0, 0, 255), thickness=4)

    cv2.imwrite('.tmp/tess.png', img)

    boxes = [get_item(d, i) for i in range(n_boxes)]
    words = list(filter(lambda o: o['text'], boxes))

    target_word_id = None
    # print(''.join([prop.ljust(12) for prop in d]))
    # search for word wrapping mouse pos
    # props = []
    # for prop in d:
    #     props.append(str(d[prop][i]).ljust(12))
    # print(''.join(props))

    target_word = None
    min_distance = math.inf
    for word in words:
        x, y, w, h = word['left'], word['top'], word['width'], word['height']
        d = rect_distance(mx, my, x, y, x + w, y + h)
        if d < min_distance:
            target_word = word
            min_distance = d

    print(target_word, min_distance)
    x, y, w, h = target_word['left'], target_word['top'], target_word['width'], target_word['height']
    if min_distance > point_distance(x, y, x + w, y + h) / 2:
        target_word = None

    if not target_word:
        print('no target word found')
        return []

    # construct paragraph from words with same page, block, paragraph

    paragraph = []
    target_id = 0

    # print('target word', target_word)
    for i, word in enumerate(words):
        if is_same_paragraph(word, target_word):
            paragraph.append(word)

        if word['id'] == target_word['id']:
            target_id = len(paragraph) - 1

    # CUT_OFF_CONFIDENCE = 80
    # filter out lines of the paragraph that has low min confidence, except for target_line
    # select L consecutive words before & after target word
    queries = []
    # possibly only return target region from here
    print('pargraph:', get_text_from_words(paragraph))
    print('target word:', target_word['text'])
    print('target word id in paragraph:', target_id)

    # to be read from refstring, small for "[<num>]" style, larger for "<name> (<year>)" style, 6 words should be plenty
    L = 6
    start_bound = max(target_id - L, 0)
    end_bound = min(target_id + L + 1, len(paragraph) + 1)

    for start in range(start_bound, target_id + 1):
        for end in range(target_id + 1, end_bound):
            if end - start <= L:
                queries.append(get_text_from_words(paragraph[start:end]))

    print('queries generator time: {:.4f}s'.format(time.time() - start_time))

    return queries
