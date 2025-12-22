import bpy

# 楼梯属性挂载到 Scene
bpy.types.Scene.total_height = bpy.props.FloatProperty(
    name="Total Height",
    description="Total height of the staircase (Z axis)",
    default=3.0,
    min=0.1
)

bpy.types.Scene.step_height = bpy.props.FloatProperty(
    name="Step Height",
    description="Height of each step",
    default=0.2,
    min=0.01
)

bpy.types.Scene.step_width = bpy.props.FloatProperty(
    name="Step Width",
    description="Width of each step (X axis)",
    default=1.0,
    min=0.1
)

bpy.types.Scene.step_length = bpy.props.FloatProperty(
    name="Step Length",
    description="Depth of each step (Y axis)",
    default=0.3,
    min=0.1
)

class ULTRS_GENERATE_stairs(bpy.types.Operator):
    """Generate a staircase"""  # 可选说明
    bl_idname = "object.ULTRS_GENERATE_stairs"  # 唯一标识符
    bl_label = "Generate Stairs"           # 面板显示的名字
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        total_height = scene.total_height
        step_height  = scene.step_height
        step_width   = scene.step_width
        step_length  = scene.step_length

        steps_count = int(total_height / step_height)
        if steps_count < 1:
            self.report({'ERROR'}, "Total height too small for step height")
            return {'CANCELLED'}

        # 删除已有楼梯
        for obj in context.scene.objects:
            if obj.get("is_generated_stairs"):
                bpy.data.objects.remove(obj, do_unlink=True)

        # 生成楼梯
        for i in range(steps_count):
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                enter_editmode=False,
                location=(0, i * step_length + step_length / 2, i * step_height + step_height / 2)
            )
            step = context.active_object
            step.scale = (step_width / 2, step_length / 2, step_height / 2)
            step["is_generated_stairs"] = True

        self.report({'INFO'}, f"Generated {steps_count} steps")
        return {'FINISHED'}

class OBJECT_OT_generate_stair_plane(bpy.types.Operator):
    """生成楼梯平面与分线"""
    bl_idname = "object.generate_stair_plane"
    bl_label = "生成楼梯平面"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        width = scene.stair_width
        height = scene.stair_height
        step_w = scene.step_width
        step_h = scene.step_height

        print("=== 开始生成楼梯平面 ===")

        # 删除旧对象
        deleted_count = 0
        for obj in context.scene.objects:
            if obj.get("is_stair_plane"):
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted_count += 1
        print(f"已删除 {deleted_count} 个已有楼梯对象")

        # 1️⃣ 创建平面
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        plane = context.active_object
        plane.name = "楼梯平面"
        plane.scale = (width / 2, 1, height / 2)
        plane["is_stair_plane"] = True
        print(f"已创建平面：{plane.name}，宽度={width}，高度={height}")

        # 2️⃣ 创建分线函数
        def create_line(start, end, name):
            curve_data = bpy.data.curves.new(name, type='CURVE')
            curve_data.dimensions = '3D'
            polyline = curve_data.splines.new('POLY')
            polyline.points.add(1)
            polyline.points[0].co = (*start, 1)
            polyline.points[1].co = (*end, 1)
            curve_obj = bpy.data.objects.new(name, curve_data)
            bpy.context.collection.objects.link(curve_obj)
            curve_obj["is_stair_plane"] = True
            curve_data.bevel_depth = 0.01  # 增加厚度可见
            print(f"生成分线：{name} 从 {start} 到 {end}")

        # 3️⃣ 高度方向分线
        steps_count = int(height / step_h)
        print(f"开始生成 {steps_count-1} 条横向分线（高度方向）")
        for i in range(1, steps_count):
            z = -height / 2 + i * step_h
            create_line((-width / 2, 0, z), (width / 2, 0, z), f"横向线_{i}")

        # 4️⃣ 宽度方向分线
        cols = int(width / step_w)
        print(f"开始生成 {cols-1} 条纵向分线（宽度方向）")
        for i in range(1, cols):
            x = -width / 2 + i * step_w
            create_line((x, 0, -height / 2), (x, 0, height / 2), f"纵向线_{i}")

        print(f"生成完成：共 {steps_count} 阶，{cols} 列分线")
        print("=== 楼梯平面生成结束 ===")
        return {'FINISHED'}