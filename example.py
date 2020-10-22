from ai2thor.controller import Controller

# Kitchens: FloorPlan1 - FloorPlan30
# Living rooms: FloorPlan201 - FloorPlan230
# Bedrooms: FloorPlan301 - FloorPlan330
# Bathrooms: FloorPLan401 - FloorPlan430

controller = Controller(scene='FloorPlan28', gridSize=0.25)

event = controller.step(action='MoveAhead')

# Numpy Array - shape (width, height, channels), channels are in RGB order
event.frame

# Numpy Array in BGR order suitable for use with OpenCV
event.cv2image

# current metadata dictionary that includes the state of the scene
event.metadata

# shuts down the controller
controller.stop()

