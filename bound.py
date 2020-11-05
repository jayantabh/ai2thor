from ai2thor.controller import Controller
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


# Running Pre-requites
def prepare_data(metadata, event):
    dist = []
    name = []
    objpos = []

    for i in range(len(metadata)):
        dist.append(metadata[i]['distance'])
        name.append(metadata[i]['objectId'])
        objpos.append([metadata[i]['name'], metadata[i]['position']])

    res = dict(zip(name, dist)) 
    p = event.instance_detections2D
    q = list(p.values())
    l = list(p.keys())
    objs = l

    res1 = dict(zip(objs, q)) 
    for i in objs:
        if i not in name:
            del res1[i]

    box = list(res1.values())

    a_sub = {key: res[key] for key in res1}

    mod_name=list(a_sub.keys())
    mod_dist=list(a_sub.values())

    return res1, box, mod_name, mod_dist, objpos


def process_relations(object_ids, relations):
    object_ids_map = {}
    relation_map = defaultdict(set)

    for source, relation, target in relations:
        if source is None or target is None:
            continue

        if source in object_ids_map:
            source_id = object_ids_map[source]
        else:
            object_ids.append(source)
            object_ids_map[source] = len(object_ids) - 1
            source_id = object_ids_map[source]

        if target in object_ids_map:
            target_id = object_ids_map[source]
        else:
            object_ids.append(target)
            object_ids_map[target] = len(object_ids) - 1
            target_id = object_ids_map[target]

        if source_id == target_id:
            continue

        relation_map[relation].add((source_id, target_id))

    return relation_map, object_ids


#'On top and Below Relations'
def top_down(metadata):
    topdown = []

    for i in range(len(metadata)):
        if isinstance(metadata[i]['receptacleObjectIds'], list):
            for rec_object_ids in metadata[i]['receptacleObjectIds']:
                topdown.append(
                    [
                        rec_object_ids,
                        'on top of',
                        metadata[i]['objectId']
                    ]
                )
        else:
            topdown.append(
                [
                    metadata[i]['receptacleObjectIds'],
                    'on top of',
                    metadata[i]['objectId']
                ]
            )

        if isinstance(metadata[i]['parentReceptacles'], list):
            for parent_object_ids in metadata[i]['parentReceptacles']:
                topdown.append(
                    [
                        metadata[i]['objectId'],
                        'on top of',
                        parent_object_ids
                    ]
                )
        else:
            topdown.append(
                [
                    metadata[i]['objectId'],
                    'on top of',
                    metadata[i]['parentReceptacles']
                ]
            )

    return topdown


#'Near and Left/Right Relation'
def near_lr(metadata, objpos):
    near_reldist = []
    far_reldist = []

    for i in range(len(metadata) - 1):
        for j in range(i + 1, len(metadata)):
            distance = np.linalg.norm(np.array(list(objpos[i][1].values())) - np.array(list(objpos[j][1].values())))
            if distance < 0.25:
                if list(objpos[i][1].values())[0] >= list(objpos[j][1].values())[0]:
                    lr = 'left'
                else:
                    lr = 'right'
                near_reldist.append([metadata[i]['objectId'], f'to {lr} of', metadata[j]['objectId']])
            else:
                far_reldist.append([metadata[i]['objectId'], 'far', metadata[j]['objectId']])

    return near_reldist

  
# In-front and Behind Relation
def front_back(metadata, res1, box, mod_name, mod_dist):
    infront_behind = []

    def inter_con(arr1, arr2):
        k = 1
        l = 0
        # If one rectangle is on left side of other 
        if arr1[0] > arr2[2] or arr2[0] > arr1[2]:
            k = 0

        # If one rectangle is above other 
        if arr1[1] > arr2[3] or arr2[1] > arr1[3]:
            k = 0

        # Check if one rectangle is inside another
        if arr1[0] <= arr2[0] <= arr2[2] <= arr1[2] and arr1[3] >= arr2[3] >= arr2[1] >= arr1[1]:
            l = 1

        # Check if one rectangle is inside another
        if arr2[0] <= arr1[0] <= arr1[2] <= arr2[2] and arr2[3] >= arr1[3] >= arr1[1] >= arr2[1]:
            l = 1

        return k, l


    c1 = 0
    c2 = 0
    c3 = 0

    for s in range(len(res1)-1):
        for t in range(s+1, len(res1)):

            j, i = inter_con(box[s], box[t])

            m = 0
            n = 0
            if i == 1:
                # Boxes contain each other

                for p in range(len(metadata)):
                    if metadata[p]['objectId'] == mod_name[s]:

                        if metadata[p]['parentReceptacles']:
                            if mod_name[t] in metadata[p]['parentReceptacles']:
                                m=1

                    if metadata[p]['receptacleObjectIds']:
                        if mod_name[t] in metadata[p]['receptacleObjectIds']:
                            n = 1

                    if m == 0 or n == 0:
                        if mod_dist[s] > mod_dist[t]:
                            infront_behind.append([mod_name[s], 'is behind', mod_name[t]])
                        else:
                            infront_behind.append([mod_name[s], 'is infront', mod_name[t]])
                c1 += 1

            else:
                if j == 0:
                    # Boxes dont intersect nor contain each other

                    c2 += 1

                if j == 1:
                    # Boxes intersect but dont contain each other
                    c3 += 1

                    for p in range(len(metadata)):
                        if metadata[p]['objectId'] == mod_name[s]:
                            if metadata[p]['parentReceptacles']:
                                if mod_name[t] in metadata[p]['parentReceptacles']:
                                    m = 1

                        if metadata[p]['receptacleObjectIds']:
                            if mod_name[t] in metadata[p]['receptacleObjectIds']:
                                n = 1

                        if m == 0 or n == 0:
                            if mod_dist[s] > mod_dist[t]:
                                infront_behind.append([mod_name[s], 'is behind', mod_name[t]])
                            else:
                                infront_behind.append([mod_name[s], 'is in-front of', mod_name[t]])

    print('Number of containing bounding boxes: ', c1)
    print('Number of bounding boxes that dont intersect or contain: ', c2)
    print('Number of bounding boxes that intersect but dont contain: ', c3)
    
    return infront_behind


if __name__ == '__main__':
    controller = Controller(scene='FloorPlan28')
    controller.reset(scene='FloorPlan28')

    event = controller.step(action='MoveAhead', renderObjectImage=True)

    metadata = event.metadata['objects']

    res1, box, mod_name, mod_dist, objpos = prepare_data(metadata, event)

    print('On top and Below Relations')
    tp = top_down(metadata)
    print(tp)

    print('Near and Left/Right Relation')
    nlr = near_lr(metadata, objpos)
    print(nlr)

    print('Infront and Behind Relation')
    fb = front_back(metadata, res1, box, mod_name, mod_dist)
    print(fb)

    # Displaying Bounding Boxes
    # import cv2
    #
    # img = event.frame
    # img = np.array(img)
    #
    # for i in box:
    #       cv2.rectangle(img, (i[0], i[1]), (i[2], i[3]), (255,0,0), 2)
    #
    # imgplot = plt.imshow(img)
    # plt.show()
