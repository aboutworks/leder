import bpy  # Blender Python API

# 清除所有 mesh 物体的材质的函数
def clear_all_materials():
    for obj in bpy.data.objects:
        if obj.type == 'MESH':  # 只处理网格物体
            obj.data.materials.clear()  # 清除材质槽

# 定义一个操作符类，用于在 Blender UI 中调用清除材质功能
class MATERIAL_OT_clear_all(bpy.types.Operator):
    bl_idname = "material.clear_all"  # 操作符唯一标识
    bl_label = "移除所有材质"  # 按钮显示名称
    bl_description = "移除场景中所有物体的材质"  # 鼠标悬停提示

    def execute(self, context):
        clear_all_materials()  # 调用清除材质函数
        self.report({'INFO'}, "已移除所有材质")  # 在 Blender 状态栏显示提示
        return {'FINISHED'}  # 操作完成
