bl_info = {
    # required
    'name': 'IslandsDEM terrain generator',
    'blender': (2, 93, 0),
    'category': 'Object',
    # optional
    'version': (1, 0, 0),
    'author': 'ÓDB',
    'description': '',
}

import bpy
import re
from math import sqrt

# == GLOBAL VARIABLES
PROPS = [
    ('row_count', bpy.props.IntProperty(name='Row count', default=1)),
    ('col_count', bpy.props.IntProperty(name='Column count', default=1)),
]

# == UTILS
def generate_collider(obj):
    obj.select_set(True)
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    current_name = obj.name
    if 'collider' in current_name:
        return
    else:
        new_name = current_name + '_collider'
    obj.name = new_name
    obj.modifiers.new('Decimate','DECIMATE')
    obj.modifiers["Decimate"].ratio = 0.05
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Decimate")
    # obj.modifier_apply(modifier="Decimate")

def get_heights_old():
    heightcsv = {
        'brh': '/Users/odinndagur/Blender/2022/islandsdem-modular-heightmap/brh.csv',
        'tif1': '/Users/odinndagur/Blender/2022/islandsdem-modular-heightmap/tif1heightmap.csv'
    }
    heights = []
    with open(heightcsv['tif1']) as f:
        for line in f.readlines()[1:]:
            arr = []
            for val in line.split(',')[1:]:
                if val is not None:
                    arr.append(float(val.strip()))
                else:
                    arr.append(0.0)

            heights.append(arr)
    return heights


def get_heights_new():
    from osgeo import gdal, gdal_array
    import numpy as np
    import pandas as pd
    import os
    from io import StringIO
    print('get_heights_new byrjun')
    heights = []
    filepath = '/Users/odinndagur/Blender/2022/islandsdem-modular-heightmap/data/raw/IslandsDEMv1.0_2x2m_zmasl_isn2016_57.tif' # testa með heilu 25k * 25k tif
    rasterArray = gdal_array.LoadFile(filepath)
    print('rasterarray buid')
    raster = gdal.Open(filepath)
    print('raster buid')
    band = raster.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    heights = np.ma.masked_equal(rasterArray, nodata)
    return heights

def generate_terrain_mesh(row,col):
    heights = get_heights_old()

    w = 251
    h = 251
    scale = 1
    plane_name = 'x{x}y{y}_plane_width{w}_height{h}_scale{scale}'.format(x=col,y=row,w=w,h=h,scale=scale)
    xmin = col * (w-1)
    ymin = row * (h-1)
    edges = []
    faces = []
    
    if(row == 9):
        xmin -= 1
    if(col == 9):
        ymin -= 1
    vertices = [((x-xmin)*scale,(y-ymin)*scale,heights[x][y]*scale) for x in range(xmin,xmin+w) for y in range(ymin,ymin+h)]
    #print(len(heights),len(heights[2500]))

    # make triangle faces
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
    IslandsDEM_collection = bpy.data.collections.get('IslandsDEM')
    if not IslandsDEM_collection:
        IslandsDEM_collection = bpy.data.collections.new('IslandsDEM')
        bpy.context.scene.collection.children.link(IslandsDEM_collection)
    IslandsDEM_collection.objects.link(new_object)
    new_object.select_set(True)
    new_object.location = (col*w*scale - scale*col,row*h*scale - scale*row,0)
    bpy.ops.view3d.view_selected(use_all_regions=False)

# == OPERATORS
class TerrainMeshGenerator(bpy.types.Operator):
    
    bl_idname = 'opr.object_terrain_generator'
    bl_label = 'Terrain Generator'
    
    def execute(self, context):
        for i in range(context.scene.row_count):
            for j in range(context.scene.col_count):
                generate_terrain_mesh(i,j)
            
        return {'FINISHED'}

class MeshColliderGenerator(bpy.types.Operator):
    
    bl_idname = 'opr.object_collider_generator'
    bl_label = 'Mesh collider generator'
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            generate_collider(obj)
        return {'FINISHED'}

# == PANELS
class TerrainGeneratorPanel(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_terrain_generator'
    bl_label = 'Terrain Generator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
            
        col.operator('opr.object_terrain_generator', text='Generate terrain')
        col.operator('opr.object_collider_generator', text='Generate collider')

# == MAIN ROUTINE
CLASSES = [
    TerrainMeshGenerator,
    TerrainGeneratorPanel,
    MeshColliderGenerator,
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    
    for c in CLASSES:
        bpy.utils.register_class(c)

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for c in CLASSES:
        bpy.utils.unregister_class(c)
        

if __name__ == '__main__':
    register()