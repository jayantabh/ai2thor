from ai2thor.controller import Controller
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


def get_angle_to_look_at(point, agent_location):
    base_vector = (0, 1)
    req_vector = (point[0] - agent_location[0], point[1] - agent_location[1])

    dot = base_vector[0] * req_vector[0] + base_vector[1] * req_vector[1]
    det = base_vector[0] * req_vector[1] - base_vector[1] * req_vector[0]

    return np.arctan2(det, dot) * 180 / np.pi


def distance(p1, p2):
    return np.sqrt((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2 + (p1['z'] - p2['z']) ** 2)


def point_inside_aabb(point, extents):
    return extents[0][0] <= point[0] <= extents[0][1] and \
           extents[1][0] <= point[1] <= extents[1][1] and \
           extents[2][0] <= point[2] <= extents[2][1]


def has_relations(metadata, inc=0.05):
    relations = []

    for i in range(len(metadata)):
        for j in range(len(metadata)):
            if i == j:
                continue

            parent_object = metadata[i]
            child_object = metadata[j]

            if parent_object['objectId'] == child_object['objectId']:
                continue

            parent_object_corners = parent_object['axisAlignedBoundingBox']['cornerPoints']
            parent_object_center = parent_object['axisAlignedBoundingBox']['center']
            child_object_corners = child_object['axisAlignedBoundingBox']['cornerPoints']

            if parent_object_corners is None or parent_object_center is None:
                continue

            if child_object_corners is None:
                continue

            if child_object['parentReceptacles'] is not None and \
                    parent_object['objectId'] in child_object['parentReceptacles']:
                continue

            if child_object['objectType'] == parent_object['objectType']:
                continue

            min_x, min_y, min_z = np.inf, np.inf, np.inf
            max_x, max_y, max_z = - np.inf, - np.inf, - np.inf

            for point in parent_object_corners:
                x = point[0] + inc * (point[0] - parent_object_center['x'])
                y = point[1] + inc * (point[1] - parent_object_center['y'])
                z = point[2] + inc * (point[2] - parent_object_center['z'])
                min_x, min_y, min_z = min(min_x, x), min(min_y, y), min(min_z, z)
                max_x, max_y, max_z = max(max_x, x), max(max_y, y), max(max_z, z)

            extents = [(min_x, max_x), (min_y, max_y), (min_z, max_z)]

            point_inside = []

            for corner in child_object_corners:
                point_inside.append(point_inside_aabb(corner, extents))

            if not all(point_inside) or not child_object['visible']:
                continue

            print(point_inside)
            print(f"Parent Object: {parent_object['objectId']}")
            print(f"Child Object: {child_object['objectId']}")
            print(extents)
            print(child_object_corners)

            relations.append(
                [
                    parent_object["objectId"],
                    "has",
                    child_object["objectId"]
                ]
            )

    return relations

if __name__ == "__main__":
    print(get_angle_to_look_at())