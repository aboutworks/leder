import bpy
import bmesh
import mathutils
import random
import math
from bpy.app.translations import pgettext_iface as _

# ==================== 1. 注册场景属性 =====================
bpy.types.Scene.stone_count = bpy.props.IntProperty(
    name=_("Stone Count"),
    description=_("Number of stone instances to generate"),
    default=100,
    min=1,
    max=5000
)

# 分布模式：1-自动创建平面 2-选中对象（基于面散布）
bpy.types.Scene.stone_dist_mode = bpy.props.EnumProperty(
    name=_("Distribution Mode"),
    description=_("Where to distribute stones"),
    items=[
        ("1", _("Auto Create Plane"), _("Create a new plane for stone distribution")),
        ("2", _("Selected Object"), _("Distribute stones on selected object (based on faces)"))
    ],
    default="1"
)

# 复制模式（关联/独立）
bpy.types.Scene.stone_copy_mode = bpy.props.EnumProperty(
    name=_("Copy Mode"),
    description=_("How to copy stone mesh data"),
    items=[
        ("LINKED", _("Linked Copy (Shared Mesh)"), _("Shared mesh data, low performance cost")),
        ("INDEPENDENT", _("Independent Copy (Unique Mesh)"), _("Independent mesh data, high performance cost"))
    ],
    default="LINKED"
)

# 石块形状参数
bpy.types.Scene.stone_base_size = bpy.props.FloatProperty(
    name=_("Base Size"),
    description=_("Initial size of auto-created stone"),
    default=1.0,
    min=0.1,
    max=10.0
)
bpy.types.Scene.stone_irregularity = bpy.props.FloatProperty(
    name=_("Irregularity"),
    description=_("Vertex perturbation degree (0=regular, 1=extremely irregular)"),
    default=0.3,
    min=0.0,
    max=1.0
)

# 分布参数（基于面）
bpy.types.Scene.stone_scale_min = bpy.props.FloatProperty(
    name=_("Minimum Scale"),
    default=0.2,
    min=0.01,
    max=5.0
)
bpy.types.Scene.stone_scale_max = bpy.props.FloatProperty(
    name=_("Maximum Scale"),
    default=0.8,
    min=0.01,
    max=5.0
)
bpy.types.Scene.stone_height_offset = bpy.props.FloatProperty(
    name=_("Height Offset"),
    description=_("Stone height offset from face (avoid penetration)"),
    default=0.05,
    min=0.0,
    max=10.0
)

# 颜色参数
bpy.types.Scene.stone_color_min = bpy.props.FloatProperty(
    name=_("Minimum Color (Grayscale)"),
    default=0.6,
    min=0.0,
    max=1.0
)
bpy.types.Scene.stone_color_max = bpy.props.FloatProperty(
    name=_("Maximum Color (Grayscale)"),
    default=0.9,
    min=0.0,
    max=1.0
)

# ==================== 2. 核心工具函数（基于面的随机点）====================
def create_auto_stone(scene):
    """完全自动创建石块"""
    if "Auto_Generated_Stone" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Auto_Generated_Stone"])
    
    # 创建二十面体作为基础石块
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=scene.stone_base_size,
        location=(0, 0, 0)
    )
    auto_stone = bpy.context.active_object
    auto_stone.name = "Auto_Generated_Stone"
    
    # 应用变换
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 顶点扰动创建不规则形状
    mesh = auto_stone.data
    for v in mesh.vertices:
        perturb = random.uniform(1-scene.stone_irregularity, 1+scene.stone_irregularity)
        v.co.x *= perturb
        v.co.y *= perturb
        v.co.z *= perturb
    mesh.update()
    
    # 创建基础材质
    mat = bpy.data.materials.new(name="Auto_Stone_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.7, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    if auto_stone.data.materials:
        auto_stone.data.materials[0] = mat
    else:
        auto_stone.data.materials.append(mat)
    
    return auto_stone

def create_distribution_plane(scene):
    """创建分布平面（细分增加面数，让分布更均匀）"""
    if "Distribution_Plane" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Distribution_Plane"])
    
    # 创建平面并细分（增加面数）
    bpy.ops.mesh.primitive_plane_add(
        size=20,
        location=(0, 0, 0)
    )
    plane = bpy.context.active_object
    plane.name = "Distribution_Plane"
    
    # 细分平面（增加面数）
    bpy.context.view_layer.objects.active = plane
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=10)  # 细分10次，生成更多面
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 平面材质
    mat = bpy.data.materials.new(name="Distribution_Plane_Mat")
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.2, 0.3, 0.2, 1.0)
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)
    
    return plane

