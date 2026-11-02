"""Кубический («воксельный») мир фильма «Тринадцатидолье» для простых кино-зарисовок: всё из блоков, свет дневной,
персонажи — кубические фигурки, подписи закреплены на камере. Сцены — shot_*.py рядом.
Запуск: blender -b -P papers/ega1-film/blender/shot_s02.py -- <выход.mp4> [--draft] [--still=12.5]"""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

import world as W

ROOT = W.ROOT
FPS = 24
DAY_SKY = W.PH / "sky.hdr"

_UNIT = {}


def frame(t):
    return int(round(t * FPS)) + 1


def setup(res=(1920, 1080), samples=16, sun=4.0):
    sc = W.setup(res=res, samples=samples, sky_strength=0.0, moon=0.0, haze=0.0, exposure=0.0)
    w = sc.world
    env = next(n for n in w.node_tree.nodes if n.type == "TEX_ENVIRONMENT")
    env.image = bpy.data.images.load(str(DAY_SKY), check_existing=True)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    moon = bpy.data.objects["moon"]
    moon.name = "sun"
    moon.data.energy, moon.data.color, moon.data.angle = sun, (1.0, 0.95, 0.85), math.radians(1.0)
    moon.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sc.render.fps = FPS
    return sc


def flat(name, color, rough=0.9, emit=None):
    return W.pbr(name, color=color, rough=rough, emit=emit)


def _unit_mesh(mat_name):
    """Единичный куб с данным материалом — одна сетка на материал, объекты её делят (быстро для тысяч блоков)."""
    key = f"unit_{mat_name}"
    if key in _UNIT:
        return _UNIT[key]
    me = bpy.data.meshes.new(key)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(bpy.data.materials[mat_name])
    _UNIT[key] = me
    return me


def block(loc, mat, size=(1, 1, 1), name="block", parent=None):
    o = bpy.data.objects.new(name, _unit_mesh(mat.name))
    o.location, o.scale = loc, size
    bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    bpy.context.scene.collection.objects.link(e)
    return e


# ---------- зал: стены из блоков с окнами, пол, потолок, тринадцать столов ----------

def hall(L=32, D=14, H=6, seed=1):
    rnd = random.Random(seed)
    stone = [flat("stone0", (0.42, 0.40, 0.37)), flat("stone1", (0.36, 0.34, 0.32)), flat("stone2", (0.47, 0.45, 0.41))]
    wood = [flat("plank0", (0.45, 0.30, 0.16)), flat("plank1", (0.40, 0.26, 0.14))]
    beam = flat("beam", (0.25, 0.16, 0.09))
    root = empty("hall")
    x0, y0 = -L / 2, -D / 2
    for i in range(L):  # пол
        for j in range(D):
            block((x0 + i + 0.5, y0 + j + 0.5, -0.5), rnd.choice(wood), parent=root, name="floor")
    for i in range(L):  # потолок
        for j in range(D):
            block((x0 + i + 0.5, y0 + j + 0.5, H + 0.5), beam, parent=root, name="ceil")
    for k in range(H):  # стены по периметру, окна — проёмы 2×2 каждые 4 блока на длинных стенах
        for i in range(-1, L + 1):
            for y in (y0 - 0.5, y0 + D + 0.5):
                window = (i % 5 in (1, 2)) and k in (2, 3)
                if not window:
                    block((x0 + i + 0.5, y, k + 0.5), rnd.choice(stone), parent=root, name="wall")
        for j in range(D):
            for x in (x0 - 0.5, x0 + L + 0.5):
                block((x, y0 + j + 0.5, k + 0.5), rnd.choice(stone), parent=root, name="wall")
    return root


def table(x, y=0.0, label="", zero=False):
    root = empty(f"table_{label or 'zero'}", (x, y, 0))
    top = flat("table_zero" if zero else "table_top", (0.55, 0.42, 0.18) if zero else (0.30, 0.20, 0.11))
    leg = flat("table_leg", (0.22, 0.15, 0.08))
    block((0, 0, 0.75), top, size=(1.6, 0.8, 0.1), parent=root, name="top")
    for dx in (-0.7, 0.7):
        for dy in (-0.3, 0.3):
            block((dx, dy, 0.35), leg, size=(0.1, 0.1, 0.7), parent=root, name="leg")
    paper = flat("paper", (0.95, 0.93, 0.86), rough=0.8)
    block((0.3, 0.05, 0.815), paper, size=(0.3, 0.42, 0.03), parent=root, name="paper")
    if label:
        t = text(label, size=0.22, color=(0.95, 0.9, 0.8) if zero else (0.9, 0.9, 0.9))
        t.parent = root
        t.location, t.rotation_euler = (-0.75, -0.41, 0.45), (math.pi / 2, 0, 0)
        t.data.align_x = "LEFT"
    return root


