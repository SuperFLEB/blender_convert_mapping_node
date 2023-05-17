from typing import Iterable, Callable
import bpy

import bpy
from bpy.types import ShaderNodeMapRange, ShaderNodeValToRGB, ColorRamp
from math import ceil


def default_warn(message):
    print(f"(!) {message}")


def rgb_to_float(rgb):
    return (rgb[0] * 0.2126) + (rgb[1] * 0.7152) + (rgb[2] * 0.0722)


def ramp_to_range(ramp_node: ShaderNodeValToRGB, range_node: ShaderNodeMapRange,
                  warning_callback: Callable = default_warn):
    supported_interpolations = {
        'EASE': 'SMOOTHSTEP',
        'LINEAR': 'LINEAR',
        'CONSTANT': 'STEPPED',
    }
    unsupported_interpolations = {
        'CARDINAL': 'SMOOTHSTEP',
        'B_SPLINE': 'SMOOTHSTEP',
    }

    ramp: ColorRamp = ramp_node.color_ramp
    range_interpolation = supported_interpolations.get(ramp.interpolation,
                                                       unsupported_interpolations.get(ramp.interpolation, "SMOOTHSTEP"))

    elements = ramp.elements

    if len(elements) > 2:
        warning_callback(
            "Cannot convert a Color Ramp with more than 2 elements to a Map Range. Using first and last elements.")

    if ramp.interpolation not in supported_interpolations:
        warning_callback(
            f"There is no equivalent Map Range interpolation mode for {ramp.interpolation}. Using {range_interpolation}.")

    if range_interpolation == 'STEPPED':
        range_node.inputs['Steps'].default_value = 0.5
        range_node.clamp = True
        inputs = (
            elements[-1].position - 0.001,
            elements[-1].position + 0.001,
            rgb_to_float(elements[0].color),
            rgb_to_float(elements[-1].color)
        )
    else:
        inputs = (
            elements[0].position,
            elements[-1].position,
            rgb_to_float(elements[0].color),
            rgb_to_float(elements[-1].color)
        )

    (
        range_node.inputs['From Min'].default_value,
        range_node.inputs['From Max'].default_value,
        range_node.inputs['To Min'].default_value,
        range_node.inputs['To Max'].default_value
    ) = inputs

    range_node.interpolation_type = range_interpolation
    range_node.clamp = True


def range_to_ramp(range_node: ShaderNodeMapRange, ramp_node: ShaderNodeValToRGB,
                  warning_callback: Callable = default_warn):
    supported_interpolations = {
        'SMOOTHSTEP': 'EASE',
        'LINEAR': 'LINEAR',
        # CONSTANT also needs special processing
        'STEPPED': 'CONSTANT',
    }
    unsupported_interpolations = {
        'SMOOTHERSTEP': 'EASE',
    }

    ramp_interpolation = supported_interpolations.get(range_node.interpolation_type,
                                                      unsupported_interpolations.get(range_node.interpolation_type,
                                                                                     "LINEAR"))
    ramp_node.color_ramp.interpolation = ramp_interpolation
    range_values = [range_node.inputs[name].default_value for name in ["From Min", "To Min", "From Max", "To Max"]]

    if not supported_interpolations.get(range_node.interpolation_type):
        warning_callback(
            f"There is no equivalent Color Ramp interpolation mode for {range_node.interpolation_type}. Using {ramp_interpolation}.")

    # Clear any previously-existing stops
    while len(ramp_node.color_ramp.elements) > 1:
        ramp_node.color_ramp.elements.remove(ramp_node.color_ramp.elements[-1])
    ramp_node.color_ramp.elements[0].position = 0

    if ramp_interpolation != 'CONSTANT':
        ramp_values = list(zip(range_values[0::2], range_values[1::2]))
    else:
        steps = range_node.inputs['Steps'].default_value
        if steps < 0:
            warning_callback(
                "Negative Steps value is not supported. Setting to {abs(steps)}.")
            steps = abs(steps)

        stop_count = ceil(steps + 1)
        ramp_values = []
        gradient_start = min(range_values[0], range_values[2])
        gradient_len = abs(range_values[0] - range_values[2])
        gradient_step = (range_values[3] - range_values[1]) / steps

        for idx in range(0, stop_count):
            position = gradient_start + idx / (steps + 1) * gradient_len
            value = range_values[3] if idx == stop_count - 1 else range_values[1] + gradient_step * idx
            ramp_values.append((position, value))

    # Create new stops
    for idx, value in enumerate(ramp_values):
        # If the position is 0, reuse the existing 0 node, because we can't delete it
        element = ramp_node.color_ramp.elements.new(value[0]) if idx else ramp_node.color_ramp.elements[0]
        element.position = value[0]
        element.color = [value[1], value[1], value[1], 1]