def get_object_faces_data(obj):
    """获取对象所有面的详细数据（世界坐标）"""
    if not obj or obj.type != 'MESH':
        return []
    
    face_data_list = []
    # 使用bmesh获取面数据
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)  # 转换到世界坐标
    
    for face in bm.faces:
        # 面中心点
        face_center = face.calc_center_median()
        # 面法向量
        face_normal = face.normal.normalized()
        # 面的边界范围
        verts = [v.co for v in face.verts]
        min_x = min(v.x for v in verts)
        max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts)
        max_y = max(v.y for v in verts)
        min_z = min(v.z for v in verts)
        max_z = max(v.z for v in verts)
        
        face_data_list.append({
            "center": face_center,
            "normal": face_normal,
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
            "verts": verts
        })
    
    bm.free()
    return face_data_list

def get_random_point_on_face(face_data, scene):
    """在单个面内生成随机点"""
    # 方法1：三角形面（三点插值）
    if len(face_data["verts"]) == 3:
        v1, v2, v3 = face_data["verts"]
        # 生成两个随机权重（0-1）
        u = random.uniform(0, 1)
        v = random.uniform(0, 1 - u)
        w = 1 - u - v
        # 插值计算随机点
        rand_point = (u * v1) + (v * v2) + (w * v3)
    
    # 方法2：四边形/更多边面（边界内随机）
    else:
        rand_x = random.uniform(face_data["min_x"], face_data["max_x"])
        rand_y = random.uniform(face_data["min_y"], face_data["max_y"])
        # 计算Z值（基于面的平面方程）
        a, b, c = face_data["normal"]
        d = a * face_data["center"].x + b * face_data["center"].y + c * face_data["center"].z
        rand_z = (d - a * rand_x - b * rand_y) / c if c != 0 else random.uniform(face_data["min_z"], face_data["max_z"])
        rand_point = mathutils.Vector((rand_x, rand_y, rand_z))
    
    # 添加高度偏移（沿法向量方向）
    final_point = rand_point + (face_data["normal"] * scene.stone_height_offset)
    
    return final_point

def copy_stone(auto_stone, copy_mode):
    """复制石块（关联/独立）"""
    new_stone = auto_stone.copy()
    new_stone.animation_data_clear()
    
    if copy_mode == "LINKED":
        new_stone.data = auto_stone.data
    elif copy_mode == "INDEPENDENT":
        new_stone.data = auto_stone.data.copy()
    
    return new_stone

def transform_stone(obj, scene, face_data_list):
    """变换石块到随机面的随机点"""
    if not face_data_list:
        return
    
    # 1. 随机选一个面
    random_face = random.choice(face_data_list)
    # 2. 在选中面内生成随机点
    obj.location = get_random_point_on_face(random_face, scene)
    
    # 3. 旋转：对齐面法线 + 随机旋转
    # 基础旋转（对齐法向量）
    default_z = mathutils.Vector((0, 0, 1))
    base_rotation = default_z.rotation_difference(random_face["normal"])
    obj.rotation_euler = base_rotation.to_euler()
    # 随机旋转
    obj.rotation_euler.rotate_axis("Z", random.uniform(0, math.pi * 2))
    
    # 4. 随机等比缩放
    scale = random.uniform(scene.stone_scale_min, scene.stone_scale_max)
    obj.scale = (scale, scale, scale)
    
    # 5. 随机颜色（仅独立复制时生效）
    if scene.stone_copy_mode == "INDEPENDENT" and obj.data.materials:
        mat_inst = obj.data.materials[0].copy()
        mat_inst.name = f"Stone_Mat_{obj.name}"
        gray = random.uniform(scene.stone_color_min, scene.stone_color_max)
        mat_inst.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (gray, gray, gray, 1.0)
        obj.data.materials[0] = mat_inst

