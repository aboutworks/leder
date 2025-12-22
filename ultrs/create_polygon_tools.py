import bpy
import math
from mathutils import Vector
from bpy.app.translations import pgettext_iface as _

class OBJECT_OT_create_polygon(bpy.types.Operator):
    """Create Equilateral Tetrahedron"""  # 默认英文描述
    bl_idname = "object.create_polygon"
    bl_label = _("Create Equilateral Tetrahedron")  # 默认英文，自动翻译
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        side = 2.0
        h = side * math.sqrt(3) / 2

        verts = [
            Vector((0, 0, 0)),
            Vector((side, 0, 0)),
            Vector((side / 2, h, 0)),
            Vector((side / 2, h / 3, 1.5)),
        ]

        faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]

        mesh = bpy.data.meshes.new("Equilateral_Tetra")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        obj = bpy.data.objects.new("Tetrahedron", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj

        return {'FINISHED'}