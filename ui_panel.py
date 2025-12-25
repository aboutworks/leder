import bpy
from bpy.app.translations import pgettext_iface as _  # 翻译函数（核心：找不到翻译就显示原英文）

# ===================== 父面板：Material 主面板 =====================
class MaterialPanel(bpy.types.Panel):
    bl_label = _("Material & UV")  # 已适配翻译
    bl_idname = "VIEW3D_PT_material_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 10

    def draw(self, context):
        layout = self.layout
        layout.operator("material.clear_all", text=_("Remove All Materials"))  # 已适配翻译

# ===================== 子面板：Material UV 子面板 =====================
class MaterialPanel_uv(bpy.types.Panel):  # ✅ 修复拼写错误：Material → Material
    bl_label = _("UV Tools")  # 已适配翻译
    bl_idname = "VIEW3D_PT_material_uv_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_parent_id = "VIEW3D_PT_material_tools"  # 关联父面板的bl_idname
    bl_order = 1  # 子面板在父面板中的排序

    def draw(self, context):  # ✅ 修复方法名：draw_uv_grid_panel → draw
        layout = self.layout
        layout.separator()
        layout.label(text=_("XY Grid UV Assignment"), icon='UV')  # 已适配翻译
        
        # 添加UV分配运算符按钮
        layout.operator("object.assign_uv_by_xy_grid", text=_("Assign UV by XY Grid"))  # 已适配翻译
        
        # 可选：添加UV展开相关的快捷按钮（提升实用性）
        layout.separator()
        layout.label(text=_("Quick UV Tools"), icon='IMAGE')  # 已适配翻译
        layout.operator("uv.smart_project", text=_("Smart UV Project"))  # 已适配翻译
        layout.operator("uv.project_from_view", text=_("Project UV from View"))  # 已适配翻译


class OriginPanel(bpy.types.Panel):
    bl_label = _("Origin")  # 已适配翻译
    bl_idname = "VIEW3D_PT_origin_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 11

    def draw(self, context):
        layout = self.layout
        layout.operator("origin.to_geometry", text=_("Geometry Center"))  # 已适配翻译
        layout.operator("origin.to_mass", text=_("Center of Mass"))  # 已适配翻译
        layout.operator("origin.to_cursor", text=_("Origin (3D Cursor)"))  # 已适配翻译
        layout.operator("origin.to_volume", text=_("Volume Center"))  # 已适配翻译

class FixModelPanel(bpy.types.Panel):
    bl_label = _("Fix")  # 已适配翻译
    bl_idname = "VIEW3D_PT_fix_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 12

    def draw(self, context):
        layout = self.layout
        layout.operator("object.fix_model", text=_("Fix Model"))  # 已适配翻译

class CreatePolygonPanel(bpy.types.Panel):
    bl_label = _("Create-Polygon")  # 已适配翻译
    bl_idname = "VIEW3D_PT_create_polygon_tools"  # ✅ 规范bl_idname命名（原Create_Polygon_tools不符合规范）
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 20

    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_polygon", text=_("Create Equilateral Tetrahedron"))  # 已适配翻译

class TextPanel(bpy.types.Panel):
    bl_label = _("Text - Batch Rename")  # 已适配翻译
    bl_idname = "VIEW3D_PT_text_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 31

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text=_("Batch Number Rename"))  # 已适配翻译
        layout.prop(scene, "rename_text", text=_("Name Body"))  # 已适配翻译
        layout.prop(scene, "rename_pos", text=_("Number Position"))  # 已适配翻译
        layout.prop(scene, "rename_start", text=_("Start Number"))  # 已适配翻译
        layout.prop(scene, "rename_order", text=_("Order"))  # 已适配翻译
        layout.operator("object.rename_selected", text=_("Execute Batch Rename"))  # 已适配翻译
        layout.separator()

# -------------------- DensePointCloudPanel 父面板 --------------------
class DensePointCloudPanel(bpy.types.Panel):
    bl_label = _("Dense Point Cloud")  # 已适配翻译
    bl_idname = "VIEW3D_PT_dense_point_cloud"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 40
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=_("Point Cloud Processing Tools"), icon='OUTLINER_OB_POINTCLOUD')  # 已适配翻译

# -------------------- DensePointCloudPanel 子面板 --------------------
class DensePointCloudPanel_PointHandler(bpy.types.Panel):
    bl_label = _("Point Handler")  # 已适配翻译
    bl_idname = "VIEW3D_PT_dense_point_cloud_point_handler"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_parent_id = "VIEW3D_PT_dense_point_cloud"
    bl_order = 1
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_grid_faces", text=_("Create Grid Faces"), icon='MOD_INSTANCE')  # 已适配翻译

#   procedural generate
class ProceduralGeneratePanel(bpy.types.Panel):
    bl_label = _("Procedural Generation")  # 已适配翻译
    bl_idname = "VIEW3D_PT_procedural_generate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_order = 50

    def draw(self, context):
        layout = self.layout

