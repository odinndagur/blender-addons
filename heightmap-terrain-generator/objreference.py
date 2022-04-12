"""
[Blender and Python] Creating custom UI panels with Blender's Python API
Mina Pêcheux - September 2021
Email: mina.pecheux@gmail.com
A very basic Blender addon that lets you rename all selected objects
with a given format: <prefix>_<obj name>_<suffix>(-v<version number>).
This code is a simple example of how to create custom UI panels in
Blender using the Python API.
Read the full tutorial on Medium:
https://mina-pecheux.medium.com/creating-a-custom-panel-with-blenders-python-api-b9602d890663
--------
MIT License
Copyright (c) 2021 Mina Pêcheux
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    # required
    'name': 'Object Renamer',
    'blender': (2, 93, 0),
    'category': 'Object',
    # optional
    'version': (1, 0, 0),
    'author': 'Mina Pêcheux',
    'description': 'A quick object renamer to add a prefix, a suffix and an optional version number to the selected objects.',
}

import bpy
import re

# == GLOBAL VARIABLES
PROPS = [
    ('prefix', bpy.props.StringProperty(name='Prefix', default='Pref')),
    ('suffix', bpy.props.StringProperty(name='Suffix', default='Suff')),
    ('add_version', bpy.props.BoolProperty(name='Add Version', default=False)),
    ('version', bpy.props.IntProperty(name='Version', default=1)),
]

# == UTILS
def rename_object(obj, params):
    (prefix, suffix, version, add_version) = params
    
    version_str = '-v{}'.format(version) if add_version else ''
    
    format_regex = r'(?P<prefix>.*)_(?P<main>.*)_(?P<suffix>[^-\n]*)(-v(?P<version>\d+))?'
    match = re.search(format_regex, obj.name)
    # if the object has already been renamed previously,
    # extract the initial name
    if match is not None:
        current_name = match.group('main')
    # else, if it has a "default" name
    else:
        current_name = obj.name
        
    obj.name = '{}_{}_{}{}'.format(prefix, current_name, suffix, version_str)

# == OPERATORS
class ObjectRenamerOperator(bpy.types.Operator):
    
    bl_idname = 'opr.object_renamer_operator'
    bl_label = 'Object Renamer'
    
    def execute(self, context):
        params = (
            context.scene.prefix,
            context.scene.suffix,
            context.scene.version,
            context.scene.add_version
        )
        
        for obj in bpy.context.selected_objects:
            rename_object(obj, params)
            
        return {'FINISHED'}

# == PANELS
class ObjectRenamerPanel(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_object_renamer'
    bl_label = 'Object Renamer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            if prop_name == 'version':
                row = row.row()
                row.enabled = context.scene.add_version
            row.prop(context.scene, prop_name)
            
        col.operator('opr.object_renamer_operator', text='Rename')

# == MAIN ROUTINE
CLASSES = [
    ObjectRenamerOperator,
    ObjectRenamerPanel,
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
        

if __name__ == '__main__':
    register()