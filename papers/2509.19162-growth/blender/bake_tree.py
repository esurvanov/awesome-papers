"""Снимок дерева Poly Haven на прозрачном фоне — для лёгких «карточек» деревьев (station.trees_cards).
Запуск: blender -b -P papers/2509.19162-growth/blender/bake_tree.py"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import station as S

for k, (name, ang) in enumerate([("tree_small_02", 0.0), ("tree_small_02", 2.1), ("shrub_04", 0.0)]):
    S.setup(res=(1024, 1024), samples=48)
    sc = bpy.context.scene
    sc.render.film_transparent = True
    coll = S._gltf_collection(name)
    e = bpy.data.objects.new("t", None)
    e.instance_type, e.instance_collection = "COLLECTION", coll
    e.rotation_euler.z = ang
    sc.collection.objects.link(e)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in coll.objects if o.type == "MESH" for c in o.bound_box]
    h = max(p.z for p in pts)
    w = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))
    cx = (max(p.x for p in pts) + min(p.x for p in pts)) / 2
    bpy.ops.object.camera_add(location=(cx, -60, h / 2), rotation=(math.pi / 2, 0, 0))
    cam = sc.camera = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(h, w) * 1.04
    out = S.PH / f"card_{k}.png"
    sc.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print(f"КАРТОЧКА {out} высота {h:.1f} ширина {w:.1f}")
