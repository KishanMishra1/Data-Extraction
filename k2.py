# bounding_boxes is the bounding box array
# textAnnotation is the array from gcp ocr
# convert to function for ease of use
# mapping is a dict

import dmm

bounding_boxes=dmm.bounding_boxes

textAnnotation=dmm.res['responses'][0]['textAnnotations']


def overlap_calc(bb1, bb2):
        assert bb1['x1'] < bb1['x2']
        assert bb1['y1'] < bb1['y2']
        assert bb2['x1'] < bb2['x2']
        assert bb2['y1'] < bb2['y2']

        x_left = max(bb1['x1'], bb2['x1'])
        y_top = max(bb1['y1'], bb2['y1'])
        x_right = min(bb1['x2'], bb2['x2'])
        y_bottom = min(bb1['y2'], bb2['y2'])

        if x_right < x_left or y_bottom < y_top:
                return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
        bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

        iou = intersection_area / float(bb2_area)
        assert iou >= 0.0
        assert iou <= 1.0
        return iou


def get_iou(bb1, bb2):
        assert bb1['x1'] < bb1['x2']
        assert bb1['y1'] < bb1['y2']
        assert bb2['x1'] < bb2['x2']
        assert bb2['y1'] < bb2['y2']

        x_left = max(bb1['x1'], bb2['x1'])
        y_top = max(bb1['y1'], bb2['y1'])
        x_right = min(bb1['x2'], bb2['x2'])
        y_bottom = min(bb1['y2'], bb2['y2'])

        if x_right < x_left or y_bottom < y_top:
                return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
        bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

        iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
        assert iou >= 0.0
        assert iou <= 1.0
        return iou


textAnnotation=dmm.res['responses'][0]['textAnnotations']
mapping = dict()
for j, bx in enumerate(textAnnotation):
    if j == 0:
        continue
    bb = bx['boundingPoly']['vertices']
    for index, bbox in enumerate(bounding_boxes):
        if index not in mapping:
            mapping[index] = ""

        # mapping[index] = ""
        # print({"x1":bbox[0], "y1":bbox[1], "x2":bbox[2], "y2":bbox[3]})
        # print({"x1": bb[0]['x'], "y1":bb[0]['y'], "x2":bb[2]['x'], "y2":bb[2]['y']})
        # print("Index", index)
        #    if bbox[0]<=bb[0]['x'] and bbox[1]>=bb[0]['y'] and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']:
        #      mapping[str(index)] += bx['description']
        #      mapping[str(index)] += " "
        #
        #    elif ((abs(bbox[0] - bb[0]['x']))>=5 and bbox[1]>=bb[0]['y'] and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']) or (bbox[0]<=bb[0]['x'] and (abs(bbox[1]-bb[0]['y']) <=5)  and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']):
        #      mapping[str(index)] += bx['description']
        #      mapping[str(index)] += " "
        #    elif bbox[0]<=bb[0]['x'] and bbox[1]>=bb[0]['y'] and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']:
        #      mapping[str(index)] += bx['description']
        #      mapping[str(index)] += " "
        #    elif bbox[0]<=bb[0]['x'] and bbox[1]>=bb[0]['y'] and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']:
        #      mapping[str(index)] += bx['description']
        #      mapping[str(index)] += " "
        #    elif bbox[0]<=bb[0]['x'] and bbox[1]>=bb[0]['y'] and bbox[2]>=bb[2]['x'] and bbox[3]<=bb[2]['y']:
        #      mapping[str(index)] += bx['description']
        #      mapping[str(index)] += " "
        #    else:

        chk1 = overlap_calc({"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]},
                            {"x1": bb[0]['x'], "y1": bb[0]['y'], "x2": bb[2]['x'], "y2": bb[2]['y']})

        if (chk1 >= 0.8):
            print(chk1)
            mapping[index] += bx['description']
            mapping[index] += " "
            continue

        chk = get_iou({"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]},
                      {"x1": bb[0]['x'], "y1": bb[0]['y'], "x2": bb[2]['x'], "y2": bb[2]['y']})

        if (chk >= 0.7):
            print("next chk iou")
            print(chk)
            mapping[index] += bx['description']
            mapping[index] += " "
#print(mapping)

#mapping={0: 'HOME CARE ', 1: 'MUKUNDA PRASAD MELAN PADIA ', 2: '9439454006 ', 3: '21GMAPS2777C1Z6 ', 4: 'CASH ', 5: '', 6: '0000165 ', 7: '03/04/2022 ', 8: '19:31 ', 9: '200.05 ', 10: '200.00 ', 11: '38.95 '}