# ==================== 3. 核心算子（基于面的随机点）====================
class MESH_OT_generate_stone(bpy.types.Operator):
    bl_idname = "mesh.generate_stone"
    bl_label = _("Generate Stones")
    bl_description = _("Generate stones on random points of object faces")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        dist_mode = scene.stone_dist_mode
        copy_mode = scene.stone_copy_mode
        stone_count = scene.stone_count
        
        # 初始化变量
        auto_stone = None
        face_data_list = []
        distribution_plane = None
        
        # -------------------------- 模式1：自动创建平面 --------------------------
        if dist_mode == "1":
            # 创建分布平面（细分增加面数）
            distribution_plane = create_distribution_plane(scene)
            # 获取平面的所有面数据
            face_data_list = get_object_faces_data(distribution_plane)
            if not face_data_list:
                self.report({'ERROR'}, _("Failed to get face data from auto-created plane!"))
                return {'CANCELLED'}
        
        # -------------------------- 模式2：选中对象 --------------------------
        elif dist_mode == "2":
            # 检查是否选中有效对象
            target_obj = bpy.context.active_object
            if not target_obj or target_obj.type != 'MESH':
                self.report({'ERROR'}, _("Please select a mesh object first!"))
                return {'CANCELLED'}
            
            # 获取选中对象的所有面数据
            face_data_list = get_object_faces_data(target_obj)
            if not face_data_list:
                self.report({'ERROR'}, _("Selected object has no faces!"))
                return {'CANCELLED'}
        
        # -------------------------- 自动创建石块 --------------------------
        auto_stone = create_auto_stone(scene)
        
        # -------------------------- 批量生成石块 --------------------------
        for i in range(stone_count):
            # 复制石块（关联/独立）
            new_stone = copy_stone(auto_stone, copy_mode)
            scene.collection.objects.link(new_stone)
            
            # 变换到随机面的随机点
            transform_stone(new_stone, scene, face_data_list)
            new_stone.name = f"Face_Stone_{i}"
            
            # 进度提示
            if i % 50 == 0:
                self.report({'INFO'}, _("Generated {i}/{total} stones").format(i=i, total=stone_count))
        
        # 隐藏自动创建的石块
        auto_stone.hide_viewport = True
        auto_stone.hide_render = True
        # 保留分布平面可见（模式1）
        if distribution_plane:
            distribution_plane.hide_viewport = False
            distribution_plane.hide_render = False
        
        # 视图聚焦到石块
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.name.startswith("Face_Stone_"):
                obj.select_set(True)
        bpy.ops.view3d.view_selected(use_all_regions=True)
        
        self.report({'INFO'}, _("✅ Successfully generated {count} stones on object faces!").format(count=stone_count))
        return {'FINISHED'}

# ==================== 中日翻译字典（完整覆盖）====================
# translations = {
#     "zh_CN": {
#         # 核心面板
#         "Stone Generator": "石块生成器",
#         "Operation Tips": "操作提示",
#         "Mode 1: Auto create XY plane → Generate stones": "模式1：自动创建XY平面 → 生成石块",
#         "Mode 2: Select mesh object → Generate stones on its XY top face": "模式2：选择网格对象 → 在其XY顶面生成石块",
        
#         # 分布模式
#         "Distribution Mode": "分布模式",
#         "Auto Create Distribution Plane": "自动创建分布平面",
#         "Create a new plane (XY face, Z normal up)": "创建新平面（XY面，Z法线向上）",
#         "Selected Object Top Face": "选中对象的顶面",
#         "Use top face of selected object (XY face, Z normal up)": "使用选中对象的顶面（XY面，Z法线向上）",
        
#         # 基础设置
#         "Stone Count": "石块数量",
#         "Number of stone instances to generate": "需要生成的石块实例数量",
#         "Copy Mode": "复制模式",
#         "Linked Copy (Shared Mesh)": "关联复制（共享网格）",
#         "Independent Copy (Unique Mesh)": "独立复制（独立网格）",
#         "Shared mesh data, low performance cost": "共享网格数据，性能开销极低",
#         "Independent mesh data, high performance cost": "独立网格数据，性能开销较高",
        
#         # 石块形状
#         "Stone Shape": "石块形状",
#         "Base Size": "基础尺寸",
#         "Initial size of auto-created stone": "自动创建石块的初始尺寸",
#         "Irregularity": "不规则度",
#         "Vertex perturbation degree (0=regular, 1=extremely irregular)": "顶点扰动程度（0=规则，1=极度不规则）",
        
#         # 分布约束
#         "XY Face Distribution": "XY面分布",
#         "X Distribution Range": "X轴分布范围",
#         "X-axis range on XY face (± value)": "XY面X轴分布范围（±数值）",
#         "Y Distribution Range": "Y轴分布范围",
#         "Y-axis range on XY face (± value)": "XY面Y轴分布范围（±数值）",
#         "Z Offset": "Z轴偏移",
#         "Stone height offset from face (avoid penetration)": "石块离面的高度偏移（避免穿模）",
        
#         # 视觉设置
#         "Visual Settings": "视觉设置",
#         "Minimum Scale": "最小缩放",
#         "Maximum Scale": "最大缩放",
#         "Minimum Color (Grayscale)": "最小颜色（灰度）",
#         "Maximum Color (Grayscale)": "最大颜色（灰度）",
        
