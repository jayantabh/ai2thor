from ai2thor.controller import Controller
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


# Running Pre-requites
def prepare_data(metadata, event):
    dist = []
    name = []
    objpos = []
    inin=[]
    for i in range(len(metadata)):
        inin.append(metadata[i]['objectId'])
   
    supp = metadata
   
    p = event.instance_detections2D
    q = list(p.values())
    objs = list(p.keys())

    res1 = dict(zip(objs, q))
    for i in objs:
        if i not in inin:
            del res1[i]
 
    upd_obj = res1.keys()

    ind = []
    for j in range(len(metadata)):
        i = metadata[j]['objectId']
        if i not in upd_obj:
            ind.append(j)    
    for i in sorted(ind,reverse=True):
        del supp[i]
 
    for i in range(len(supp)):
        dist.append(supp[i]['distance'])
        name.append(supp[i]['objectId'])

    res = dict(zip(name, dist))

    box = list(res1.values())

    a_sub = {key: res[key] for key in res1}

    mod_name=list(a_sub.keys())
    mod_dist=list(a_sub.values())
    d=[]
    put = supp
    search = ['Bed','CounterTop','DiningTable','Floor','ShelvingUnit','StoveBurner']
    for i in search:
      for j in range(len(put)):
        if put[j]['objectType'] == i:
           d.append(j)
    for i in sorted(d,reverse=True):
        del put[i]

    for i in range(len(put)):
       objpos.append([put[i]['name'],put[i]['position']])


    return supp, put, res1, box, mod_name, mod_dist, objpos


def process_relations(object_ids, relations):
    object_ids_map = {}
    relation_map = defaultdict(set)

    for i in range(len(object_ids)):
        object_ids_map[object_ids[i]] = i

    for source, relation, target in relations:
        if source is None or target is None:
            continue

        if source in object_ids_map:
            source_id = object_ids_map[source]
        else:
            # object_ids.append(source)
            # object_ids_map[source] = len(object_ids) - 1
            # source_id = object_ids_map[source]
            source_id = None

        if target in object_ids_map:
            target_id = object_ids_map[target]
        else:
            # object_ids.append(target)
            # object_ids_map[target] = len(object_ids) - 1
            # target_id = object_ids_map[target]
            target_id = None

        if source_id is None or target_id is None or source_id == target_id:
            continue

        relation_map[relation].add((source_id, target_id))

    return relation_map


#'On top and Below Relations'
def top_down(supp):
    topdown = []

    for i in range(len(supp)):
        if isinstance(supp[i]['receptacleObjectIds'], list):
            for rec_object_ids in supp[i]['receptacleObjectIds']:
                topdown.append(
                    [
                        rec_object_ids,
                        'on top of',
                        supp[i]['objectId']
                    ]
                )
        else:
            topdown.append(
                [
                    supp[i]['receptacleObjectIds'],
                    'on top of',
                    supp[i]['objectId']
                ]
            )

        if isinstance(supp[i]['parentReceptacles'], list):
            for parent_object_ids in supp[i]['parentReceptacles']:
                topdown.append(
                    [
                        supp[i]['objectId'],
                        'on top of',
                        parent_object_ids
                    ]
                )
        else:
            topdown.append(
                [
                    supp[i]['objectId'],
                    'on top of',
                    supp[i]['parentReceptacles']
                ]
            )

    return topdown


#'Near and Left/Right Relation'
def near_lr(put, objpos):
    near_reldist = []
    far_reldist = []

    for i in range(len(put) - 1):
        for j in range(i + 1, len(put)):
            distance = np.linalg.norm(np.array(list(objpos[i][1].values())) - np.array(list(objpos[j][1].values())))
            if distance < 0.25:
                if list(objpos[i][1].values())[0] >= list(objpos[j][1].values())[0]:
                    lr = 'left'
                else:
                    lr = 'right'
                near_reldist.append([put[i]['objectId'], f'to {lr} of', put[j]['objectId']])
            else:
                far_reldist.append([put[i]['objectId'], 'far', put[j]['objectId']])

    return near_reldist

 
# In-front and Behind Relation
def front_back(supp, res1, box, mod_name, mod_dist):
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

                for p in range(len(supp)):
                    if supp[p]['objectId'] == mod_name[s]:

                        if supp[p]['parentReceptacles']:
                            if mod_name[t] in supp[p]['parentReceptacles']:
                                m=1

                        if supp[p]['receptacleObjectIds']:
                            if mod_name[t] in supp[p]['receptacleObjectIds']:
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

                    for p in range(len(supp)):
                        if supp[p]['objectId'] == mod_name[s]:
                            if supp[p]['parentReceptacles']:
                                if mod_name[t] in supp[p]['parentReceptacles']:
                                    m = 1

                            if supp[p]['receptacleObjectIds']:
                                if mod_name[t] in supp[p]['receptacleObjectIds']:
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
   
    supp, put, res1, box, mod_name, mod_dist, objpos = prepare_data(metadata, event)

    print('On top and Below Relations')
    tp = top_down(supp)
    print(tp)

    print('Near and Left/Right Relation')
    nlr = near_lr(put, objpos)
    print(nlr)

    print('Infront and Behind Relation')
    fb = front_back(supp, res1, box, mod_name, mod_dist)
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