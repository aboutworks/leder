import bpy
from bpy.app.translations import pgettext_iface as _  # 翻译函数（核心：找不到翻译就显示原英文）

# ===================== 面板类（全部默认写英文） =====================
class MaterialPanel(bpy.types.Panel):
    bl_label = _("Material")  # 默认英文，翻译函数自动匹配语言
    bl_idname = "VIEW3D_PT_material_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 10

    def draw(self, context):
        layout = self.layout
        layout.operator("material.clear_all", text=_("Remove All Materials"))

class OriginPanel(bpy.types.Panel):
    bl_label = _("Origin")
    bl_idname = "VIEW3D_PT_origin_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 11

    def draw(self, context):
        layout = self.layout
        layout.operator("origin.to_geometry", text=_("Geometry Center"))
        layout.operator("origin.to_mass", text=_("Center of Mass"))
        layout.operator("origin.to_cursor", text=_("Origin (3D Cursor)"))
        layout.operator("origin.to_volume", text=_("Volume Center"))

class FixModelPanel(bpy.types.Panel):
    bl_label = _("Fix")
    bl_idname = "VIEW3D_PT_fix_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 12

    def draw(self, context):
        layout = self.layout
        layout.operator("object.fix_model", text=_("Fix Model"))

class CreatePolygonPanel(bpy.types.Panel):
    bl_label = _("Create-Polygon")
    bl_idname = "Create_Polygon_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 20

    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_polygon", text=_("Create Equilateral Tetrahedron"))

class TextPanel(bpy.types.Panel):
    bl_label = _("Text - Batch Rename")
    bl_idname = "VIEW3D_PT_text_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 31

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text=_("Batch Number Rename"))
        layout.prop(scene, "rename_text", text=_("Name Body"))
        layout.prop(scene, "rename_pos", text=_("Number Position"))
        layout.prop(scene, "rename_start", text=_("Start Number"))
        layout.prop(scene, "rename_order", text=_("Order"))
        layout.operator("object.rename_selected", text=_("Execute Batch Rename"))
        layout.separator()

class ProceduralGeneratePanel(bpy.types.Panel):
    bl_label = _("Procedural Generation")
    bl_idname = "VIEW3D_PT_procedural_generate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_order = 50

    def draw(self, context):
        layout = self.layout

class GenerateStonePanel(bpy.types.Panel):
    bl_label = _("Stone Generator")
    bl_idname = "VIEW3D_PT_stone_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 操作提示
        box_tip = layout.box()
        box_tip.label(text=_("Operation Tips"), icon='INFO')
        if scene.stone_dist_mode == "1":
            box_tip.label(text=_("Mode 1: Auto create plane → Generate stones on plane faces"))
        else:
            box_tip.label(text=_("Mode 2: Select any mesh object → Generate stones on object faces"))
        
        # 核心设置
        layout.prop(scene, "stone_count", text=_("Stone Count"))
        layout.prop(scene, "stone_dist_mode", text=_("Distribution Mode"))
        layout.prop(scene, "stone_copy_mode", text=_("Copy Mode"))
        
        # 石块形状设置
        box_shape = layout.box()
        box_shape.label(text=_("Stone Shape"), icon='MESH_ICOSPHERE')
        box_shape.prop(scene, "stone_base_size", text=_("Base Size"))
        box_shape.prop(scene, "stone_irregularity", text=_("Irregularity"))
        
        # 分布设置
        box_dist = layout.box()
        box_dist.label(text=_("Distribution Settings"), icon='CONSTRAINT')
        box_dist.prop(scene, "stone_height_offset", text=_("Height Offset"))
        box_dist.prop(scene, "stone_scale_min", text=_("Minimum Scale"))
        box_dist.prop(scene, "stone_scale_max", text=_("Maximum Scale"))
        
        # 颜色设置
        box_color = layout.box()
        box_color.label(text=_("Color Settings"), icon='COLOR')
        box_color.prop(scene, "stone_color_min", text=_("Minimum Color (Grayscale)"))
        box_color.prop(scene, "stone_color_max", text=_("Maximum Color (Grayscale)"))
        
        # 生成按钮
        layout.separator()
        layout.operator("mesh.generate_stone", text=_("Generate Stones on Faces"), icon='MOD_INSTANCE')




class GenerateMazePanel(bpy.types.Panel):
    bl_label = _("Maze")
    bl_idname = "MESH_PT_generate_maze_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text=_("Polygon Maze Parameters (Walls Only)"))
        layout.prop(scene, "edge_count", text=_("Cell Edge Count"))
        layout.prop(scene, "cell_length", text=_("Cell Length (m)"))
        layout.prop(scene, "wall_thickness", text=_("Wall Thickness (m)"))
        layout.prop(scene, "wall_height", text=_("Wall Height (m)"))
        layout.prop(scene, "row_count", text=_("Row Count"))
        layout.prop(scene, "col_count", text=_("Column Count"))
        layout.operator("mesh.generate_maze_grid", text=_("Generate Maze"))

class GenerateRoadPanel(bpy.types.Panel):
    bl_label = _("Road")
    bl_idname = "MESH_PT_generate_road_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Legma'
    bl_parent_id = "VIEW3D_PT_procedural_generate"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text=_("Road Parameters"))
        layout.prop(scene, "i_road_object_name", text=_("Straight Road Name"))
        layout.prop(scene, "l_road_object_name", text=_("Curve Road Name"))
        layout.prop(scene, "x_road_object_name", text=_("Cross Road Name"))
        layout.prop(scene, "t_road_object_name", text=_("T-Junction Name"))
        layout.label(text=_("Generate Mode:"))
        layout.operator("mesh.generate_road_linked", icon='LINKED', text=_("Linked Instance (Shared Data)"))
        layout.operator("mesh.generate_road_independent", icon='UNLINKED', text=_("Independent Copy (Unlinked)"))

# class GenerateStairsPanel(bpy.types.Panel):
#     bl_label = _("Stairs")
#     bl_idname = "GenerateStairsPanel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Legma'
#     bl_parent_id = "VIEW3D_PT_procedural_generate"
#     bl_order = 4

#     def draw(self, context):
#         layout = self.layout
#         layout.label(text=_("Generate a staircase"))
#         layout.operator("object.ULTRS_GENERATE_stairs")
#         layout.label(text=_("Generate a staircase by Panel"))
#         layout.operator("object.generate_stair_plane")

# class DXFGeneratorPanel(bpy.types.Panel):
#     bl_label = _("DXF Generate 3D")
#     bl_idname = "VIEW3D_PT_ULTRS_GENERATE_from_dxf"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Legma'
#     bl_order = 60

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene

#         layout.label(text=_("Upload DXF and Generate 3D"))
#         layout.prop(scene, "dxf_filepath", text=_("Select File"))
#         layout.prop(scene, "level_height", text=_("Floor Height (m)"))
#         layout.prop(scene, "wall_thickness", text=_("Wall Thickness (m)"))
#         layout.operator("object.ULTRS_GENERATE_from_dxf", text=_("Generate 3D Walls"))

def unregister_panel_props():
    if hasattr(bpy.types.Scene, "lehuye_tab"):
        del bpy.types.Scene.lehuye_tab