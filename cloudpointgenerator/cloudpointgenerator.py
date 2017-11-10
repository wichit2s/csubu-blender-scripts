bl_info = {
    "name": "CloudPoint Generator",
    "author": "Wichit Sombat",
    "category": "Object",
}

import bpy


class CloudPointGenerator(bpy.types.Operator):
    """Cloud Point Generator"""
    bl_idname = "object.cloud_point_generator"
    bl_label = "Cloud Point Generator"
    bl_options = {'REGISTER', 'UNDO'}

    total = bpy.props.IntProperty(name="Points", default=6, min=4, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location

        x = 1.0
        verts = ((x,x,-1), (x,-x,-1), (-x,-x,-1), (-x,x,-1), (0,0,1))
        faces = ((1,0,4), (4,2,1), (4,3,2), (4,0,3), (0,1,2,3))

        bpy.ops.object.add(
            type='MESH',
            enter_editmode=False,
            location=(0,0,0))
        ob = bpy.context.object
        ob.name = 'Cloud-Point'
        ob.show_name = True
        me = ob.data
        me.name = 'Cloud-Point'+'Mesh'

        me.from_pydata(verts, [], faces)
        me.update()
        bpy.ops.object.mode_set(mode='OBJECT')

        #return ob
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(CloudPointGenerator.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_class(CloudPointGenerator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(CloudPointGenerator.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        kmi.properties.total = 4
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(CloudPointGenerator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()