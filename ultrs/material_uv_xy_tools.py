import bpy
import bmesh
from mathutils import Vector
from bpy.app.translations import pgettext_iface as _

class OBJECT_OT_assign_uv_by_xy_grid(bpy.types.Operator):
    """按XY网格顺序自动分配UV（顶点遍历顺序与UV一一对应）"""
    bl_idname = "object.assign_uv_by_xy_grid"
    bl_label = _("Assign UV by XY Grid")
    bl_options = {'REGISTER', 'UNDO'}

    # 可配置参数（在运算符面板中可调）
    grid_step_x: bpy.props.FloatProperty(
        name=_("Grid Step X"),
        description=_("X-axis grid step size"),
        default=4.0,
        min=0.1,
        max=100.0
    )
    
    grid_step_y: bpy.props.FloatProperty(
        name=_("Grid Step Y"),
        description=_("Y-axis grid step size"),
        default=4.0,
        min=0.1,
        max=100.0
    )
    
    sort_by_y_then_x: bpy.props.BoolProperty(
        name=_("Sort by Y then X"),
        description=_("Sort vertices by Y axis first, then X axis (match traversal order)"),
        default=True
    )
    
    uv_unit_size: bpy.props.FloatProperty(
        name=_("UV Unit Size"),
        description=_("UV size per grid unit (1.0 = square UV)"),
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    uv_map_name: bpy.props.StringProperty(
        name=_("UV Map Name"),
        description=_("Name of the UV map to create/use"),
        default="UVMap_XYGrid"
    )

    def get_sorted_vertex_data(self, obj):
        """提取顶点数据并按指定顺序排序（核心逻辑）"""
        vertex_data = []
        for v_idx, v in enumerate(obj.data.vertices):
            # 转换为世界坐标
            world_co = obj.matrix_world @ v.co
            # 对齐到网格步长（消除浮点误差）
            x_aligned = round(world_co.x / self.grid_step_x) * self.grid_step_x
            y_aligned = round(world_co.y / self.grid_step_y) * self.grid_step_y
            
            vertex_data.append({
                'index': v_idx,          # 顶点原始索引
                'world_co': world_co,    # 世界坐标
                'x': x_aligned,          # 对齐后的X
                'y': y_aligned,          # 对齐后的Y
                'z': world_co.z          # Z轴（保留）
            })
        
        # 按指定顺序排序（先Y后X 或 先X后Y）
        if self.sort_by_y_then_x:
            vertex_data.sort(key=lambda d: (d['y'], d['x']))
        else:
            vertex_data.sort(key=lambda d: (d['x'], d['y']))
        
        return vertex_data

    def execute(self, context):
        # 获取选中对象
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, _("Please select a mesh object first!"))
            return {'CANCELLED'}
        
        self.report({'INFO'}, _("Start assigning UV by XY grid: {0}").format(obj.name))

        # 1. 提取并排序顶点数据
        vertex_data = self.get_sorted_vertex_data(obj)
        if not vertex_data:
            self.report({'ERROR'}, _("Object has no vertices!"))
            return {'CANCELLED'}
        
        # 2. 计算网格行列信息
        unique_y = sorted(list(set([d['y'] for d in vertex_data])))
        unique_x = sorted(list(set([d['x'] for d in vertex_data])))
        row_count = len(unique_y)
        col_count = len(unique_x)
        self.report({'INFO'}, _("Grid dimensions: {0} rows × {1} columns").format(row_count, col_count))
        
        # 建立行列映射
        y_to_row = {y: idx for idx, y in enumerate(unique_y)}
        x_to_col = {x: idx for idx, x in enumerate(unique_x)}

        # 3. 进入编辑模式，初始化BMesh和UV层
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        
        # 创建/激活指定名称的UV层
        if self.uv_map_name in bm.loops.layers.uv:
            uv_layer = bm.loops.layers.uv[self.uv_map_name]
        else:
            uv_layer = bm.loops.layers.uv.new(self.uv_map_name)
        bm.loops.layers.uv.active = uv_layer
        bm.verts.ensure_lookup_table()

        # 4. 核心：为每个顶点分配UV（严格匹配遍历顺序）
        uv_assign_count = 0
        for sorted_idx, v_data in enumerate(vertex_data):
            # 计算行列号和UV坐标
            row = y_to_row[v_data['y']]
            col = x_to_col[v_data['x']]
            u = col * self.uv_unit_size
            v = row * self.uv_unit_size
            
            # 为顶点的所有环分配UV
            bm_vert = bm.verts[v_data['index']]
            for loop in bm_vert.link_loops:
                loop[uv_layer].uv = (u, v)
                uv_assign_count += 1

        # 5. 更新网格并清理
        bmesh.update_edit_mesh(obj.data)
        bm.free()

        # 6. UV优化：对齐到网格+统一缩放
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.snap_selected(target='GRID')
        bpy.ops.uv.average_islands_scale()
        bpy.ops.object.mode_set(mode='OBJECT')

        # 7. 输出验证信息
        self.report({'INFO'}, _("✅ UV assignment completed! Assigned UV to {0} loops").format(uv_assign_count))
        
        # 打印前10个顶点的匹配信息（调试用）
        self.report({'INFO'}, _("\nTop 10 vertices UV mapping:"))
        self.report({'INFO'}, _("Traversal | Vertex | XY Coord     | UV Coord     | Row/Col"))
        for i in range(min(10, len(vertex_data))):
            v_data = vertex_data[i]
            row = y_to_row[v_data['y']]
            col = x_to_col[v_data['x']]
            u = col * self.uv_unit_size
            v = row * self.uv_unit_size
            info = f"{i+1:6d} | {v_data['index']:6d} | ({v_data['x']:.0f},{v_data['y']:.0f}) | ({u:.1f},{v:.1f}) | R{row}C{col}"
            self.report({'INFO'}, info)

        return {'FINISHED'}
