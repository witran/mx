import cv2
import pytesseract

FILE = '.tmp/crop.png'
mx, my = (1078, 110)


def get_item(d, i):
    item = {}
    for prop in d:
        item[prop] = d[prop][i]
    return item

# or search for nearest center


def is_inside(mx, my, x, y, width, height):
    return x <= mx <= x + width and y <= my <= y + height


def is_same_line(w1, w2):
    props = ['page_num', 'block_num', 'par_num', 'line_num']
    return all(map(lambda prop: w1[prop] == w2[prop], props))


def tess(img):
    d = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT)

    n_boxes = len(d['level'])

    for i in range(n_boxes):
        x, y, w, h = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h),
                      color=(255, 0, 0), thickness=1)

    target_word_id = None

    boxes = [get_item(d, i) for i in range(n_boxes)]
    words = list(filter(lambda o: o['text'], boxes))
    # print(words)

    # print(''.join([prop.ljust(12) for prop in d]))
    # search for word wrapping mouse pos
    for i in range(n_boxes):
        x, y, w, h = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

        if d['text'][i] and is_inside(mx, my, x, y, w, h):
            target_word_id = i

        # props = []
        # for prop in d:
        #     props.append(str(d[prop][i]).ljust(12))
        # print(''.join(props))

    # for i, word in enumerate(words):
    #     x, y, w, h = (word['left'], word['top'], word['width'], word['height'])

    #     if is_inside(mx, my, x, y, w, h):
    #         target_word_id = i
    #         break

    line = []
    if target_word_id:
        target_word = get_item(d, target_word_id)
        print('target word', target_word_id, target_word)
        for i, word in enumerate(words):
            if is_same_line(word, target_word):
                line.append(word['text'])

    print(line)

    return img, d


img, d = tess(cv2.imread(FILE))
