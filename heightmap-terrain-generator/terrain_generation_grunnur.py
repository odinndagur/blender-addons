import bpy
import random
from math import sqrt

heightcsv = {
    'brh': '/Users/odinndagur/Blender/2022/islandsdem-modular-heightmap/brh.csv',
    'tif1': '/Users/odinndagur/Blender/2022/islandsdem-modular-heightmap/tif1heightmap.csv'
}
heights = []
with open(heightcsv['brh']) as f:
    for line in f.readlines()[1:]:
        arr = []
        for val in line.split(',')[1:]:
            if val is not None:
                arr.append(float(val.strip()))
            else:
                arr.append(0.0)

        heights.append(arr)
print(len(heights))

def delete_all():
    if bpy.context.object:
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    bpy.ops.object.select_all(action='SELECT')
    # delete all selected objects
    bpy.ops.object.delete()


def setcursor(position):
    x,y,z = position[0], position[1], position[2]
    bpy.context.scene.cursor.location = (x,y,z)


def make_plane(w = 251, h = 251, scale = 0.01, startpos = (0,0,0),xindex=0,yindex=0):
    plane_name = 'x{x}y{y}_plane_width{w}_height{h}_scale{scale}'.format(x=xindex,y=yindex,w=w,h=h,scale=scale)
    print(plane_name)
    xmin = xindex * (w-1)
    ymin = yindex * (h-1)
    edges = []
    faces = []
    
    print('xmin: {xmin}, w: {w}, ymin: {ymin}, h: {h}'.format(xmin=xmin,w=w,ymin=ymin,h=h))
    #print({xmin,xmin+w,ymin,ymin+h})
    
    if(xindex == 9):
        xmin -= 1
    if(yindex == 9):
        ymin -= 1
    vertices = [((x-xmin)*scale,(y-ymin)*scale,heights[x][y]*scale) for x in range(xmin,xmin+w) for y in range(ymin,ymin+h)]
    #print(len(heights),len(heights[2500]))
    vertexIndex = 0
    sz = int(sqrt(len(vertices)))
    for y in range(sz):
        for x in range(sz):
            if (x < sz - 1) and (y < sz - 1):
                # faces.append((vertexIndex,vertexIndex+width+1,vertexIndex+width)) #unity mode
                # faces.append((vertexIndex + width + 1, vertexIndex, vertexIndex+1)) #unity mode
                faces.append((vertexIndex+sz,vertexIndex+sz+1,vertexIndex)) #blender mode
                faces.append((vertexIndex+1, vertexIndex,vertexIndex + sz + 1)) #blender mode
                
            vertexIndex+=1


    new_mesh = bpy.data.meshes.new(plane_name)
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    # make object from mesh
    new_object = bpy.data.objects.new(plane_name, new_mesh)
    # make collection
    new_collection = bpy.data.collections.get('new_collection')
    if not new_collection:
        new_collection = bpy.data.collections.new('new_collection')
        bpy.context.scene.collection.children.link(new_collection)
    new_collection.objects.link(new_object)
    new_object.select_set(True)
    #new_object.location.x -= xindex * scale * 3
    #new_object.location.y -= yindex * scale * 3
    new_object.location = (xindex*w*scale - scale*xindex,yindex*h*scale - scale*yindex,0)



delete_all()
for xp in range(10):
    print(xp)
    for yp in range(10):
        make_plane(xindex=xp,yindex=yp)