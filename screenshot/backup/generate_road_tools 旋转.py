import bpy
import bmesh
import math
import mathutils

# ==================== 1. 注册场景属性（仅保留道路模板名称）====================
bpy.types.Scene.i_road_object_name = bpy.props.StringProperty(
    name="直路模板名称",
    description="直路原型对象的名称（需提前在场景中创建）",
    default="i"
)
bpy.types.Scene.l_road_object_name = bpy.props.StringProperty(
    name="L路口模板名称",
    description="L型路口原型对象的名称（需提前在场景中创建）",
    default="l"
)
bpy.types.Scene.x_road_object_name = bpy.props.StringProperty(
    name="十字路模板名称",
    description="十字路原型对象的名称（需提前在场景中创建）",
    default="x"
)
bpy.types.Scene.t_road_object_name = bpy.props.StringProperty(
    name="T型路口模板名称",
    description="T型路口原型对象的名称（需提前在场景中创建）",
    default="t"
)

# ==================== 2. 核心工具函数（精准计算路口朝向）====================
def calculate_vector_angle(v1, v2):
    """计算两向量夹角（角度值）"""
    if v1.length < 0.001 or v2.length < 0.001:
        return 0.0
    v1_norm = v1.normalized()
    v2_norm = v2.normalized()
    dot = max(min(v1_norm.dot(v2_norm), 1.0), -1.0)
    return math.degrees(math.acos(dot))

def is_angle_match(target_angle, actual_angle, threshold=5.0):
    """判断角度是否匹配（±阈值）"""
    return abs(actual_angle - target_angle) <= threshold

def get_junction_main_direction(vert, obj, junction_type):
    """
    针对不同路口类型，精准计算主朝向
    :param vert: 路口中心点顶点
    :param obj: 边缘网格对象
    :param junction_type: 路口类型（L_JUNCTION/T_JUNCTION/CROSS）
    :return: 主朝向向量
    """
    adj_vectors = []
    for edge in vert.link_edges:
        if edge.verts[0] == vert:
            vec = obj.matrix_world @ edge.verts[1].co - obj.matrix_world @ vert.co
        else:
            vec = obj.matrix_world @ edge.verts[0].co - obj.matrix_world @ vert.co
        adj_vectors.append(vec.normalized())  # 归一化方向向量

    if junction_type == "L_JUNCTION":
        # L路口：取两个向量的角平分线方向
        if len(adj_vectors) == 2:
            avg_vec = (adj_vectors[0] + adj_vectors[1]).normalized()
            return avg_vec
    elif junction_type == "T_JUNCTION":
        # T路口：取180°对向的两个向量的平均方向（主干道方向）
        for i in range(len(adj_vectors)):
            for j in range(i+1, len(adj_vectors)):
                angle = calculate_vector_angle(adj_vectors[i], adj_vectors[j])
                if is_angle_match(180, angle):
                    # 主干道方向（两个对向向量的平均）
                    main_vec = (adj_vectors[i] + adj_vectors[j]).normalized()
                    return main_vec
        # 兜底：取最长边方向
        return max(adj_vectors, key=lambda v: v.length) if adj_vectors else mathutils.Vector((1,0,0))
    elif junction_type == "CROSS":
        # 十字路：取X轴方向的对向向量（优先水平主干道）
        for i in range(len(adj_vectors)):
            for j in range(i+1, len(adj_vectors)):
                angle = calculate_vector_angle(adj_vectors[i], adj_vectors[j])
                if is_angle_match(180, angle):
                    # 判断是否为水平方向（X轴）
                    vec = adj_vectors[i]
                    if abs(vec.x) > abs(vec.y):
                        return vec.normalized()
        # 兜底：取第一个向量
        return adj_vectors[0] if adj_vectors else mathutils.Vector((1,0,0))
    elif junction_type == "LINE":
        # 直线：取线段方向
        return adj_vectors[0] if adj_vectors else mathutils.Vector((1,0,0))
    
    # 默认方向
    return mathutils.Vector((1, 0, 0))

def analyze_vert_junction_type(vert, obj):
    """分析单个顶点的路口类型"""
    edge_count = len(vert.link_edges)
    world_co = obj.matrix_world @ vert.co
    
    # 1. 直线端点（仅标记，直线段单独处理）
    if edge_count == 1:
        return "LINE_END", world_co
    
    # 2. 十字路中心点（4条边 + 90°/180°夹角）
    elif edge_count == 4:
        adj_vectors = []
        for edge in vert.link_edges:
            if edge.verts[0] == vert:
                vec = obj.matrix_world @ edge.verts[1].co - world_co
            else:
                vec = obj.matrix_world @ edge.verts[0].co - world_co
            adj_vectors.append(vec)
        
        angles = []
        for i in range(len(adj_vectors)):
            for j in range(i+1, len(adj_vectors)):
                angles.append(calculate_vector_angle(adj_vectors[i], adj_vectors[j]))
        
        has_90 = any(is_angle_match(90, a) for a in angles)
        has_180 = any(is_angle_match(180, a) for a in angles)
        if has_90 and has_180:
            return "CROSS", world_co
    
    # 3. T字路中心点（3条边 + 180°+90°夹角）
    elif edge_count == 3:
        adj_vectors = []
        for edge in vert.link_edges:
            if edge.verts[0] == vert:
                vec = obj.matrix_world @ edge.verts[1].co - world_co
            else:
                vec = obj.matrix_world @ edge.verts[0].co - world_co
            adj_vectors.append(vec)
        
        angles = []
        for i in range(len(adj_vectors)):
            for j in range(i+1, len(adj_vectors)):
                angles.append(calculate_vector_angle(adj_vectors[i], adj_vectors[j]))
        
        has_180 = any(is_angle_match(180, a) for a in angles)
        has_90 = any(is_angle_match(90, a) for a in angles)
        if has_180 and has_90:
            return "T_JUNCTION", world_co
    
    # 4. L路口中心点（2条边 + 90°夹角）
    elif edge_count == 2:
        adj_vectors = []
        for edge in vert.link_edges:
            if edge.verts[0] == vert:
                vec = obj.matrix_world @ edge.verts[1].co - world_co
            else:
                vec = obj.matrix_world @ edge.verts[0].co - world_co
            adj_vectors.append(vec)
        
        if len(adj_vectors) == 2:
            angle = calculate_vector_angle(adj_vectors[0], adj_vectors[1])
            if is_angle_match(90, angle):
                return "L_JUNCTION", world_co
    
    # 未知类型
    return "UNKNOWN", world_co

