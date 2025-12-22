import bpy
import bmesh

class OBJECT_OT_fix_model(bpy.types.Operator):
    """清理模型并修复权重绑定问题"""
    bl_idname = "object.fix_model"
    bl_label = "修复模型（清理+重置权重）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取选中对象
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "请先选中一个 Mesh 对象！")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"正在整理模型: {obj.name}")

        # 进入编辑模式
        bpy.ops.object.mode_set(mode='EDIT')

        # 获取BMesh
        mesh = bmesh.from_edit_mesh(obj.data)
        mesh.select_mode = {'VERT'}

        # 全选顶点
        bpy.ops.mesh.select_all(action='SELECT')

        # 合并重复顶点
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        self.report({'INFO'}, "✔ 已清理重复点")

        # 修复法线方向
        bpy.ops.mesh.normals_make_consistent(inside=False)
        self.report({'INFO'}, "✔ 已修复法线方向")

        # 删除松散几何
        bpy.ops.mesh.delete_loose()
        self.report({'INFO'}, "✔ 已删除松散几何")

        # 删除非流形几何
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.delete(type='VERT')
        self.report({'INFO'}, "✔ 已删除非流形几何")

        # 更新网格
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply 变换（旋转+缩放）
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        self.report({'INFO'}, "✔ 已 Apply Rotation & Scale")

        # 清空 Vertex Groups（权重组）
        obj.vertex_groups.clear()
        self.report({'INFO'}, "✔ 已清空所有 Vertex Groups（可重新绑定自动权重）")

        self.report({'INFO'}, "🎉 模型整理完成！可以重新尝试 Ctrl+P → Automatic Weights 了！")
        return {'FINISHED'}