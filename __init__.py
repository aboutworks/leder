bl_info = {
    "name": "Lehuye Plugin",
    "author": "Lehuye Inc.",
    "version": (1, 1, 0),
    "blender": (4, 5, 0),  # 明确适配4.5
    "location": "View3D > Sidebar > Lehuye",
    "description": "乐乎也多功能插件集",
    "category": "PluginTools"
}

import bpy
import bpy.app.translations
import os
import sys

# ===================== 4.5专属翻译注册 =====================
# 1. 添加i18n路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n"))

# 2. 导入合并后的翻译字典
try:
    from translations import translations as all_translations
except ImportError:
    all_translations = {}

# 3. 注册/注销翻译（4.5仅需2参数）
def register_translations():
    bpy.app.translations.register("Lehuye Plugin", all_translations)

def unregister_translations():
    bpy.app.translations.unregister("Lehuye Plugin")

# ===================== 原有逻辑 =====================
from . import main

def register():
    register_translations()  # 注册翻译
    main.register()

def unregister():
    main.unregister()
    unregister_translations()  # 注销翻译