#         # 生成按钮
#         "Generate Stones": "生成石块",
#         "Generate Stones on XY Face": "在XY面生成石块",
#         "Generate stones on XY face (Z normal up) with auto-created stone shape": "在XY面（Z法线向上）生成自动创建形状的石块",
        
#         # 错误提示（核心修复）
#         "Please select a mesh object first (cube/plane with XY top face)!": "请先选择一个网格对象（带XY顶面的立方体/平面）！",
#         "No top face found (require XY face with Z normal up) on selected object!": "选中对象上未找到符合要求的顶面（需要XY面+Z法线向上）！",
#         "Failed to create distribution plane (XY face, Z normal up)!": "无法创建分布平面（XY面，Z法线向上）！",
        
#         # 成功提示
#         "Generated {i}/{total} stones": "已生成 {i}/{total} 个石块",
#         "✅ Successfully generated {count} stones on XY face (Z normal up)!": "✅ 成功在XY面（Z法线向上）生成 {count} 个石块！"
#     },
#     "ja_JP": {
#         # 核心面板
#         "Stone Generator": "石の生成器",
#         "Operation Tips": "操作ヒント",
#         "Mode 1: Auto create XY plane → Generate stones": "モード1：XY平面を自動作成 → 石を生成",
#         "Mode 2: Select mesh object → Generate stones on its XY top face": "モード2：メッシュオブジェクトを選択 → XY上面に石を生成",
        
#         # 分布模式
#         "Distribution Mode": "分布モード",
#         "Auto Create Distribution Plane": "分布平面を自動作成",
#         "Create a new plane (XY face, Z normal up)": "新しい平面を作成（XY面、Z法線が上向き）",
#         "Selected Object Top Face": "選択オブジェクトの上面",
#         "Use top face of selected object (XY face, Z normal up)": "選択したオブジェクトの上面を使用（XY面、Z法線が上向き）",
        
#         # 基础设置
#         "Stone Count": "石の数",
#         "Number of stone instances to generate": "生成する石のインスタンス数",
#         "Copy Mode": "コピーモード",
#         "Linked Copy (Shared Mesh)": "リンクコピー（メッシュ共有）",
#         "Independent Copy (Unique Mesh)": "独立コピー（メッシュ独立）",
#         "Shared mesh data, low performance cost": "メッシュデータを共有、パフォーマンス負荷が極めて低い",
#         "Independent mesh data, high performance cost": "メッシュデータを独立、パフォーマンス負荷が高い",
        
#         # 石块形状
#         "Stone Shape": "石の形状",
#         "Base Size": "ベースサイズ",
#         "Initial size of auto-created stone": "自動作成した石の初期サイズ",
#         "Irregularity": "不規則度",
#         "Vertex perturbation degree (0=regular, 1=extremely irregular)": "頂点の摂動度（0=規則的、1=極めて不規則）",
        
#         # 分布约束
#         "XY Face Distribution": "XY面分布",
#         "X Distribution Range": "X軸分布範囲",
#         "X-axis range on XY face (± value)": "XY面のX軸分布範囲（±値）",
#         "Y Distribution Range": "Y軸分布範囲",
#         "Y-axis range on XY face (± value)": "XY面のY軸分布範囲（±値）",
#         "Z Offset": "Z軸オフセット",
#         "Stone height offset from face (avoid penetration)": "石の面からの高さオフセット（貫通回避）",
        
#         # 视觉设置
#         "Visual Settings": "ビジュアル設定",
#         "Minimum Scale": "最小スケール",
#         "Maximum Scale": "最大スケール",
#         "Minimum Color (Grayscale)": "最小カラー（グレースケール）",
#         "Maximum Color (Grayscale)": "最大カラー（グレースケール）",
        
#         # 生成按钮
#         "Generate Stones": "石を生成",
#         "Generate Stones on XY Face": "XY面に石を生成",
#         "Generate stones on XY face (Z normal up) with auto-created stone shape": "XY面（Z法線が上向き）に自動作成した形状の石を生成",
        
#         # 错误提示（核心修复）
#         "Please select a mesh object first (cube/plane with XY top face)!": "メッシュオブジェクトを選択してください（XY上面のあるキューブ/平面）！",
#         "No top face found (require XY face with Z normal up) on selected object!": "選択したオブジェクトに符合する上面が見つかりません（XY面+Z法線が上向きが必要）！",
#         "Failed to create distribution plane (XY face, Z normal up)!": "分布平面を作成できません（XY面、Z法線が上向き）！",
        