class GenerateStonePanel(bpy.types.Panel):
    bl_label = _("Stone Generator")  # 已适配翻译
    bl_idname = "VIEW3D_PT_stone_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 操作提示
        box_tip = layout.box()
        box_tip.label(text=_("Operation Tips"), icon='INFO')  # 已适配翻译
        if scene.stone_dist_mode == "1":
            box_tip.label(text=_("Mode 1: Auto create plane → Generate stones on plane faces"))  # 已适配翻译
        else:
            box_tip.label(text=_("Mode 2: Select any mesh object → Generate stones on object faces"))  # 已适配翻译
        
        # 核心设置
        layout.prop(scene, "stone_count", text=_("Stone Count"))  # 已适配翻译
        layout.prop(scene, "stone_dist_mode", text=_("Distribution Mode"))  # 已适配翻译
        layout.prop(scene, "stone_copy_mode", text=_("Copy Mode"))  # 补充翻译key
        
        # 石块形状设置
        box_shape = layout.box()
        box_shape.label(text=_("Stone Shape"), icon='MESH_ICOSPHERE')  # 已适配翻译
        box_shape.prop(scene, "stone_base_size", text=_("Base Size"))  # 已适配翻译
        box_shape.prop(scene, "stone_irregularity", text=_("Irregularity"))  # 已适配翻译
        
        # 分布设置
        box_dist = layout.box()
        box_dist.label(text=_("Distribution Settings"), icon='CONSTRAINT')  # 已适配翻译
        box_dist.prop(scene, "stone_height_offset", text=_("Height Offset"))  # 补充翻译key
        box_dist.prop(scene, "stone_scale_min", text=_("Minimum Scale"))  # 已适配翻译
        box_dist.prop(scene, "stone_scale_max", text=_("Maximum Scale"))  # 已适配翻译
        
        # 颜色设置
        box_color = layout.box()
        box_color.label(text=_("Color Settings"), icon='COLOR')  # 已适配翻译
        box_color.prop(scene, "stone_color_min", text=_("Minimum Color (Grayscale)"))  # 已适配翻译
        box_color.prop(scene, "stone_color_max", text=_("Maximum Color (Grayscale)"))  # 已适配翻译
        
        # 生成按钮
        layout.separator()
        layout.operator("mesh.generate_stone", text=_("Generate Stones on Faces"), icon='MOD_INSTANCE')  # 补充翻译key

class GenerateMazePanel(bpy.types.Panel):
    bl_label = _("Maze")  # 已适配翻译
    bl_idname = "VIEW3D_PT_generate_maze_panel"  # ✅ 规范bl_idname命名（原MESH_PT不符合3D视图面板规范）
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text=_("Polygon Maze Parameters (Walls Only)"))  # 已适配翻译
        layout.prop(scene, "edge_count", text=_("Cell Edge Count"))  # 已适配翻译
        layout.prop(scene, "cell_length", text=_("Cell Length (m)"))  # 已适配翻译
        layout.prop(scene, "wall_thickness", text=_("Wall Thickness (m)"))  # 已适配翻译
        layout.prop(scene, "wall_height", text=_("Wall Height (m)"))  # 已适配翻译
        layout.prop(scene, "row_count", text=_("Row Count"))  # 已适配翻译
        layout.prop(scene, "col_count", text=_("Column Count"))  # 已适配翻译
        layout.operator("mesh.generate_maze_grid", text=_("Generate Maze"))  # 已适配翻译

class GenerateRoadPanel(bpy.types.Panel):
    bl_label = _("Road")  # 已适配翻译
    bl_idname = "VIEW3D_PT_generate_road_panel"  # ✅ 规范bl_idname命名（原MESH_PT不符合规范）
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lehuye-Leder'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text=_("Road Parameters"))  # 已适配翻译
        layout.prop(scene, "i_road_object_name", text=_("Straight Road Name"))  # 已适配翻译
        layout.prop(scene, "l_road_object_name", text=_("Curve Road Name"))  # 已适配翻译
        layout.prop(scene, "x_road_object_name", text=_("Cross Road Name"))  # 已适配翻译
        layout.prop(scene, "t_road_object_name", text=_("T-Junction Name"))  # 已适配翻译
        layout.label(text=_("Generate Mode:"))  # 已适配翻译
        layout.operator("mesh.generate_road_linked", icon='LINKED', text=_("Linked Instance (Shared Data)"))  # 已适配翻译
        layout.operator("mesh.generate_road_independent", icon='UNLINKED', text=_("Independent Copy (Unlinked)"))  # 已适配翻译

# 注释掉的面板也补全翻译调用（备用）
# class GenerateStairsPanel(bpy.types.Panel):
#     bl_label = _("Stairs")  # 已适配翻译
#     bl_idname = "VIEW3D_PT_generate_stairs_panel"  # ✅ 规范bl_idname命名
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Lehuye-Leder'
#     bl_parent_id = "VIEW3D_PT_procedural_generate"
#     bl_order = 4

#     def draw(self, context):
#         layout = self.layout
#         layout.label(text=_("Generate a staircase"))  # 已适配翻译
#         layout.operator("object.ULTRS_GENERATE_stairs", text=_("Generate a staircase"))  # 补充按钮文本翻译
#         layout.label(text=_("Generate a staircase by Panel"))  # 已适配翻译
#         layout.operator("object.generate_stair_plane", text=_("Generate Stair by Panel"))  # 补充按钮文本翻译

# class DXFGeneratorPanel(bpy.types.Panel):
#     bl_label = _("DXF Generate 3D")  # 已适配翻译
#     bl_idname = "VIEW3D_PT_dxf_generator_panel"  # ✅ 规范bl_idname命名
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Lehuye-Leder'
#     bl_order = 60

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene

#         layout.label(text=_("Upload DXF and Generate 3D"))  # 已适配翻译
#         layout.prop(scene, "dxf_filepath", text=_("Select File"))  # 已适配翻译
#         layout.prop(scene, "level_height", text=_("Floor Height (m)"))  # 已适配翻译
#         layout.prop(scene, "wall_thickness", text=_("Wall Thickness (m)"))  # 已适配翻译
#         layout.operator("object.ULTRS_GENERATE_from_dxf", text=_("Generate 3D Walls"))  # 已适配翻译

def unregister_panel_props():
    if hasattr(bpy.types.Scene, "lehuye_tab"):
        del bpy.types.Scene.lehuye_tab