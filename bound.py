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

    near_obj = []
    near_raw=list(res1.keys())
    print(near_raw)
    for i in range(len(near_raw)):
        near_obj.append(near_raw[i].split('|')[0])
    print(near_obj) 
    near_box=list(res1.values())
    upd_obj = res1.keys()
    print(len(near_box))
    print(len(near_obj))
    #near_dict = dict(zip(near_obj, q))
    #print(near_box)
    #print(res1)
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
    print(d)
    for i in sorted(d,reverse=True):
        del put[i]

    for i in range(len(put)):
       objpos.append([put[i]['name'],put[i]['position']])

    return supp, put, res1, box, mod_name, mod_dist, objpos, near_box, near_obj


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
       # print(supp[i])
        x_c=[]
        y_c=[]
        z_c=[]

        #if supp[i]['objectOrientedBoundingBox'] != None:
        axisaln = supp[i]['axisAlignedBoundingBox']['cornerPoints']
      #print(len(axisaln))
      #if len(axisaln) > 3 :
        for j in axisaln:
            x_c.append(j[0])
            y_c.append(j[1])
            z_c.append(j[2])
        X_max= max(x_c)
        Y_max= max(y_c)
        Z_max= max(z_c)
        X_min= min(x_c)
        Y_min= min(y_c)
        Z_min= min(z_c)

        if isinstance(supp[i]['receptacleObjectIds'], list):
            for rec_object_ids in supp[i]['receptacleObjectIds']:

                point = None

                for j in range(len(supp)):
                    if supp[j]['objectId'] == rec_object_ids:
                        # point = supp[j]['axisAlignedBoundingBox']['center']
                        point = supp[j]['position']

                        point = list(point.values())
                        print(point)
                        break

                if point is None:
                    continue
                    
                if X_min <= point[0] <= X_max and Y_min <= point[1] <= Y_max  and Z_min <= point[2] <= Z_max:
                    topdown.append(
                    [
                        rec_object_ids,
                        'inside of',
                        supp[i]['objectId']
                    ]
                    )
                else:
                    topdown.append(
                    [
                        rec_object_ids,
                        'on top of',
                        supp[i]['objectId']
                    ]
                    )

      #  else:
      #      topdown.append(
      #          [
      #              supp[i]['receptacleObjectIds'],
      #              'on top of',
      #              supp[i]['objectId']
      #          ]
      #      )

        if isinstance(supp[i]['parentReceptacles'], list):
            for parent_object_ids in supp[i]['parentReceptacles']:
                point1 = None

                for j in range(len(supp)):
                    if supp[j]['objectId'] == parent_object_ids:
                        # point = supp[j]['axisAlignedBoundingBox']['center']
                        point1 = supp[j]['position']

                        point1 = list(point1.values())

                if point1 is None:
                    continue

                if X_min <= point1[0] <= X_max and Y_min <= point1[1] <= Y_max and Z_min <= point1[2] <= Z_max:
                    topdown.append(
                    [
                        supp[i]['objectId'],
                        'inside of',
                        parent_object_ids
                    ]
                    )
                else:
                    topdown.append(
                    [
                        supp[i]['objectId'],
                        'on top of',
                        parent_object_ids
                    ]
                    )
       # else:
       #     topdown.append(
       #         [
       #             supp[i]['objectId'],
       #             'on top of',
       #             supp[i]['parentReceptacles']
       #         ]
       #     )

    return topdown


#'Near and Left/Right Relation'
def near_lr(put, objpos, near_box, near_obj):
    near_reldist = []
    far_reldist = []
#    print(near_box[0])
#    for i in range(len(put) - 1):
#        for j in range(i + 1, len(put)):
#            distance = np.linalg.norm(np.array(list(objpos[i][1].values())) - np.array(list(objpos[j][1].values())))
#            if distance < 0.25:
#               if list(objpos[i][1].values())[0] >= list(objpos[j][1].values())[0]:
#                    lr = 'left'
#                else:
#                    lr = 'right'
#                near_reldist.append([put[i]['objectId'], f'to {lr} of', put[j]['objectId']])
#            else:
#                far_reldist.append([put[i]['objectId'], 'far', put[j]['objectId']])

    for  i in range(len(near_box)):
        for j in range(i+1, len(near_box)):
            #(x1, y1, x1b, y1b), (x2, y2, x2b, y2b)
            x1 = near_box[i][0]
            y1 = near_box[i][1]
            x1b = near_box[i][2]
            y1b = near_box[i][3]
            x2 = near_box[j][0]
            y2 = near_box[j][1]
            x2b = near_box[j][2]
            y2b = near_box[j][3]

            left = x2b < x1
            right = x1b < x2
            bottom = y2b < y1
            top = y1b < y2
            if top and left:
                dist= np.linalg.norm(np.array((x1, y1b))- np.array((x2b, y2)))
                if dist<10:
                    near_reldist.append([near_obj[i], 'is top-left of' , near_obj[j]])
            elif left and bottom:
                dist= np.linalg.norm(np.array((x1, y1))- np.array((x2b, y2b)))
                if dist<10:
                    near_reldist.append([near_obj[i], 'is bottom-right of' , near_obj[j]])  
            elif bottom and right:
                dist= np.linalg.norm(np.array((x1b, y1))- np.array((x2, y2b)))
                if dist<10:
                    near_reldist.append([near_obj[i], 'is bottom-left of' , near_obj[j]])
            elif right and top:
                dist= np.linalg.norm(np.array((x1b, y1b))- np.array((x2, y2)))
                if dist<10:
                    near_reldist.append([near_obj[i], 'is top-right of' , near_obj[j]])
            elif left:
                dist= x1 - x2b
                if dist<10:
                    near_reldist.append([near_obj[i], 'is to right of' , near_obj[j]])
            elif right:
                dist= x2 - x1b
                if dist<10:
                    near_reldist.append([near_obj[i], 'is to left of' , near_obj[j]])
            elif bottom:
                dist= y1 - y2b
                if dist<10:
                    near_reldist.append([near_obj[i], 'is bottom of' , near_obj[j]])
            elif top:
                dist= y2 - y1b
                if dist<10:
                    near_reldist.append([near_obj[i], 'is top of' , near_obj[j]]) 
#            print(dist)
#            if dist < 10:
#                near_reldist.append([near_obj[i], 'near' , near_obj[j]])
#                print('Objects are near')
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
   
    supp, put, res1, box, mod_name, mod_dist, objpos, near_box, near_obj = prepare_data(metadata, event)

    print('On top and Below Relations')
    tp = top_down(supp)
    print(tp)

    print('Near and Left/Right Relation')
    nlr = near_lr(put, objpos, near_box, near_obj)
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