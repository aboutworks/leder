# 这是集中将所有 文件名称 导入类
from .material_tools import MATERIAL_OT_clear_all

from .material_uv_xy_tools import OBJECT_OT_assign_uv_by_xy_grid


from .origin_tools import (
    ORIGIN_OT_to_geometry,
    ORIGIN_OT_to_mass,
    ORIGIN_OT_to_cursor,
    ORIGIN_OT_to_volume,
)
from .text_tools import OBJECT_OT_rename_batch

from .generatefromdxf_tools import ULTRS_GENERATE_from_dxf

from .generate_maze_tools import MESH_OT_generate_maze_grid

from .create_polygon_tools import OBJECT_OT_create_polygon

from .generate_road_tools import MESH_OT_generate_road_independent, MESH_OT_generate_road_linked

from .generate_stone_tools import MESH_OT_generate_stone

from .densePointCloud_panel_tools import OBJECT_OT_create_grid_faces


# from .generate_stairs_tools import ULTRS_GENERATE_stairs,OBJECT_OT_generate_stair_plane
# from .fix_model_tools import OBJECT_OT_fix_model