def card(parent, loc, red=False, name="card"):
    m = flat("card_red", (0.55, 0.08, 0.05), emit=((1, 0.2, 0.1), 0.8)) if red else flat("card_blue", (0.12, 0.35, 0.8), emit=((0.3, 0.6, 1), 0.8))
    return block(loc, m, size=(0.5, 0.26, 0.04), parent=parent, name=name)


def text(s, size=0.3, color=(1, 1, 1), emit=0.0):
    bpy.ops.object.text_add()
    t = bpy.context.object
    t.data.body, t.data.font, t.data.size = s, W.font(), size
    t.data.extrude = 0.01
    t.data.materials.append(flat(f"text_{color}_{emit}", color, emit=((*color,), emit) if emit else None))
    return t


# ---------- кубические персонажи ----------

def person(name, coat, loc, yaw=0.0, skin=(0.85, 0.65, 0.5), hair=(0.15, 0.1, 0.08), scarf=None):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, yaw)
    c, s, h = flat(f"{name}_coat", coat), flat(f"{name}_skin", skin), flat(f"{name}_hair", hair)
    legs = flat(f"{name}_legs", (coat[0] * 0.5, coat[1] * 0.5, coat[2] * 0.5))
    parts = {}
    for side, dx in (("l", -0.13), ("r", 0.13)):
        leg = empty(f"{name}_leg_{side}", (dx, 0, 0.8))
        leg.parent = root
        block((0, 0, -0.4), legs, size=(0.22, 0.26, 0.8), parent=leg, name="leg")
        parts[f"leg_{side}"] = leg
    block((0, 0, 1.18), c, size=(0.5, 0.3, 0.75), parent=root, name="body")
    for side, dx in (("l", -0.37), ("r", 0.37)):
        arm = empty(f"{name}_arm_{side}", (dx, 0, 1.5))
        arm.parent = root
        block((0, 0, -0.35), c, size=(0.2, 0.26, 0.7), parent=arm, name="arm")
        block((0, 0, -0.76), s, size=(0.18, 0.22, 0.12), parent=arm, name="hand")
        parts[f"arm_{side}"] = arm
    head = empty(f"{name}_head", (0, 0, 1.58))
    head.parent = root
    block((0, 0, 0.3), s, size=(0.5, 0.5, 0.5), parent=head, name="head")
    block((0, 0, 0.5), h, size=(0.54, 0.54, 0.16), parent=head, name="hair")
    block((0, -0.27, 0.32), flat("eye", (0.05, 0.05, 0.05)), size=(0.26, 0.04, 0.06), parent=head, name="eyes")
    if scarf:
        block((0, 0, 1.52), flat(f"{name}_scarf", scarf), size=(0.56, 0.36, 0.14), parent=root, name="scarf")
    parts["head"] = head
    root["parts"] = list(parts)
    return root, parts


def fcurves(obj):
    """Кривые анимации объекта (Blender 5: действие слоистое, fcurves лежат в channelbag слота)."""
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot) if hasattr(strip, "channelbag") else None
            if cb:
                out.extend(cb.fcurves)
    return out


def key(obj, t, loc=None, rot=None, interp="BEZIER"):
    f = frame(t)
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=f)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=f)
    for fc in fcurves(obj):
        for kp in fc.keyframe_points:
            if kp.co.x == f:
                kp.interpolation = interp


def walk(root, parts, t0, t1, a, b, yaw=None):
    """Идти из a в b за время t0..t1: тело скользит, ноги и руки качаются, голова чуть кивает."""
    a, b = Vector(a), Vector(b)
    if yaw is None:
        d = b - a
        yaw = math.atan2(d.y, d.x) - math.pi / 2  # фигурка смотрит в -Y в своей системе
    key(root, t0, loc=a, rot=(0, 0, yaw), interp="LINEAR")
    key(root, t1, loc=b, rot=(0, 0, yaw), interp="LINEAR")
    step = 0.45
    n = max(1, int((t1 - t0) / step))
    for i in range(n + 1):
        t = t0 + i * (t1 - t0) / n
        s = 0.6 if i % 2 == 0 else -0.6
        if i in (0, n):
            s = 0.0
        key(parts["leg_l"], t, rot=(s, 0, 0))
        key(parts["leg_r"], t, rot=(-s, 0, 0))
        key(parts["arm_l"], t, rot=(-s * 0.8, 0, 0))
        key(parts["arm_r"], t, rot=(s * 0.8, 0, 0))


