import numpy as np
from collections import defaultdict

def attributes(metadata, object_ids):
    attr_map = defaultdict(list)

    object_ids_map = {obj: i for i, obj in enumerate(object_ids)}

    for item in metadata:
        # Salient Material
        object_id = item["objectId"]

        if object_id not in object_ids_map:
            continue

        if item["salientMaterials"] is not None:
            for material in item["salientMaterials"]:
                attr_map[object_ids_map[object_id]].append(material)

        rules = [
            ("breakable", "broken"),
            ("canFillWithLiquid", "filled"),
            ("isDirty", "dirty"),
            ("isCooked", "cooked"),
            ("isOpen", "open",),
            ("pickupable", "can be picked up"),
            ("moveable", "can be moved"),
            ("sliceable", "can be sliced"),
            ("isUsedUp", "has been used")
        ]

        for rule, attr_str in rules:
            if item[rule] is not None and item[rule]:
                attr_map[object_ids_map[object_id]].append(attr_str)

        if item["ObjectTemperature"] == "RoomTemp":
            attr_map[object_ids_map[object_id]].append("room temperature")
        elif item["ObjectTemperature"] == "Hot":
            attr_map[object_ids_map[object_id]].append("high temperature")
        else:
            attr_map[object_ids_map[object_id]].append("low temperature")

        if item["canChangeTempToHot"]:
            attr_map[object_ids_map[object_id]].append("heat source")

        if item["canChangeTempToCold"]:
            attr_map[object_ids_map[object_id]].append("heat sink")

        if not item["pickupable"] and not item["moveable"]:
            continue

        if item["mass"] < 0.5:
            attr_map[object_ids_map[object_id]].append("light")

        if item["mass"] > 0.5:
            attr_map[object_ids_map[object_id]].append("heavy")

    return attr_map
