import bpy
from typing import Set
from bpy.types import Operator, ShaderNodeMapRange, ShaderNodeValToRGB, ColorRamp
from ..lib import pkginfo
from ..lib import util
from ..lib import convert

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, util, convert):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class MapRangeToColorRamp(Operator):
    """Convert between different types of numeric mapping nodes, like Color Ramp and Map Range"""
    bl_idname = "convert_mapping_node.map_range_to_color_ramp"
    bl_label = "Convert to Color Ramp Node"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def can_show(cls, context) -> bool:
        return context.active_node.type in ('MAP_RANGE',)

    def execute(self, context) -> Set[str]:
        def warn(message):
            self.report({'WARNING'}, message)

        def message(menu, _) -> None:
            menu.layout.label(text="It worked!", icon="SOLO_ON")

        node_tree = context.space_data.edit_tree
        range_node: ShaderNodeMapRange = context.active_node
        ramp_node: ShaderNodeValToRGB = node_tree.nodes.new('ShaderNodeValToRGB')
        ramp_node.location = range_node.location

        convert.range_to_ramp(range_node, ramp_node, warn)

        # Link the new node like the old one
        incoming_links = [lnk.from_socket for lnk in range_node.inputs["Value"].links]
        for src in incoming_links:
            node_tree.links.new(src, ramp_node.inputs['Fac'])

        outgoing_links = [lnk.to_socket for lnk in range_node.outputs["Result"].links]
        for dest in outgoing_links:
            node_tree.links.new(ramp_node.outputs['Color'], dest)

        # Delete the old node and select the new one
        node_tree.nodes.remove(range_node)
        util.select_only_node(node_tree, ramp_node)

        return {'FINISHED'}


REGISTER_CLASSES = [MapRangeToColorRamp]
