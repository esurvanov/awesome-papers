"""Пробный кадр станции в Blender: небо и щебень Poly Haven (CC0), рельсы и шпалы, пять вагонов-заготовок с номерами.
Заготовки вагонов заменятся моделями Sketchfab (assets/MANIFEST.md), когда будут скачаны.
Запуск (из корня): blender -b -P papers/2509.19162-growth/blender/shot_test.py -- videos/2509.19162-growth/blender/test.png"""
import math
import sys
import time
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
PH = ROOT / "assets" / "polyhaven"
OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else str(ROOT / "videos/2509.19162-growth/blender/test.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.view_transform = "AgX"

# небо
world = bpy.data.worlds.new("sky")
sc.world = world
world.use_nodes = True
nt = world.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(str(PH / "sky.hdr"))
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.0
nt.links.new(env.outputs["Color"], bg.inputs["Color"])


def mat_pbr(name, color=None, img=None, rough=0.6, metal=0.0, scale=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes
    b = n["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if color:
        b.inputs["Base Color"].default_value = (*color, 1)
    if img:
        tc = n.new("ShaderNodeTexCoord")
        mp = n.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale, scale, scale)
        m.node_tree.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        for key, inp, cs in (("Diffuse", "Base Color", "sRGB"), ("Rough", "Roughness", "Non-Color")):
            t = n.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(PH / f"gravel_{key}.jpg"))
            t.image.colorspace_settings.name = cs
            m.node_tree.links.new(mp.outputs["Vector"], t.inputs["Vector"])
            m.node_tree.links.new(t.outputs["Color"], b.inputs[inp])
        t = n.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(str(PH / "gravel_nor_gl.jpg"))
        t.image.colorspace_settings.name = "Non-Color"
        nm = n.new("ShaderNodeNormalMap")
        m.node_tree.links.new(mp.outputs["Vector"], t.inputs["Vector"])
        m.node_tree.links.new(t.outputs["Color"], nm.inputs["Color"])
        m.node_tree.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def box(name, size, loc, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 3
    o.data.materials.append(mat)
    return o


ground = mat_pbr("gravel", img=True, rough=0.9, scale=12)
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
bpy.context.object.data.materials.append(ground)

steel = mat_pbr("steel", (0.55, 0.55, 0.58), rough=0.3, metal=1.0)
wood = mat_pbr("sleeper", (0.18, 0.12, 0.08), rough=0.85)
paint = mat_pbr("wagon", (0.35, 0.09, 0.05), rough=0.55)
blue = mat_pbr("wagon_blue", (0.08, 0.22, 0.45), rough=0.5)
white = mat_pbr("number", (0.95, 0.95, 0.95), rough=0.4)

for y in (-0.75, 0.75):
    box("rail", (60, 0.08, 0.15), (0, y, 0.25), steel)
for x in range(-30, 31):
    box("sleeper", (0.25, 2.6, 0.15), (x * 0.9, 0, 0.1), wood)

nums = [3, 1, 5, 2, 4]
for k, num in enumerate(nums):
    x = (k - 2) * 7.4
    box(f"wagon{num}", (7.0, 2.9, 3.0), (x, 0, 2.0), paint if num != 5 else blue, bevel=0.08)
    for dx in (-2.4, 2.4):
        box("bogie", (2.2, 2.4, 0.5), (x + dx, 0, 0.55), steel)
    bpy.ops.object.text_add(location=(x, -1.47, 2.2), rotation=(math.pi / 2, 0, 0))
    t = bpy.context.object
    t.data.body = str(num)
    t.data.size = 1.6
    t.data.align_x, t.data.align_y = "CENTER", "CENTER"
    t.data.extrude = 0.02
    t.data.materials.append(white)

# солнце в тон неба и камера
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(35)))
bpy.context.object.data.energy = 3.0
bpy.ops.object.camera_add(location=(-14, -16, 4.5), rotation=(math.radians(80), 0, math.radians(-38)))
cam = bpy.context.object
cam.data.lens = 35
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 18
cam.data.dof.aperture_fstop = 4
sc.camera = cam

sc.render.filepath = OUT
t0 = time.time()
bpy.ops.render.render(write_still=True)
print(f"РЕНДЕР: {time.time() - t0:.1f} с → {OUT}")