def instantiate_template_at_location(scene, template_type, location, direction):
    """根据路口类型匹配面板配置的模板，实例化到指定位置并精准对齐方向"""
    # 匹配面板配置的模板名称
    template_name_map = {
        "LINE": scene.i_road_object_name,
        "L_JUNCTION": scene.l_road_object_name,
        "T_JUNCTION": scene.t_road_object_name,
        "CROSS": scene.x_road_object_name
    }
    template_name = template_name_map.get(template_type)
    if not template_name:
        print(f"❌ 无匹配的模板类型：{template_type}")
        return None
    
    # 检查模板是否存在
    if template_name not in bpy.data.objects:
        print(f"❌ 模板「{template_name}」不存在！请先在场景中创建该对象")
        return None
    
    # 关联复制模板（共享数据块，节省内存）
    template_obj = bpy.data.objects[template_name]
    new_obj = template_obj.copy()
    new_obj.data = template_obj.data  # 关联复制（修改原型所有实例同步更新）
    new_obj.name = f"{template_name}_Instance_{len(bpy.data.objects)}"
    
    # 添加到场景
    bpy.context.collection.objects.link(new_obj)
    
    # 设置实例位置
    new_obj.location = location
    
    # 精准旋转对齐方向（沿Z轴）
    if direction.length > 0.001:
        # 计算方向角（与X轴的夹角）
        angle_rad = math.atan2(direction.y, direction.x)
        new_obj.rotation_euler = (0.0, 0.0, angle_rad)
        # 额外优化：T/L路口补充旋转适配拐角
        if template_type == "L_JUNCTION":
            new_obj.rotation_euler.z += math.radians(45)  # L路口旋转45°匹配角平分线
        elif template_type == "T_JUNCTION":
            new_obj.rotation_euler.z += math.radians(0)   # T路口沿主干道方向
    
    print(f"✅ 实例化「{template_name}」→ 位置：({location.x:.2f}, {location.y:.2f})，朝向：{math.degrees(angle_rad):.1f}°")
    return new_obj

def process_straight_segments(scene, obj):
    """处理直线段（取线段方向实例化直路模板）"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    
    # 提取所有直线段（两个端点都是边数=1的顶点）
    straight_edges = []
    for edge in bm.edges:
        v1 = edge.verts[0]
        v2 = edge.verts[1]
        if len(v1.link_edges) == 1 and len(v2.link_edges) == 1:
            straight_edges.append(edge)
    
    # 对每个直线段，按线段方向实例化直路模板
    for edge in straight_edges:
        v1_co = obj.matrix_world @ edge.verts[0].co
        v2_co = obj.matrix_world @ edge.verts[1].co
        mid_co = (v1_co + v2_co) / 2  # 线段中点
        line_dir = (v2_co - v1_co).normalized()  # 线段方向（归一化）
        instantiate_template_at_location(scene, "LINE", mid_co, line_dir)
    
    bm.free()

# ==================== 3. 核心算子：一键生成道路 =====================
class MESH_OT_generate_road_grid(bpy.types.Operator):
    bl_idname = "mesh.generate_road"
    bl_label = "快速生成道路"
    bl_description = "基于选中的边缘网格，自动分析路口并精准对齐道路模板"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        
        # 1. 检查选中对象
        selected_objs = context.selected_objects
        if not selected_objs or selected_objs[0].type != 'MESH':
            self.report({'ERROR'}, "请先选中道路边缘网格（MESH类型）！")
            return {'CANCELLED'}
        
        mesh_obj = selected_objs[0]
        self.report({'INFO'}, f"开始分析道路网格：{mesh_obj.name}")

        # 2. 创建bmesh对象分析顶点
        bm = bmesh.new()
        bm.from_mesh(mesh_obj.data)
        bm.verts.ensure_lookup_table()

        # 3. 遍历顶点，分析路口类型并实例化模板
        processed_verts = []
        for vert in bm.verts:
            if vert in processed_verts:
                continue
            
            # 分析顶点类型
            junction_type, vert_co = analyze_vert_junction_type(vert, mesh_obj)
            
            # 跳过未知类型和直线端点（直线段单独处理）
            if junction_type in ["UNKNOWN", "LINE_END"]:
                continue
            
            # 精准计算路口主朝向
            main_dir = get_junction_main_direction(vert, mesh_obj, junction_type)
            
            # 实例化对应模板
            instantiate_template_at_location(scene, junction_type, vert_co, main_dir)
            processed_verts.append(vert)

        # 4. 处理直线段（单独实例化直路模板）
        process_straight_segments(scene, mesh_obj)

        # 5. 清理资源
        bm.free()
        self.report({'INFO'}, "道路模板实例化完成！所有模板已精准对齐道路朝向")
        
        return {'FINISHED'}