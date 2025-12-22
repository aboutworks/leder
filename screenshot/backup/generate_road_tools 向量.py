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

# ==================== 2. 核心工具函数（直接获取端点边缘线朝向）====================
def get_edge_raw_direction(edge, obj):
    """
    获取单条边缘线的原始朝向（从中心点到端点的向量）
    :param edge: 边缘线对象
    :param obj: 边缘网格对象
    :return: 边缘线的原始朝向向量（归一化）
    """
    # 取边缘线的两个顶点世界坐标
    v1_co = obj.matrix_world @ edge.verts[0].co
    v2_co = obj.matrix_world @ edge.verts[1].co
    # 计算边缘线的方向向量（v1→v2）
    edge_dir = (v2_co - v1_co).normalized()
    return edge_dir

def get_junction_edge_directions(vert, obj):
    """
    获取路口中心点所有关联边缘线的原始朝向（从中心点到各端点）
    :param vert: 路口中心点顶点
    :param obj: 边缘网格对象
    :return: 所有边缘线的原始朝向列表 + 中心点世界坐标
    """
    center_co = obj.matrix_world @ vert.co  # 路口中心点坐标
    edge_directions = []
    
    # 遍历中心点关联的所有边缘线
    for edge in vert.link_edges:
        # 找到边缘线的端点（非中心点的那个顶点）
        if edge.verts[0] == vert:
            end_vert = edge.verts[1]
        else:
            end_vert = edge.verts[0]
        
        # 计算「中心点→端点」的原始朝向向量
        end_co = obj.matrix_world @ end_vert.co
        edge_dir = (end_co - center_co).normalized()
        edge_directions.append(edge_dir)
    
    return edge_directions, center_co

def analyze_vert_junction_type(vert):
    """仅根据边数判断路口类型（简化逻辑，专注朝向）"""
    edge_count = len(vert.link_edges)
    if edge_count == 1:
        return "LINE_END"
    elif edge_count == 2:
        return "L_JUNCTION"
    elif edge_count == 3:
        return "T_JUNCTION"
    elif edge_count == 4:
        return "CROSS"
    else:
        return "UNKNOWN"

def rotate_template_to_edge_direction(obj, target_dir):
    """
    将对象旋转到指定边缘线的朝向（核心：精准匹配原始边缘线方向）
    :param obj: 要旋转的模板对象
    :param target_dir: 目标边缘线朝向向量（归一化）
    """
    # 计算目标朝向与X轴的夹角（核心：直接用边缘线原始向量计算）
    target_angle = math.atan2(target_dir.y, target_dir.x)
    # 设置对象旋转（仅沿Z轴旋转，保持XY平面）
    obj.rotation_euler = (0.0, 0.0, target_angle)
    return target_angle

def instantiate_template(scene, junction_type, center_co, edge_directions):
    """
    实例化模板并精准匹配边缘线朝向
    :param junction_type: 路口类型（L_JUNCTION/T_JUNCTION/CROSS/LINE）
    :param center_co: 路口中心点坐标
    :param edge_directions: 所有关联边缘线的原始朝向列表
    """
    # 匹配模板名称
    template_name_map = {
        "LINE": scene.i_road_object_name,
        "L_JUNCTION": scene.l_road_object_name,
        "T_JUNCTION": scene.t_road_object_name,
        "CROSS": scene.x_road_object_name
    }
    template_name = template_name_map.get(junction_type)
    if not template_name or template_name not in bpy.data.objects:
        print(f"❌ 模板「{template_name}」不存在！")
        return None

    # 关联复制模板
    template_obj = bpy.data.objects[template_name]
    new_obj = template_obj.copy()
    new_obj.data = template_obj.data
    new_obj.name = f"{template_name}_Instance_{len(bpy.data.objects)}"
    bpy.context.collection.objects.link(new_obj)
    new_obj.location = center_co

    # ========== 核心：根据路口类型，选择对应边缘线的朝向进行匹配 ==========
    if junction_type == "T_JUNCTION":
        # T型口：选择最长的那条边缘线（主干道）的朝向
        main_edge_dir = max(edge_directions, key=lambda v: v.length)
        angle = rotate_template_to_edge_direction(new_obj, main_edge_dir)
        print(f"📌 T型口匹配：沿主干道边缘线朝向旋转 {math.degrees(angle):.1f}°")
    
    elif junction_type == "L_JUNCTION":
        # L型口：选择第一条边缘线的朝向（贴合其中一条边缘）
        main_edge_dir = edge_directions[0]
        angle = rotate_template_to_edge_direction(new_obj, main_edge_dir)
        print(f"📌 L型口匹配：沿边缘线朝向旋转 {math.degrees(angle):.1f}°")
    
    elif junction_type == "CROSS":
        # 十字口：选择水平方向（X轴绝对值最大）的边缘线朝向
        horizontal_dir = max(edge_directions, key=lambda v: abs(v.x))
        angle = rotate_template_to_edge_direction(new_obj, horizontal_dir)
        print(f"📌 十字口匹配：沿水平边缘线朝向旋转 {math.degrees(angle):.1f}°")
    
    elif junction_type == "LINE":
        # 直线：直接匹配线段朝向
        line_dir = edge_directions[0] if edge_directions else mathutils.Vector((1,0,0))
        angle = rotate_template_to_edge_direction(new_obj, line_dir)
        print(f"📌 直线匹配：沿边缘线朝向旋转 {math.degrees(angle):.1f}°")

    return new_obj

