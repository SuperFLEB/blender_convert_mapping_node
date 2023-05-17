import bpy
from ..operator import map_range_to_color_ramp
from ..operator import color_ramp_to_map_range

if "_LOADED" in locals():
    import importlib

    for mod in (map_range_to_color_ramp, color_ramp_to_map_range,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class ConvertMappingNodeSubmenu(bpy.types.Menu):
    bl_idname = 'convert_mapping_node.convert_mapping_node'
    bl_label = 'Convert Mapping Node'

    def draw(self, context) -> None:
        self.layout.operator(color_ramp_to_map_range.ColorRampToMapRange.bl_idname)
        self.layout.operator(map_range_to_color_ramp.MapRangeToColorRamp.bl_idname)

REGISTER_CLASSES = [ConvertMappingNodeSubmenu]
