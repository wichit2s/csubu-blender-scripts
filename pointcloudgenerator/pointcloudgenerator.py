"""
Copyright 2017 Wichit Sombat

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

bl_info = {
    "name": "Point-Cloud Generator",
    "description": "Simple point-cloud generator",
    "author": "wichit2s",
    "category": "Object",
}

import bpy
from random import randint
import logging
logger = logging.getLogger('PointCloudGenerator')
logger.setLevel(logging.DEBUG)

M = 1000000

class PointCloudGenerator(bpy.types.Operator):
    """Point-Cloud Generator"""
    bl_idname = "object.point_cloud_generator"
    bl_label = "Point-Cloud Generator"
    bl_options = {'REGISTER', 'UNDO'}

    n_points = bpy.props.IntProperty(name="n_points", default=6, min=4, max=100)
    bound_min = bpy.props.FloatProperty(name="bound_min", default=-1, min=-20, max=0)
    bound_max = bpy.props.FloatProperty(name="bound_max", default=1, min=1, max=20)
    add_face = bpy.props.BoolProperty(name="add_face")
    point_size = bpy.props.FloatProperty(name="point_size", default=0.1, min=0.001, max=1)
    point_shape = bpy.props.EnumProperty(
        items=(
            ('0', 'Sphere', 'no shape on vertices'),
            ('1', 'Cube', 'sphere on vertices'),
            ('2', 'None', 'cube on vertices')
        ), 
        name="Point Shape")

    def print_props(self):
        logger.warn("""
            PointCloudGenerator: {{
                "n_points": {},
                "bound": {} <-> {},
                "add_face": {},
                "point_size": {},
                "point_shape": {}
            }}
        """.format(
                self.n_points,
                self.bound_min, self.bound_max,
                self.add_face,
                self.point_size,
                self.point_shape
            )
        )

    def r(self):
        r = randint(0, M)
        return r*(self.bound_max-self.bound_min)/M + self.bound_min

    def execute(self, context):
        scene = context.scene
        self.print_props()
        c = scene.cursor_location

        shapes = {
            '0': lambda x,y,z: 
                bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=8, size=self.point_size, location=[c.x+x, c.y+y, c.z+z])
            ,
            '1': lambda x,y,z:
                bpy.ops.mesh.primitive_cube_add(radius=self.point_size, location=[c.x+x, c.y+y, c.z+z])
            ,
            '2': lambda x,y,z: None
            
        }
        verts = [] 
        for i in range(self.n_points):
            x,y,z = self.r(), self.r(), self.r()
            verts.append( [x, y, z] )
            shapes[self.point_shape](x, y, z)

        bpy.ops.object.add(
            type='MESH',
            enter_editmode=False,
            location=c)
        ob = bpy.context.object
        ob.name = 'Point-Cloud'
        ob.show_name = True
        me = ob.data
        me.name = 'Point-Cloud'+'Mesh'

        faces = [] if not self.add_face else self.connect_surface(verts)
        me.from_pydata(verts, [], faces)
        me.update()
        bpy.ops.object.mode_set(mode='OBJECT')

        #return ob
        return {'FINISHED'}

    def connect_surface(self, verts):
        """Given
        verts = [ [x0,y0,z0], [x1,y1,z1], ..., [xn,yn,zn] ]
        faces = ?
        """
        n = len(verts)
        # Quad
        faces = [ [0,3,2,1] ] #, [3,4,5,2], [5,6,7,4], ... ]
        for i in range(1, (n-4)//2 + 1):
            faces.append( [i*2+1, i*2+2, i*2+3, i*2+0] )
        return faces

def menu_func(self, context):
    self.layout.operator(PointCloudGenerator.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_class(PointCloudGenerator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(PointCloudGenerator.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        kmi.properties.n_points = 6
        kmi.properties.bound_min = -1.0
        kmi.properties.bound_max = 1.0
        kmi.properties.point_size = 0.2 
        kmi.properties.point_shape = '0'
        kmi.properties.add_face = False

        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(PointCloudGenerator)

def invoke(self, context, event):
    wm = context.window_manager
    return wm.invoke_props_dialog(self)

if __name__ == "__main__":
    register()
