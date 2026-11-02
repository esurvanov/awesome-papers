"""Превью моделей: импорт (.3ds / .max / .obj / .fbx / .glb), приведение к размеру, свет от неба Poly Haven, снимок 3/4.
Запуск: blender -b -P papers/2509.19162-growth/blender/preview_models.py -- <файл модели> <выход.png>"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
src, out = sys.argv[sys.argv.index("--") + 1:][:2]

bpy.ops.wm.read_factory_settings(use_empty=True)
for e in ("autodesk_3ds_format", "io_scene_max"):
    try:
        bpy.ops.preferences.addon_enable(module=f"bl_ext.blender_org.{e}")
    except Exception:
        pass
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.view_settings.view_transform = "AgX"
w = bpy.data.worlds.new("sky")
sc.world = w
w.use_nodes = True
env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(str(ROOT / "assets/polyhaven/sky.hdr"))
w.node_tree.links.new(env.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])

ext = Path(src).suffix.lower()
if ext == ".3ds":
    bpy.ops.import_scene.max3ds(filepath=src)
elif ext == ".max":
    bpy.ops.import_scene.max(filepath=src)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=src)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=src)
else:
    bpy.ops.import_scene.gltf(filepath=src)

meshes = [o for o in sc.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
# к реальному размеру: самая длинная сторона — 15 м (длина вагона); модели бывают в мм и в дюймах
ext0 = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
k = 15.0 / max(ext0, 1e-9)
root = bpy.data.objects.new("root", None)
sc.collection.objects.link(root)
for o in sc.objects:
    if o.parent is None and o is not root:
        o.parent = root
root.scale = (k, k, k)
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
size = max((hi - lo).length, 1e-6)
center = (lo + hi) / 2
faces = sum(len(o.data.polygons) for o in meshes)
bpy.ops.object.camera_add(location=center + Vector((size * 0.9, -size * 1.1, size * 0.45)))
cam = sc.camera = bpy.context.object
d = center - cam.location
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 35
cam.data.clip_end = 1000
bpy.ops.mesh.primitive_plane_add(size=size * 20, location=(center.x, center.y, lo.z))
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print(f"ПРЕВЬЮ {Path(src).name}: объектов {len(meshes)}, граней {faces}, размер {tuple(round(v, 2) for v in (hi - lo))}")