#         # 成功提示
#         "Generated {i}/{total} stones": "{i}/{total} 個の石を生成しました",
#         "✅ Successfully generated {count} stones on XY face (Z normal up)!": "✅ XY面（Z法線が上向き）に {count} 個の石を生成しました！"
#     }
# }




# 遍历所有选中对象批量添加刚体（Blender 4.4.3专用）
# import bpy

# def batch_set_rigid_body_for_selected(
#     rigid_type="ACTIVE",  # ACTIVE(动态)/PASSIVE(静态)
#     mass=1.0,             # 质量（仅动态刚体生效）
#     friction=0.6,         # 摩擦系数（越大滑动越慢）
#     restitution=0.1,      # 弹性系数（越大反弹越明显）
#     collision_shape="CONVEX_HULL"  # 碰撞形状（性能优先）
# ):
#     """
#     Blender 4.4.3专用：遍历所有选中的网格对象，批量添加刚体属性
#     :param rigid_type: 刚体类型，ACTIVE=动态（受重力），PASSIVE=静态（碰撞体）
#     :param mass: 动态刚体质量，值越大惯性越大
#     :param friction: 摩擦系数，0-1，越大滑动越慢
#     :param restitution: 弹性系数，0-1，越大反弹越明显
#     :param collision_shape: 碰撞形状（CONVEX_HULL/MESH/SPHERE等）
#     """
#     # 1. 获取所有选中的网格对象（过滤非网格对象）
#     selected_meshes = []
#     for obj in bpy.context.selected_objects:
#         if obj.type == 'MESH':
#             selected_meshes.append(obj)
#         else:
#             print(f"⚠️ 跳过非网格对象：{obj.name}（仅网格可设置刚体）")
    
#     # 2. 校验：无有效网格对象时提示并退出
#     if not selected_meshes:
#         print("❌ 错误：未选中任何网格对象！")
#         return
    
#     # 3. 遍历每一个选中的网格对象，逐个添加刚体
#     success_count = 0
#     for idx, obj in enumerate(selected_meshes, 1):
#         try:
#             # 激活当前遍历的对象（4.4.3必须激活才能操作刚体）
#             bpy.context.view_layer.objects.active = obj
            
#             # 移除原有刚体属性（避免重复添加冲突）
#             if obj.rigid_body:
#                 bpy.ops.rigidbody.object_remove()
#                 print(f"📌 移除[{obj.name}]原有刚体属性，重新添加")
            
#             # 为当前对象添加刚体（核心：遍历逐个添加）
#             bpy.ops.rigidbody.object_add(type=rigid_type)
            
#             # 配置当前对象的刚体参数
#             rb = obj.rigid_body
#             rb.mass = mass                      # 质量
#             rb.friction = friction              # 摩擦系数
#             rb.restitution = restitution        # 弹性系数
#             rb.collision_shape = collision_shape # 碰撞形状
#             rb.collision_margin = 0.01          # 碰撞边距
            
#             # 动态刚体专属配置
#             if rigid_type == "ACTIVE":
#                 rb.body.use_gravity = True      # 启用重力
#                 rb.body.linear_damping = 0.05   # 线性阻尼
#                 rb.body.angular_damping = 0.1    # 角阻尼
            
#             success_count += 1
#             print(f"✅ [{idx}/{len(selected_meshes)}] 已为{obj.name}添加{rigid_type}刚体")
        
#         except Exception as e:
#             print(f"❌ [{idx}/{len(selected_meshes)}] {obj.name}添加刚体失败：{str(e)}")
    
#     # 4. 最终统计
#     print(f"\n🎉 批量添加完成！总计选中{len(selected_meshes)}个网格对象，成功设置{success_count}个刚体")

# # ==================== 执行批量添加（按需修改参数）====================
# if __name__ == "__main__":
#     # 自定义批量配置（所有选中对象共用此参数）
#     BATCH_SETTINGS = {
#         "rigid_type": "ACTIVE",    # 所有选中对象设为动态刚体（可改为PASSIVE）
#         "mass": 1.0,               # 统一质量（仅动态生效）
#         "friction": 0.6,           # 统一摩擦系数
#         "restitution": 0.1,        # 统一弹性系数
#         "collision_shape": "CONVEX_HULL"  # 统一碰撞形状
#     }
    
#     # 执行：遍历所有选中对象批量添加刚体
#     batch_set_rigid_body_for_selected(**BATCH_SETTINGS)