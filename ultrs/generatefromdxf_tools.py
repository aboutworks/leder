import bpy
import os

# --------------------------
# 1️⃣ 属性定义
# --------------------------
# DXF 文件路径
bpy.types.Scene.dxf_filepath = bpy.props.StringProperty(
    name="DXF 文件",
    description="选择要导入的 DXF 文件",
    subtype='FILE_PATH'
)

# 楼层高度（浮点数）
bpy.types.Scene.level_height = bpy.props.FloatProperty(
    name="楼层高度",
    description="生成墙体和楼层的高度（米）",
    default=3.0,
    min=0.1
)

# 墙体厚度（浮点数）
bpy.types.Scene.wall_thickness = bpy.props.FloatProperty(
    name="墙体厚度",
    description="墙体厚度（米）",
    default=0.2,
    min=0.01
)

# --------------------------
# 2️⃣ 操作类：生成 3D
# --------------------------
class ULTRS_GENERATE_from_dxf(bpy.types.Operator):
    bl_idname = "object.ULTRS_GENERATE_from_dxf"
    bl_label = "生成 3D 建筑"
    bl_description = "从 DXF 文件生成基础墙体"

    def execute(self, context):
        scene = bpy.context.scene
        filepath = scene.dxf_filepath
        level_height = scene.level_height
        wall_thickness = scene.wall_thickness

        # 1️⃣ 检查 DXF 导入插件是否启用
        if not hasattr(bpy.ops.import_curve, "dxf"):
            self.report({'ERROR'}, "DXF 导入插件未启用，请在 Preferences → Add-ons 启用")
            return {'CANCELLED'}

        # 2️⃣ 检查文件路径
        if not filepath or not os.path.exists(filepath):
            self.report({'ERROR'}, "DXF 文件不存在")
            return {'CANCELLED'}

        # 3️⃣ 导入 DXF
        bpy.ops.import_curve.dxf(filepath=filepath)
        imported_objects = [obj for obj in context.selected_objects if obj.type == 'CURVE']

        if not imported_objects:
            self.report({'ERROR'}, "DXF 文件中没有曲线")
            return {'CANCELLED'}

        # 4️⃣ 生成墙体
        if "Walls" not in bpy.data.collections:
            wall_coll = bpy.data.collections.new("Walls")
            context.scene.collection.children.link(wall_coll)
        else:
            wall_coll = bpy.data.collections["Walls"]

        for curve in imported_objects:
            bpy.context.view_layer.objects.active = curve
            curve.select_set(True)

            # 转 Mesh
            bpy.ops.object.convert(target='MESH')
            mesh_obj = bpy.context.object

            # Solidify 墙厚
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            mesh_obj.modifiers["Solidify"].thickness = wall_thickness
            mesh_obj.modifiers["Solidify"].offset = 0

            # 调整高度
            mesh_obj.scale.z = level_height / mesh_obj.dimensions.z

            # 移动到 Walls 集合
            if mesh_obj.name in context.scene.collection.objects:
                context.scene.collection.objects.unlink(mesh_obj)
            wall_coll.objects.link(mesh_obj)

        self.report({'INFO'}, f"已生成 {len(imported_objects)} 面墙体，高度 {level_height}m，厚度 {wall_thickness}m")
        return {'FINISHED'}
