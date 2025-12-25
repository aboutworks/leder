import bpy

#从ui_pennel引入面板类
from .ui_panel import MaterialPanel,TextPanel,OriginPanel, GenerateMazePanel,FixModelPanel,CreatePolygonPanel,GenerateRoadPanel, GenerateStonePanel,ProceduralGeneratePanel,DensePointCloudPanel, DensePointCloudPanel_PointHandler,MaterialPanel_uv
#,DXFGeneratorPanel,GenerateStairsPanel

# 引入的类名
from .ultrs import (
    MATERIAL_OT_clear_all,
    ORIGIN_OT_to_geometry,
    ORIGIN_OT_to_mass,
    ORIGIN_OT_to_cursor,
    ORIGIN_OT_to_volume,
    OBJECT_OT_rename_batch,
    MESH_OT_generate_maze_grid, #* 快速生成四壁 */
    OBJECT_OT_create_polygon,
    MESH_OT_generate_road_independent,
    MESH_OT_generate_road_linked,
    MESH_OT_generate_stone,
    #ULTRS_GENERATE_stairs,
    #ULTRS_GENERATE_from_dxf, # DXF 快速生成 3D
    OBJECT_OT_create_grid_faces,
    OBJECT_OT_assign_uv_by_xy_grid,

)

classes = [
    ProceduralGeneratePanel,


    # 材质工具
    MaterialPanel,
    MATERIAL_OT_clear_all,

    # 中心轴心工具
    OriginPanel,
    ORIGIN_OT_to_geometry,
    ORIGIN_OT_to_mass,
    ORIGIN_OT_to_cursor,
    ORIGIN_OT_to_volume,

    # Text 面板
    TextPanel,
    OBJECT_OT_rename_batch,

    # 快速生成四壁
    GenerateMazePanel,
    MESH_OT_generate_maze_grid,     # 快速生成四壁

    # DXF 生成面板和操作类

    # 修复模型
    FixModelPanel,

    # 创建多边形
    CreatePolygonPanel,
    OBJECT_OT_create_polygon,

    # 快速生成道路
    GenerateRoadPanel,
    MESH_OT_generate_road_independent,
    MESH_OT_generate_road_linked,

    # 快速生成石块
    GenerateStonePanel,
    MESH_OT_generate_stone,

    DensePointCloudPanel, 
    DensePointCloudPanel_PointHandler,
    OBJECT_OT_create_grid_faces,

    # 暂时不放
    # GenerateStairsPanel,
    # DXFGeneratorPanel,
    # ULTRS_GENERATE_stairs,
    # ULTRS_GENERATE_from_dxf,

    MaterialPanel_uv,
    OBJECT_OT_assign_uv_by_xy_grid

]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):  # 注销顺序反向
        bpy.utils.unregister_class(cls)

# 仅用于调试脚本时直接运行
if __name__ == "__main__":
    register()