def process_junction_verts(obj, scene):
    """处理所有路口顶点，提取边缘线朝向并实例化模板"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    processed_verts = []

    for vert in bm.verts:
        if vert in processed_verts:
            continue
        
        # 1. 判断路口类型（仅根据边数）
        junction_type = analyze_vert_junction_type(vert)
        if junction_type in ["UNKNOWN", "LINE_END"]:
            continue
        
        # 2. 核心：获取该路口所有边缘线的原始朝向
        edge_directions, center_co = get_junction_edge_directions(vert, obj)
        if not edge_directions:
            continue
        
        # 3. 实例化模板并匹配边缘线朝向
        instantiate_template(scene, junction_type, center_co, edge_directions)
        processed_verts.append(vert)

    bm.free()

def process_straight_edges(obj, scene):
    """处理直线段（直接提取直线边缘的原始朝向）"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()

    # 筛选纯直线段（两个端点都是边数=1）
    straight_edges = []
    for edge in bm.edges:
        v1 = edge.verts[0]
        v2 = edge.verts[1]
        if len(v1.link_edges) == 1 and len(v2.link_edges) == 1:
            straight_edges.append(edge)

    # 处理每条直线段
    for edge in straight_edges:
        # 获取直线段的原始朝向
        edge_dir = get_edge_raw_direction(edge, obj)
        # 计算线段中点
        v1_co = obj.matrix_world @ edge.verts[0].co
        v2_co = obj.matrix_world @ edge.verts[1].co
        mid_co = (v1_co + v2_co) / 2
        # 实例化直路模板（传入直线朝向）
        instantiate_template(scene, "LINE", mid_co, [edge_dir])

    bm.free()

# ==================== 3. 核心算子 =====================
class MESH_OT_generate_road_grid(bpy.types.Operator):
    bl_idname = "mesh.generate_road"
    bl_label = "快速生成道路"
    bl_description = "精准匹配边缘线原始朝向生成道路"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        
        # 检查选中对象
        selected_objs = context.selected_objects
        if not selected_objs or selected_objs[0].type != 'MESH':
            self.report({'ERROR'}, "请选中道路边缘网格（MESH类型）！")
            return {'CANCELLED'}
        
        mesh_obj = selected_objs[0]
        self.report({'INFO'}, f"开始分析边缘线朝向：{mesh_obj.name}")

        # 1. 处理路口顶点（T/L/十字）
        process_junction_verts(mesh_obj, scene)
        
        # 2. 处理直线段
        process_straight_edges(mesh_obj, scene)

        self.report({'INFO'}, "道路生成完成！所有模板已匹配边缘线原始朝向")
        return {'FINISHED'}

# ==================== 4. 注册面板 =====================
class VIEW3D_PT_road_generator(bpy.types.Panel):
    bl_label = "道路生成器（精准朝向）"
    bl_idname = "VIEW3D_PT_road_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '道路工具'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        box.label(text="模板名称配置")
        box.prop(scene, "i_road_object_name")
        box.prop(scene, "l_road_object_name")
        box.prop(scene, "x_road_object_name")
        box.prop(scene, "t_road_object_name")

        layout.operator("mesh.generate_road", icon='ROAD', text="生成道路（精准匹配朝向）")

# ==================== 5. 注册/注销 =====================
classes = [
    MESH_OT_generate_road_grid,
    VIEW3D_PT_road_generator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.i_road_object_name
    del bpy.types.Scene.l_road_object_name
    del bpy.types.Scene.x_road_object_name
    del bpy.types.Scene.t_road_object_name

if __name__ == "__main__":
    register()