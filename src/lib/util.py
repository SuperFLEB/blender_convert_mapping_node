from typing import Iterable, Callable
import bpy
from bpy.types import NodeTree, Node


def select_only_node(node_tree: NodeTree, node: Node):
    for node in node_tree.nodes:
        node.select = False
    node_tree.nodes.active = node

