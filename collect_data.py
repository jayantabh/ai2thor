from ai2thor.controller import Controller
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import json
import itertools
import numpy as np
from bound import *
import pickle
import os

REJECT_THRESHOLD = 10
plot_bb = True
facecolor = 'r'
edgecolor = 'None'
alpha = 0.5

controller = Controller(scene='FloorPlan28', gridSize=0.25, renderObjectImage=True, agentControllerType='Physics')

save_path = "dataset/"

event = controller.step('Pass')

# center = event.metadata["sceneBounds"]["center"]
#
# bounds = np.array(event.metadata["sceneBounds"]["cornerPoints"])
#
# x_min = np.amin(bounds[:, 0])
# x_max = np.amax(bounds[:, 0])
# y_min = np.amin(bounds[:, 1])
# y_max = np.amax(bounds[:, 1])
# z_min = np.amin(bounds[:, 2])
# z_max = np.amax(bounds[:, 2])

num_iters = 10

floor_types = [str(i) for i in range(1, 5)]
floor_numbers = ['0' + str(i) for i in range(1, 10)] + [str(i) for i in range(10, 31)]

image_data = {}
image_id = 0

for floor_type in floor_types:
    for floor_number in floor_numbers:
        floor_type = '' if floor_type == '1' else floor_type
        floor_number = floor_number[1:] if floor_type == '' else floor_number
        print(floor_type, floor_number)
        floor = 'FloorPlan' + str(floor_type) + str(floor_number)

        controller.reset(scene=floor)

        for i in range(num_iters):
            # fig, ax = plt.subplots(1)
            print("###########################")
            event = controller.step(action='GetReachablePositions')
            valid_positions = event.metadata['actionReturn']

            idx = np.random.choice(np.arange(0, len(valid_positions)))

            x = valid_positions[idx]['x']
            y = valid_positions[idx]['y']
            z = valid_positions[idx]['z']

            horizon = np.random.normal(loc=2.5, scale=10.0)
            rotation = 180 * np.random.random_sample() - 90

            controller.step(action='InitialRandomSpawn',
                            randomSeed=0,
                            forceVisible=True,
                            numPlacementAttempts=5,
                            placeStationary=True)

            event = controller.step(action='TeleportFull',
                                    x=x,
                                    y=y,
                                    z=z,
                                    rotation=dict(x=0.0, y=rotation, z=0.0),
                                    horizon=horizon)

            metadata = event.metadata['objects']

            # with open('metadata.json', 'w') as outfile:
            #     json.dump(event.metadata, outfile)

            img = event.frame

            bounding_boxes = event.instance_detections2D

            labels = []
            object_ids = []
            bounding_boxes_list = []

            if len(bounding_boxes) <= 10:
                print("Reject Image")
                # plt.imshow(img)
                # plt.show()
            else:
                boxes = []
                # ax.imshow(img)

                for key in bounding_boxes:
                    # label = key.split('|')[0]
                    # labels.append(label)
                    bounding_box = bounding_boxes[key]
                    #
                    # if plot_bb:
                    #     xy = (bounding_box[0], bounding_box[1])
                    #     width = bounding_box[2] - bounding_box[0]
                    #     height = bounding_box[3] - bounding_box[1]
                    #
                    #     rec = Rectangle(xy, width, height, linewidth=1, edgecolor='r', facecolor='none')
                    #     ax.add_patch(rec)

                    object_ids.append(key)
                    bounding_boxes_list.append(bounding_box)

                plt.imsave(os.path.join(save_path, str(floor_type) + str(floor_number) + str(image_id) + '.png'), img)

            res1, box, mod_name, mod_dist, objpos = prepare_data(metadata, event)

            relations = []

            # On top and Below Relations
            tp = top_down(metadata)
            relations.extend(tp)

            # Near and Left/Right Relation
            nlr = near_lr(metadata, objpos)
            relations.extend(nlr)

            # Infront and Behind Relation
            fb = front_back(metadata, res1, box, mod_name, mod_dist)
            relations.extend(fb)

            relations_map, object_ids = process_relations(object_ids, relations)

            image_data[image_id] = (object_ids, bounding_boxes_list, relations_map)
            image_id += 1

with open(os.path.join(save_path, 'data.pickle')) as f:
    pickle.dump(image_data, f)
