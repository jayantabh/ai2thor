from ai2thor.controller import Controller
co = Controller(scene='FloorPlan1',width=512,height=512)
import random
import math
from parse_template import get_object_locations
e = co.step(action='MoveAhead')
m = e.metadata['objects'] 
object_dict = get_object_locations(m,2,'goal')
print(object_dict)

parent = ['Drawer|-01.56|+00.84|+00.20', 'Cabinet|-01.69|+02.02|-02.46', 'Cabinet|-01.55|+00.50|+00.38', 'Cabinet|+00.68|+00.50|-02.20', 'Drawer|+00.95|+00.56|-02.20' , 'Drawer|-01.56|+00.84|+00.20',  'Cabinet|-01.69|+02.02|-02.46', 'Cabinet|-01.55|+00.50|+00.38']
object =  ['Knife|-01.68|+00.79|-00.24', 'Plate|+00.96|+01.65|-02.61', 'Kettle|+01.04|+00.90|-02.60', 'Pan|+00.72|+00.90|-02.42', 'Cup|+00.37|+01.64|-02.58', 'Spatula|+00.38|+00.91|-02.33', 'Bowl|+00.27|+01.10|-00.75', 'Pot|-01.22|+00.90|-02.36']
closeobj = ['None','None','None','None','None','Knife|-01.68|+00.79|-00.24','Plate|+00.96|+01.65|-02.61','Kettle|+01.04|+00.90|-02.60']

#parent = ['Shelf|+01.75|+00.88|-02.56', 'Sink|-01.90|+00.97|-01.50|SinkBasin', 'CounterTop|-00.08|+01.15|00.00', 'Sink|-01.90|+00.97|-01.50|SinkBasin', 'CounterTop|-00.08|+01.15|00.00', 'CounterTop|-00.08|+01.15|00.00','CounterTop|-00.08|+01.15|00.00','Cabinet|-01.55|+00.50|+00.38' ]
#object =  ['Knife|-01.68|+00.79|-00.24', 'Plate|+00.96|+01.65|-02.61', 'Kettle|+01.04|+00.90|-02.60', 'Pan|+00.72|+00.90|-02.42', 'Cup|+00.37|+01.64|-02.58', 'Spatula|+00.38|+00.91|-02.33', 'Bowl|+00.27|+01.10|-00.75', 'Pot|-01.22|+00.90|-02.36']
#closeobj = ['None','None','None','None','None','None','None','None']



for c in range(len(object)):
    objid = object[c]
    parentrec = parent[c]
    closeto = closeobj[c]

    co.step('OpenObject', objectId=parentrec, forceAction='True')
    event = co.step('GetSpawnCoordinatesAboveReceptacle', objectId=parentrec, anywhere=True)
    objpos = event.metadata['actionReturn']
    print('length of objpos', len(objpos))

    cp = []
    metadata = event.metadata['objects']
    for i in range(len(metadata)):
        if metadata[i]['objectId'] == parentrec:
            c = metadata[i]['axisAlignedBoundingBox']['cornerPoints']
        if metadata[i]['objectId'] == objid:
            objbox = metadata[i]['axisAlignedBoundingBox']['cornerPoints']
        if metadata[i]['objectId'] == parentrec:
            recep_objs = metadata[i]['receptacleObjectIds']


    objdim = []
    objdim.append(objbox[0])
    objdim.append(objbox[5])

    objx = objdim[0][0] - objdim[1][0]
    objz = objdim[0][2] - objdim[1][2]
    if objx >= objz:
        margin = objx
    else:
        margin = objz

    print('margin',margin)

    cp.append(c[0])
    cp.append(c[1])
    cp.append(c[4])
    cp.append(c[5])

    xes = []
    zes = []
    for i in range(len(objpos)):
        xes.append(objpos[i]['x'])
        zes.append(objpos[i]['z'])
    x_bound1 = min(xes)+margin/2 
    x_bound2 = max(xes)+margin/2
    z_bound1 = min(zes)+margin/2
    z_bound2 = max(zes)+margin/2 


   # print('xmargin',(cp[0][0]-cp[3][0])/5)
   # print('zmargin',(cp[0][2]-cp[3][2])/5)
   # print('x', cp[0][0]-cp[3][0])
   # print('z', cp[0][2]-cp[3][2])

 ##   print('xlower',cp[3][0])
 ##   print('xhigher',cp[0][0])
 ##   print('zlower',cp[3][2])
 ##   print('zhigher',cp[0][2])

#x_bound1 = cp[3][0] + margin
#x_bound2 = cp[0][0] - margin

#z_bound1 = cp[3][2] + margin
#z_bound2 = cp[0][2] - margin

    valid_pos=[]
    sum=0
    for i in range(len(objpos)):
         if x_bound1 < objpos[i]['x'] < x_bound2 and z_bound1 < objpos[i]['z'] < z_bound2 : 
            sum+=1
            valid_pos.append(objpos[i])

#    print('child recep',recep_objs)
#    m=1
    if parentrec.split('|')[0] != 'Drawer': 
        ind = []
        for i in range(len(recep_objs)):
            for j in range(len(metadata)):
                if metadata[j]['objectId'] == recep_objs[i]:
 
                    recep_obj = []
                    recep_obj_box = metadata[j]['axisAlignedBoundingBox']['cornerPoints']

                    recep_obj.append(recep_obj_box[0])
                    recep_obj.append(recep_obj_box[5])
 
                    for k in range(len(valid_pos)):

                         if recep_obj[1][0]-(margin/2) < valid_pos[k]['x'] < recep_obj[0][0]+(margin/2) and recep_obj[1][2]-(margin/2) < valid_pos[k]['z'] < recep_obj[0][2]+(margin/2):

                             if valid_pos[k] not in ind:
                                 ind.append(valid_pos[k])

        print('length of ind',len(ind))
        print('final length of valid pos', len(valid_pos))
        if ind != None:
           for i in ind:
                valid_pos.remove(i)

    if closeto != 'None':
        for i in range(len(metadata)):
            if metadata[i]['objectId']==closeto:
                closepos = metadata[i]['position']
               # print('closepos',closepos['x'])
               # print('validpos[0]',valid_pos[0])
        distarr = []
        for j in range(len(valid_pos)):
            num = math.sqrt((closepos['x']-valid_pos[j]['x'])**2+(closepos['y']-valid_pos[j]['y'])**2+(closepos['z']-valid_pos[j]['z'])**2)
            distarr.append(num) 
        scamlist = []
        for p in range(len(distarr)):
            scamlist.append([distarr[p],p])
        scamlist.sort()
        sort_index = []
        for q in scamlist:
            sort_index.append(q[1])
        #print(sort_index)
        dummy_pos = []
        for r in sort_index:
            dummy_pos.append(valid_pos[r])
        valid_pos = dummy_pos
#        valid_pos =sorted(valid_pos,key=distarr.get) 

    else:
        random.shuffle(valid_pos)

    nos = len(valid_pos)
    flag=0
    for i in range(len(valid_pos)):
        pos = valid_pos[nos-i-1]
    #print('pos',pos)
        eve = co.step(action = 'PlaceObjectAtPoint', objectId=objid, position=pos, forceAction=True)
        met = eve.metadata['objects']
        for j in range(len(met)):
            if met[j]['objectId'] == parentrec:
                set = met[j]['receptacleObjectIds']
                if set == None:
                    break
                else:
                    for k in set:
                        if k==objid:
                            print('Placed object :',objid) 
                            flag=1
            if flag==1:
                break
        if flag==1:
            break
co.interact()
