# Convert Mapping Node

https://github.com/SuperFLEB/blender_convert_mapping_node

Convert between 2-step ColorRamp nodes with grayscale colors and a Map Range node. More conversions coming soon (?).

_This version was made quickly, dirtily, and late at night. It may have bugs._

## Features

* Convert from ColorRamp to Map Range and back

## To install

Either install the ZIP file from the release, clone this repository and use the
build_release.py script to build a ZIP file that you can install into Blender.

## To use

With the Color Ramp or Map Range node selected, use the right-click/W menu to convert.

## Caveats, To-dos

* Conversion only works between Float-type Map Range nodes and Color Ramp nodes with two grayscale elements.
* Conversion only uses default values for Map Range min/max inputs, not connected-node values
* Conversion between Constant Color Ramp nodes and Stepped Linear Map Range (and vice versa) nodes may be slightly imperfect.