def stand(root, parts, t, loc, yaw):
    key(root, t, loc=loc, rot=(0, 0, yaw))
    for k in ("leg_l", "leg_r", "arm_l", "arm_r"):
        key(parts[k], t, rot=(0, 0, 0))


def reach(parts, t0, t1, side="r", angle=-1.2):
    key(parts[f"arm_{side}"], t0, rot=(0, 0, 0))
    key(parts[f"arm_{side}"], t0 + (t1 - t0) * 0.4, rot=(angle, 0, 0))
    key(parts[f"arm_{side}"], t1, rot=(0, 0, 0))


def show(obj, t0, t1=None):
    """Объект виден с t0 (до t1): до того и после — скрыт в рендере."""
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert("hide_render", frame=1)
    obj.keyframe_insert("hide_viewport", frame=1)
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert("hide_render", frame=frame(t0))
    obj.keyframe_insert("hide_viewport", frame=frame(t0))
    if t1 is not None:
        obj.hide_render = True
        obj.hide_viewport = True
        obj.keyframe_insert("hide_render", frame=frame(t1))
        obj.keyframe_insert("hide_viewport", frame=frame(t1))


# ---------- камера, планы, подписи ----------

def camera(lens=35):
    cam = W.camera((0, -10, 2), (0, 0, 1), lens=lens)
    cam.data.dof.use_dof = False
    return cam


def cam_at(cam, t, loc, look, lens=None):
    """Ключ камеры в момент t: где стоит и куда смотрит (через пустышку-цель)."""
    sc = bpy.context.scene
    if cam.get("target_obj") is None:
        e = bpy.data.objects.new("cam_target", None)
        sc.collection.objects.link(e)
        con = cam.constraints.new("TRACK_TO")
        con.target, con.track_axis, con.up_axis = e, "TRACK_NEGATIVE_Z", "UP_Y"
        cam["target_obj"] = e.name
    e = bpy.data.objects[cam["target_obj"]]
    cam.location = loc
    cam.keyframe_insert("location", frame=frame(t))
    e.location = look
    e.keyframe_insert("location", frame=frame(t))
    if lens:
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=frame(t))


def shot(cam, t0, t1, a_loc, a_look, b_loc=None, b_look=None, lens=None):
    """План t0..t1: камера из a в b (или стоит). На границе плана — монтажная склейка (ключ на соседнем кадре)."""
    b_loc, b_look = b_loc or a_loc, b_look or a_look
    cam_at(cam, t0, a_loc, a_look, lens=lens)
    cam_at(cam, t1 - 1 / FPS, b_loc, b_look, lens=lens)
    for ob in (cam, bpy.data.objects[cam["target_obj"]]):
        for fc in fcurves(ob):
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame(t1 - 1 / FPS)) < 0.5:
                    kp.interpolation = "CONSTANT"


def caption(cam, s, t0, t1, size=0.042, y=-0.27):
    """Субтитр, закреплённый на камере: виден с t0 до t1."""
    if len(s) > 44:  # длинная подпись — в две строки, чтобы влезала и в узкий план (50 мм)
        cut = s.rfind(" ", 0, len(s) // 2 + 8)
        s = s[:cut] + "\n" + s[cut + 1:]
    lines = s.split("\n")
    t = text(s, size=size, color=(1, 1, 1), emit=2.0)
    t.data.align_x = "CENTER"
    t.data.space_line = 1.15
    t.parent = cam
    t.location, t.rotation_euler = (0, y + (len(lines) - 1) * size * 1.15, -1.5), (0, 0, 0)
    w = max(1.0, max(len(l) for l in lines) * size * 0.52)
    h = size * (0.9 + 1.15 * len(lines))
    bg = block((0, y + size * 0.33 + (len(lines) - 1) * size * 0.55, -1.51), flat("cap_bg", (0, 0, 0), rough=1.0), size=(w, h, 0.001), parent=cam, name="cap_bg")
    try:
        bg.data.materials[0].surface_render_method = "BLENDED"
    except AttributeError:
        pass
    bg.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.6
    show(t, t0, t1)
    show(bg, t0, t1)
    return t


def finish(out, length, draft=True, still=None):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frame(length)
    if draft:
        W.draft(sc)
    if still is not None:
        sc.frame_current = frame(float(still))
        W.render(out)
        return
    if hasattr(sc.render.image_settings, "media_type"):
        sc.render.image_settings.media_type = "VIDEO"
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath = str(out)
    bpy.ops.render.render(animation=True)
