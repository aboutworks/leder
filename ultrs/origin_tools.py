import bpy

class ORIGIN_OT_to_geometry(bpy.types.Operator):
    bl_idname = "origin.to_geometry"
    bl_label = "重置到几何中心"

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                obj.select_set(False)
        self.report({'INFO'}, "所有网格对象轴心点已重置到几何中心")
        return {'FINISHED'}

class ORIGIN_OT_to_mass(bpy.types.Operator):
    bl_idname = "origin.to_mass"
    bl_label = "重置到质心"

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
                obj.select_set(False)
        self.report({'INFO'}, "所有网格对象轴心点已重置到质心")
        return {'FINISHED'}

class ORIGIN_OT_to_cursor(bpy.types.Operator):
    bl_idname = "origin.to_cursor"
    bl_label = "重置到3D光标"

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
                obj.select_set(False)
        self.report({'INFO'}, "所有网格对象轴心点已重置到3D光标")
        return {'FINISHED'}

class ORIGIN_OT_to_volume(bpy.types.Operator):
    bl_idname = "origin.to_volume"
    bl_label = "重置到体积中心"

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
                obj.select_set(False)
        self.report({'INFO'}, "所有网格对象轴心点已重置到体积中心")
        return {'FINISHED'}