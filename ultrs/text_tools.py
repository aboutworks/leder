import bpy


# 定义属性（供输入文本使用）

bpy.types.Scene.rename_text = bpy.props.StringProperty(
    name="名称",
    description="对象主体名称",
    default="MyObject"
)

bpy.types.Scene.rename_pos = bpy.props.EnumProperty(
    name="位置",
    description="编号放在前缀还是后缀",
    items=[('PREFIX', "前缀", ""), ('SUFFIX', "后缀", "")],
    default='SUFFIX'
)

bpy.types.Scene.rename_start = bpy.props.IntProperty(
    name="起始编号",
    description="编号起始值",
    default=1,
    min=0
)

bpy.types.Scene.rename_order = bpy.props.EnumProperty(
    name="顺序",
    description="升序或降序",
    items=[('ASC', "升序", ""), ('DESC', "降序", "")],
    default='ASC'
)

# 操作类：执行重命名

class OBJECT_OT_rename_batch(bpy.types.Operator):
    bl_idname = "object.rename_selected"
    bl_label = "重命名选中对象"
    bl_description = "将当前选中的对象重命名为输入框内容，可选择前缀/后缀和升序/降序批量编号"

    def execute(self, context):
        scene = context.scene
        base_name = scene.rename_text.strip()
        position = getattr(scene, "rename_pos", "SUFFIX")      # 前缀/后缀
        start = getattr(scene, "rename_start", 1)             # 起始编号
        ascending = getattr(scene, "rename_order", "ASC") == "ASC"  # 升序/降序
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "没有选中任何对象")
            return {'CANCELLED'}

        objs = list(selected_objects)
        if not ascending:
            objs.reverse()

        # 如果只选中一个对象，直接重命名为 rename_text
        if len(objs) == 1:
            objs[0].name = base_name
        else:
            # 多选则按编号批量重命名
            for i, obj in enumerate(objs):
                number = start + i
                if position == "PREFIX":
                    obj.name = f"{number:03d}{base_name}"
                else:  # SUFFIX
                    obj.name = f"{base_name}{number:03d}"

        self.report({'INFO'}, f"已重命名 {len(objs)} 个对象")
        return {'FINISHED'}