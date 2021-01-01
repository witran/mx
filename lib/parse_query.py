import cv2
import pytesseract
import time


def get_item(d, i):
    item = {}
    for prop in d:
        item[prop] = d[prop][i]
    item['id'] = i
    return item

# or search for nearest center


def is_inside(mx, my, x, y, width, height):
    return x <= mx <= x + width and y <= my <= y + height


def is_same_paragraph(w1, w2):
    same_props = ['page_num', 'block_num', 'par_num']
    return all(map(lambda prop: w1[prop] == w2[prop], same_props))


def get_text_from_words(words):
    return ' '.join(map(lambda o: o['text'], words))


def get_queries(img, mx, my):
    start = time.time()

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
    for i in range(n_boxes):
        x, y, w, h = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

        if d['text'][i] and is_inside(mx, my, x, y, w, h):
            target_word_id = i

        # props = []
        # for prop in d:
        #     props.append(str(d[prop][i]).ljust(12))
        # print(''.join(props))

    paragraph = []
    center_id = 0
    target_word = None

    # construct paragraph from words with same page, block, paragraph
    if target_word_id:
        target_word = get_item(d, target_word_id)
        # print('target word', target_word_id, target_word)
        for i, word in enumerate(words):
            if is_same_paragraph(word, target_word):
                paragraph.append(word)

            if word['id'] == target_word['id']:
                center_id = len(paragraph) - 1

    if not target_word:
        print('no target word found')
        return []

    # CUT_OFF_CONFIDENCE = 80
    # line_min = []
    # filter out lines of the paragraph that has low min confidence, except for target_line
    # select L consecutive words before & after target word
    plen = len(paragraph)
    queries = []
    # to be read from refstring, small for "[<num>]" style, larger for "<name> (<year>)" style, 8 should be plenty
    # possibly only return target region from here
    print('pargraph:', get_text_from_words(paragraph))
    print('target word:', target_word['text'])
    print('target word id in paragraph:', center_id)

    L = 6
    for start_id in range(max(center_id - L, 0), center_id + 1):
        # print('start', start_id)
        for end_id in range(center_id + 1, min(center_id + L + 1, plen)):
            # print('end', end_id)
            if end_id - start_id <= L:
                # print(end_id, start_id)
                queries.append(get_text_from_words(paragraph[start_id:end_id]))

    print('queries generator time: {:.4f}s'.format(time.time() - start))

    return queries
