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

class ColorRampToMapRange(Operator):
    """Convert between different types of numeric mapping nodes, like Color Ramp and Map Range"""
    bl_idname = "convert_mapping_node.color_ramp_to_map_range"
    bl_label = "Convert to Map Range Node"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context) -> bool:
        return context.active_node.type in ('VALTORGB',)

    def execute(self, context) -> Set[str]:
        def warn(message):
            self.report({'WARNING'}, message)

        def message(menu, _) -> None:
            menu.layout.label(text="It worked!", icon="SOLO_ON")

        node_tree = context.material.node_tree
        ramp_node: ShaderNodeValToRGB = context.active_node
        range_node: ShaderNodeMapRange = node_tree.nodes.new('ShaderNodeMapRange')
        range_node.location = ramp_node.location

        convert.ramp_to_range(ramp_node, range_node, warn)

        # Link the new node like the old one
        incoming_links = [lnk.from_socket for lnk in ramp_node.inputs["Fac"].links]
        for src in incoming_links:
            node_tree.links.new(src, range_node.inputs['Value'])

        outgoing_links = [lnk.to_socket for lnk in ramp_node.outputs["Color"].links] + [lnk.to_socket for lnk in ramp_node.outputs["Alpha"].links]
        for dest in outgoing_links:
            node_tree.links.new(range_node.outputs['Result'], dest)

        # Delete the old node and select the new one
        node_tree.nodes.remove(ramp_node)
        util.select_only_node(node_tree, range_node)

        return {'FINISHED'}


REGISTER_CLASSES = [ColorRampToMapRange]
