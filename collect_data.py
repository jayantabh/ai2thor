from ai2thor.controller import Controller
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import json
import itertools
import numpy as np
from bound import *
from relations import *
from attributes import *
import pickle
import os

REJECT_THRESHOLD = 12
NUM_VALID_POSITIONS = 5
plot_bb = True
facecolor = 'r'
edgecolor = 'None'
alpha = 0.5

INVALID_OBJECTS = set(
    'cube.001'
)

controller = Controller(
    scene='FloorPlan1',
    width=256,
    height=256,
    gridSize=0.05,
    renderObjectImage=True,
    agentControllerType='Physics',
    fieldOfView='120'
)

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
num_iters_surfaces = 5

surface_types = [
    'CoffeeTable',
    'DiningTable',
    'SideTable',
    'Sink',
    'Sofa',
    'CounterTop',
    'StoveBurner'
]

floor_types = [str(i) for i in range(1, 5)] # 1, 5
floor_numbers = ['0' + str(i) for i in range(1, 5)] + [str(i) for i in range(10, 31)] # 1, 10
# floor_types = [floor_types[0]]
# floor_numbers = [floor_numbers[0]]

image_data = {}
image_id = 0
on_below_len=0
left_right_len=0
front_back_len=0

for floor_type in floor_types:
    for floor_number in floor_numbers:
        floor_type = '' if floor_type == '1' else floor_type
        floor_number = floor_number[1:] if floor_type == '' and int(floor_number) < 10 else floor_number
        print(f"Floor Type: {floor_type}, Floor Number: {floor_number}")
        floor = 'FloorPlan' + str(floor_type) + str(floor_number)

        controller.reset(scene=floor)

        # for i in range(num_iters):
        #     # fig, ax = plt.subplots(1)
        #     print("###########################")
        #     event = controller.step(action='GetReachablePositions')
        #     valid_positions = event.metadata['actionReturn']
        #
        #     print(valid_positions)
        #
        #     idx = np.random.choice(np.arange(0, len(valid_positions)))
        #
        #     x = valid_positions[idx]['x']
        #     y = valid_positions[idx]['y']
        #     z = valid_positions[idx]['z']
        #
        #     horizon = np.random.normal(loc=2.5, scale=10.0)
        #     rotation = 180 * np.random.random_sample() - 90
        #
        #     controller.step(action='InitialRandomSpawn',
        #                     randomSeed=0,
        #                     forceVisible=True,
        #                     numPlacementAttempts=5,
        #                     placeStationary=True)
        #
        #     event = controller.step(action='TeleportFull',
        #                             x=x,
        #                             y=y,
        #                             z=z,
        #                             rotation=dict(x=0.0, y=rotation, z=0.0),
        #                             horizon=horizon)
        #
        #     metadata = event.metadata['objects']
        #
        #     with open('metadata.json', 'w') as outfile:
        #         json.dump(event.metadata, outfile)
        #
        #     img = event.frame
        #
        #     bounding_boxes = event.instance_detections2D
        #
        #     labels = []
        #     object_ids = []
        #     bounding_boxes_list = []
        #
        #     if len(bounding_boxes) <= REJECT_THRESHOLD:
        #         print("Reject Image")
        #         continue
        #
        #     boxes = []
        #     # ax.imshow(img)
        #
        #     for key in bounding_boxes:
        #         # label = key.split('|')[0]
        #         # labels.append(label)
        #
        #         bounding_box = bounding_boxes[key]
        #
        #         # if plot_bb:
        #         #     xy = (bounding_box[0], bounding_box[1])
        #         #     width = bounding_box[2] - bounding_box[0]
        #         #     height = bounding_box[3] - bounding_box[1]
        #         #
        #         #     rec = Rectangle(xy, width, height, linewidth=1, edgecolor='r', facecolor='none')
        #         #     ax.add_patch(rec)
        #
        #         object_ids.append(key)
        #         bounding_boxes_list.append(bounding_box)
        #
        #     plt.imsave(os.path.join(save_path, str(floor_type) + str(floor_number) + '_' + str(image_id) + '.png'), img)
        #
        #     res1, box, mod_name, mod_dist, objpos = prepare_data(metadata, event)
        #
        #     relations = []
        #
        #     # On top and Below Relations
        #     tp = top_down(metadata)
        #     relations.extend(tp)
        #
        #     # Near and Left/Right Relation
        #     nlr = near_lr(metadata, objpos)
        #     relations.extend(nlr)
        #
        #     # Infront and Behind Relation
        #     fb = front_back(metadata, res1, box, mod_name, mod_dist)
        #     relations.extend(fb)
        #
        #     has = has_relations(metadata, inc=0.1)
        #     relations.extend(has)
        #
        #     relations_map = process_relations(object_ids, relations)
        #
        #     image_data[image_id] = (object_ids, bounding_boxes_list, relations_map)
        #
        #     for key in relations_map:
        #         for o1, o2 in relations_map[key]:
        #             print(key, object_ids[o1], object_ids[o2])
        #
        #     image_id += 1

        event = controller.step("Pass")
        metadata = event.metadata['objects']
        surface_locations = []

        for object_data in metadata:
            if object_data['objectType'] in surface_types:
                surface_locations.append((object_data['position'], object_data['axisAlignedBoundingBox']['size']))

        for surface_center, size in surface_locations:
            controller.reset(scene=floor)

            if surface_center is None or size is None:
                continue

            locations = [surface_center]

            for k in range(num_iters_surfaces):
                r = np.random.random(3)
                x_r = surface_center['x'] + (r[0] - 0.5) * size['x']
                y_r = surface_center['y'] + (r[1] - 0.5) * size['y']
                z_r = surface_center['x'] + (r[2] - 0.5) * size['z']

                locations.append({'x': x_r, 'y': y_r, 'z': z_r})

            for location in locations:

                # fig, ax = plt.subplots(1)
                print(f"######################################################  {image_id} "
                      f"######################################################")
                event = controller.step(action='GetReachablePositions')
                valid_positions = event.metadata['actionReturn']
                agent_location = event.metadata['agent']['position']

                if valid_positions is None:
                    continue

                position_distance = []

                for position in valid_positions:
                    position_distance.append(distance(position, location))

                position_distance = np.array(position_distance)

                best_positions = position_distance.argsort()[:min(NUM_VALID_POSITIONS, len(valid_positions))]

                use_position = valid_positions[best_positions[np.random.randint(0, best_positions.shape[0])]]

                horizon = np.random.normal(loc=2.5, scale=10.0)
                rotation = get_angle_to_look_at(
                    (
                        location['x'],
                        location['z']
                    ),
                    (
                        agent_location['x'],
                        agent_location['z']
                    )
                )

                x, y, z = use_position['x'], use_position['y'], use_position['z']

                seed = np.random.randint(100000)

                controller.step(action='InitialRandomSpawn',
                                randomSeed=seed,
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

                with open('metadata.json', 'w') as outfile:
                    json.dump(event.metadata, outfile)

                img = event.frame

                bounding_boxes = event.instance_detections2D

                labels = []
                object_ids = []
                bounding_boxes_list = []

                # if len(bounding_boxes) <= REJECT_THRESHOLD:
                #     print("Reject Image")
                #     continue

                boxes = []
                # ax.imshow(img)
                # plt.show()

                for key in bounding_boxes:
                    print(key)
                    bounding_box = bounding_boxes[key]

                    print(bounding_box)

                    if key.split('.')[0] in INVALID_OBJECTS:
                        continue

                    object_ids.append(key)
                    bounding_boxes_list.append(bounding_box)

                images_path = os.path.join(save_path, 'images/')

                if not os.path.exists(images_path):
                    os.mkdir(images_path)

                plt.imsave(
                    os.path.join(
                        images_path,
                        str(floor_type) + str(floor_number) + '_' + str(image_id) + '.png'
                    ),
                    img
                )

                print(image_id)
                print(str(floor_type) + str(floor_number) + '_' + str(image_id) + '.png')

                supp, put, res1, box, mod_name, mod_dist, objpos, near_box, near_obj = prepare_data(metadata, event)

                relations = []

                # On top and Below Relations
                on_below = top_down(supp)
                relations.extend(on_below)
                on_below_len = on_below_len + len(on_below)

                
                # Near and Left/Right Relation
                left_right = near_lr(put, objpos, near_box, near_obj)
                relations.extend(left_right)
                left_right_len = left_right_len + len(left_right)

                
                # Infront and Behind Relation
                front_back = front_back(supp, res1, box, mod_name, mod_dist)
                relations.extend(front_back)
                front_back_len = front_back_len+len(front_back)

                
                has = has_relations(metadata, inc=0.1)
                relations.extend(has)

                relations_map = process_relations(object_ids, relations)

                attr_map = attributes(metadata, object_ids)

                image_data[image_id] = (object_ids, bounding_boxes_list, relations_map, attr_map)

                for key in relations_map:
                    for o1, o2 in relations_map[key]:
                        print(key, object_ids[o1], object_ids[o2])

                for object_id in attr_map:
                    print(object_id, attr_map[object_id])

                image_id += 1

print('Total images captured :', image_id)
print('Number of top-below relation :', on_below_len)
print('Number of near- left/right relation :', left_right_len)
print('Number of front-back relation :', front_back_len)
print('Density for top-below relation :', float(on_below_len/image_id))
print('Density for near- left/right relation :', float(left_right_len/image_id))
print('Density for front-back relation :', float(front_back_len/image_id))

with open(os.path.join(save_path, 'data.pickle'), 'wb') as f:
    pickle.dump(image_data, f)