import bpy
import bmesh
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

# ==================== 2. 通用工具函数（仅保留边数判断，移除所有角度计算）====================
def collect_vertex_info(context):
    """收集顶点信息（仅根据边数判断路口类型）"""
    object_arrays = []
    
    # 获取选中的网格对象
    selected_objs = context.selected_objects
    if not selected_objs or selected_objs[0].type != 'MESH':
        return None, "请选中网格对象！"
    mesh_obj = selected_objs[0]
    
    # 转换为bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    
    # 边数→路口类型映射（核心简化逻辑）
    edge_count_to_junction = {
        1: "LINE",    # 1条边 → 直路
        2: "L",       # 2条边 → L型
        3: "T",       # 3条边 → T型
        4: "CROSS"    # 4条边 → 十字型
    }
    
    # 遍历所有顶点
    for vert in bm.verts:
        # 获取中心点世界坐标
        center_co = mesh_obj.matrix_world @ vert.co
        # 获取关联的边数（核心判断依据）
        edge_count = len(vert.link_edges)
        
        # 仅根据边数确定路口类型
        junction_type = edge_count_to_junction.get(edge_count, "UNKNOWN")
        
        # 存储顶点信息（仅保留必要字段）
        object_arrays.append({
            "center_co": (round(center_co.x, 2), round(center_co.y, 2), round(center_co.z, 2)),
            "vertex_index": f"V{vert.index}",
            "edge_count": edge_count,
            "junction_type": junction_type
        })
    
    bm.free()
    return object_arrays, None

# ==================== 3. 核心算子1：实例关联生成道路 =====================
class MESH_OT_generate_road_linked(bpy.types.Operator):
    bl_idname = "mesh.generate_road_linked"
    bl_label = "关联复制生成"
    bl_description = "基于选中的边缘网格，生成关联道路对象（共享数据块）"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 1. 收集顶点信息
        object_arrays, error = collect_vertex_info(context)
        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        if not object_arrays:
            self.report({'WARNING'}, "未收集到有效顶点信息！")
            return {'CANCELLED'}
        
        # 2. 模板名称映射（从场景属性读取）
        template_map = {
            "LINE": context.scene.i_road_object_name,
            "L": context.scene.l_road_object_name,
            "T": context.scene.t_road_object_name,
            "CROSS": context.scene.x_road_object_name
        }
        
        # 3. 创建关联实例（不拷贝数据块）
        created_count = 0
        for vertex_info in object_arrays:
            if vertex_info["junction_type"] == "UNKNOWN":
                continue
            
            template_name = template_map.get(vertex_info["junction_type"])
            if not template_name or template_name not in bpy.data.objects:
                self.report({'WARNING'}, f"模板对象「{template_name}」不存在！")
                continue
            
            template_obj = bpy.data.objects[template_name]
            
            # 关联复制：仅复制对象，共享Mesh数据
            new_instance = template_obj.copy()
            new_instance.name = f"{template_name}_linked_{vertex_info['vertex_index']}"
            
            # 设置位置（无旋转）
            new_instance.location = vertex_info["center_co"]
            
            # 链接到场景
            context.collection.objects.link(new_instance)
            created_count += 1
        
        # 4. 反馈结果
        if created_count > 0:
            self.report({'INFO'}, f"成功创建 {created_count} 个关联道路实例！")
        else:
            self.report({'WARNING'}, "未创建任何道路实例！")
        
        return {'FINISHED'}

# ==================== 4. 核心算子2：独立复制生成道路 =====================
class MESH_OT_generate_road_independent(bpy.types.Operator):
    bl_idname = "mesh.generate_road_independent"
    bl_label = "独立复制生成"
    bl_description = "基于选中的边缘网格，生成独立道路对象（非关联复制）"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 1. 收集顶点信息
        object_arrays, error = collect_vertex_info(context)
        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        if not object_arrays:
            self.report({'WARNING'}, "未收集到有效顶点信息！")
            return {'CANCELLED'}
        
        # 2. 模板名称映射（从场景属性读取）
        template_map = {
            "LINE": context.scene.i_road_object_name,
            "L": context.scene.l_road_object_name,
            "T": context.scene.t_road_object_name,
            "CROSS": context.scene.x_road_object_name
        }
        
        # 3. 创建独立实例（拷贝数据块）
        created_count = 0
        for vertex_info in object_arrays:
            if vertex_info["junction_type"] == "UNKNOWN":
                continue
            
            template_name = template_map.get(vertex_info["junction_type"])
            if not template_name or template_name not in bpy.data.objects:
                self.report({'WARNING'}, f"模板对象「{template_name}」不存在！")
                continue
            
            template_obj = bpy.data.objects[template_name]
            
            # 独立复制：复制对象+拷贝Mesh数据
            new_instance = template_obj.copy()
            new_instance.data = template_obj.data.copy()
            new_instance.name = f"{template_name}_independent_{vertex_info['vertex_index']}"
            
            # 设置位置（无旋转）
            new_instance.location = vertex_info["center_co"]
            
            # 链接到场景
            context.collection.objects.link(new_instance)
            created_count += 1
        
        # 4. 反馈结果
        if created_count > 0:
            self.report({'INFO'}, f"成功创建 {created_count} 个独立道路实例！")
        else:
            self.report({'WARNING'}, "未创建任何道路实例！")
        
        return {'FINISHED'}
