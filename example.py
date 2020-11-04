from ai2thor.controller import Controller
from matplotlib import pyplot as plt
import json
import numpy as np


controller = Controller(scene='FloorPlan28', gridSize=0.25, renderObjectImage=True)

event = controller.step(
    'AddThirdPartyCamera',
    rotation=dict(x=45, y=90, z=0),
    position=dict(x=-4, y=1.5, z=-1.5),
    fieldOfView=90
)

center = event.metadata["sceneBounds"]["center"]

controller.interact()

print(center)

bounds = np.array(event.metadata["sceneBounds"]["cornerPoints"])

print(bounds)

x_min = np.amin(bounds[:, 0])
x_max = np.amax(bounds[:, 0])
y_min = np.amin(bounds[:, 1])
y_max = np.amax(bounds[:, 1])
z_min = np.amin(bounds[:, 2])
z_max = np.amax(bounds[:, 2])

y = y_min + 0.9 * y_max - y_min

num_iters = 1


def get_2d_vectors(start, end):
    return np.array([end[0] - start[0], end[1] - start[1]])


def calculate_2d_angle(v1, v2):
    rad = np.arccos((v1 @ v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return rad/np.pi * 180


def look_at(camera_pos, target_pos):
    x_base_vec = np.array((0, z_max - camera_pos[2]))
    x_target_vec = np.array((target_pos[1] - camera_pos[1], target_pos[2] - camera_pos[2]))
    x_angle = calculate_2d_angle(x_base_vec, x_target_vec)

    y_base_vec = np.array((x_max - camera_pos[0], 0))
    y_target_vec = np.array((target_pos[0] - camera_pos[0], target_pos[1] - camera_pos[1]))
    y_angle = calculate_2d_angle(y_base_vec, y_target_vec)

    return x_angle % 180, (90 - y_angle) % 180


for i in range(num_iters):
    x = x_min + np.random.sample() * (x_max - x_min)
    z = z_min + np.random.sample() * (z_max - z_min)

    x_angle, y_angle = look_at([x, y, z], [center['x'], center['y'], center['z']])

    event = controller.step(
        'UpdateThirdPartyCamera',
        thirdPartyCameraId=0,
        rotation=dict(x=0, y=90, z=0.),
        position=dict(x=center['x'], y=center['y'], z=center['z'])
    )

    a = event.third_party_camera_frames

    plt.imshow(a[0])
    plt.show()

    bounding_boxes = event.instance_detections2D

    labels = []
    bb_array = []

    for key in bounding_boxes:
        label = key.split('|')[0]
        labels.append(label)
        bounding_box = bounding_boxes[key]
        bb_array.append(bounding_box)

        print(label, bounding_box)

    with open('metadata.json', 'w') as outfile:
        json.dump(event.metadata, outfile)
