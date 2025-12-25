import bpy
import bmesh
from mathutils import Vector
from bpy.app.translations import pgettext_iface as _  # 翻译函数

# ===================== 运算符类 =====================
class OBJECT_OT_create_grid_faces(bpy.types.Operator):
    """按顶点分布自动计算步长，生成网格面"""
    bl_idname = "object.create_grid_faces"
    bl_label = _("Generate Grid Faces (Auto Step)")
    bl_options = {'REGISTER', 'UNDO'}

    tolerance: bpy.props.FloatProperty(
        name=_("Matching Tolerance"),
        description=_("Tolerance range for coordinate matching"),
        default=0.001,
        min=0.0001,
        max=0.1
    )

    def get_grid_step(self, obj):
        """
        从对象顶点中自动计算X/Y轴的网格步长
        原理：统计顶点坐标差值的最频值作为步长
        """
        # 获取所有顶点的世界坐标
        vert_coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if len(vert_coords) < 2:
            return None, None
        
        # 提取X/Y坐标并去重排序
        x_coords = sorted(list(set([round(v.x, 4) for v in vert_coords])))
        y_coords = sorted(list(set([round(v.y, 4) for v in vert_coords])))
        
        # 计算相邻坐标的差值（步长候选）
        x_steps = []
        for i in range(1, len(x_coords)):
            step = abs(x_coords[i] - x_coords[i-1])
            if step > self.tolerance:
                x_steps.append(step)
        
        y_steps = []
        for i in range(1, len(y_coords)):
            step = abs(y_coords[i] - y_coords[i-1])
            if step > self.tolerance:
                y_steps.append(step)
        
        # 取最频繁出现的步长作为网格步长（处理可能的噪声）
        def get_most_frequent_step(steps):
            if not steps:
                return None
            # 统计步长出现次数
            step_count = {}
            for s in steps:
                rounded_step = round(s, 4)
                step_count[rounded_step] = step_count.get(rounded_step, 0) + 1
            # 返回出现次数最多的步长
            return max(step_count.items(), key=lambda x: x[1])[0]
        
        grid_step_x = get_most_frequent_step(x_steps) or 4.0  # 默认4.0
        grid_step_y = get_most_frequent_step(y_steps) or 4.0  # 默认4.0
        
        return grid_step_x, grid_step_y

    def execute(self, context):
        # 获取选中对象
        obj = context.active_object
        
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, _("Please select a Mesh object first!"))
            return {'CANCELLED'}
        
        self.report({'INFO'}, _("Start processing model: {0}").format(obj.name))
        
        # 自动计算网格步长
        grid_step_x, grid_step_y = self.get_grid_step(obj)
        if not grid_step_x or not grid_step_y:
            self.report({'ERROR'}, _("Cannot calculate grid step, insufficient vertex count!"))
            return {'CANCELLED'}
        
        self.report({'INFO'}, _("Automatically detected step size - X: {0:.2f}, Y: {1:.2f}").format(grid_step_x, grid_step_y))

        # ===================== 核心逻辑 =====================
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 1. 提取所有顶点的世界坐标，并建立 (X,Y) → 顶点索引的映射
        vert_map = {}  # 键：(对齐后的X, 对齐后的Y)，值：顶点索引
        vert_world = []
        
        for v in obj.data.vertices:
            world_co = obj.matrix_world @ v.co
            # 将坐标对齐到步长网格（消除浮点误差）
            x_aligned = round(world_co.x / grid_step_x) * grid_step_x
            y_aligned = round(world_co.y / grid_step_y) * grid_step_y
            vert_map[(x_aligned, y_aligned)] = v.index
            vert_world.append((x_aligned, y_aligned))
        
        # 2. 计算理论网格的范围
        if not vert_world:
            self.report({'ERROR'}, _("Object has no vertices!"))
            return {'CANCELLED'}
        
        min_x = min(v[0] for v in vert_world)
        max_x = max(v[0] for v in vert_world)
        min_y = min(v[1] for v in vert_world)
        max_y = max(v[1] for v in vert_world)
        
        # 3. 进入编辑模式，初始化BMesh
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        
        # 清理原有面
        bmesh.ops.delete(bm, geom=[f for f in bm.faces], context='FACES_ONLY')
        
        # 4. 按步长遍历所有理论网格单元
        faces_created = 0
        x = min_x
        while x < max_x:
            y = min_y
            while y < max_y:
                # 当前单元的4个顶点坐标
                key1 = (x, y)
                key2 = (x + grid_step_x, y)
                key3 = (x + grid_step_x, y + grid_step_y)
                key4 = (x, y + grid_step_y)
                
                # 检查4个顶点是否都存在
                if all(k in vert_map for k in [key1, key2, key3, key4]):
                    try:
                        v1 = bm.verts[vert_map[key1]]
                        v2 = bm.verts[vert_map[key2]]
                        v3 = bm.verts[vert_map[key3]]
                        v4 = bm.verts[vert_map[key4]]
                        bm.faces.new([v1, v2, v3, v4])
                        faces_created += 1
                    except Exception as e:
                        self.report({'WARNING'}, _("Failed to create face at ({0}, {1}): {2}").format(x, y, str(e)))
                        pass
                y += grid_step_y
            x += grid_step_x
        
        # 5. 更新网格并修复法线
        bmesh.update_edit_mesh(obj.data)
        bm.free()
        
        # 统一法线+平滑着色
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        
        # 计算跳过的单元数
        total_units = ((max_x - min_x)/grid_step_x) * ((max_y - min_y)/grid_step_y)
        skipped_units = total_units - faces_created
        
        self.report({'INFO'}, _("✅ Completed! Created {0} faces, skipped {1:.0f} units with missing vertices").format(faces_created, skipped_units))
        return {'FINISHED'}
