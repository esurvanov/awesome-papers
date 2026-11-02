"""Мир фильма «Общая точка» в Blender: ночной горный город Сарань после толчка, дроны, штаб.
Модели: Kenney City Kit (CC0, assets/kenney), пропсы и небо Poly Haven (CC0, assets/polyhaven) — см. assets/MANIFEST.md.
Скрипты кадров still_*.py и shot_*.py рядом: blender -b -P papers/ega1-film/blender/still_town.py -- <выход.png> [--draft]."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector, noise

ROOT = Path(__file__).resolve().parents[3]
PH = ROOT / "assets" / "polyhaven"
KENNEY = ROOT / "assets" / "kenney"

NIGHT_SKY = PH / "hdri" / "kloppenheim_02_puresky_2k.hdr"   # ясная ночь, звёзды, без земли
BUILDING_H = 9.0     # средняя высота дома в метрах (модели Kenney масштабируются по ней)


# ---------- сцена, свет, небо ----------

def setup(res=(1920, 1080), samples=32, sky_strength=0.25, moon=0.9, haze=0.0006, exposure=0.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = exposure  # ночь: камера «открыта», как у настоящей ночной съёмки
    # «Игровое» качество: без трассировки отражений и с лёгким объёмом. Трассировка + объём с 96 пробами на 1080p
    # вешали EEVEE на видеокарте (23.10.2026) — процесс стоял, компьютер замирал. Качество игры в браузере нас устраивает.
    try:
        sc.eevee.taa_render_samples = min(samples, 24)
        sc.eevee.use_raytracing = False
        sc.eevee.use_shadows = True
        sc.eevee.shadow_resolution_scale = 0.5
        sc.eevee.volumetric_tile_size = "8"
        sc.eevee.volumetric_samples = 32
        sc.eevee.use_volumetric_shadows = False
    except AttributeError:
        pass
    w = bpy.data.worlds.new("night")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(NIGHT_SKY))
    nt.links.new(env.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = sky_strength
    if haze:  # дымка и пыль после толчка: лучи дронов видны в воздухе; объём — коробкой, чтобы не гасить небо
        try:
            sc.eevee.volumetric_start, sc.eevee.volumetric_end = 0.1, 1500.0
        except AttributeError:
            pass
        haze_box(haze)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(140)))  # луна: холодный низкий свет
    m = bpy.context.object
    m.name = "moon"
    m.data.energy = moon
    m.data.color = (0.62, 0.72, 1.0)
    m.data.angle = math.radians(2.0)
    return sc


def haze_box(density, size=(2400, 2400, 420), loc=(0, 0, 200), color=(0.55, 0.6, 0.7)):
    m = bpy.data.materials.new("haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = density
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Anisotropy"].default_value = 0.55
    nt.links.new(v.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name, o.scale = "haze", size
    o.display_type = "WIRE"
    o.data.materials.append(m)
    return o


def pbr(name, prefix=None, color=(0.5, 0.5, 0.5), rough=0.6, metal=0.0, scale=1.0, box=False, emit=None):
    """Материал: цвет или текстуры Poly Haven (<prefix>_Diffuse/_Rough/_nor_gl.jpg); emit — (цвет, сила) свечения."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n = m.node_tree, m.node_tree.nodes
    b = n["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Base Color"].default_value = (*color, 1)
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1)
        b.inputs["Emission Strength"].default_value = emit[1]
    if prefix:
        tc, mp = n.new("ShaderNodeTexCoord"), n.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale, scale, scale)
        nt.links.new(tc.outputs["Object" if box else "UV"], mp.inputs["Vector"])

        def tex(key, cs):
            t = n.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(PH / f"{prefix}_{key}.jpg"), check_existing=True)
            t.image.colorspace_settings.name = cs
            if box:
                t.projection, t.projection_blend = "BOX", 0.25
            nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
            return t

        nt.links.new(tex("Diffuse", "sRGB").outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tex("Rough", "Non-Color").outputs["Color"], b.inputs["Roughness"])
        nm = n.new("ShaderNodeNormalMap")
        nt.links.new(tex("nor_gl", "Non-Color").outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


# ---------- рельеф: долина с городом, вокруг горы ----------

def height(x, y, valley=170.0, peak=200.0):
    """Высота земли: в долине радиусом valley почти плоско, дальше склоны до peak (на 700 м от края долины) с шумом."""
    r = math.hypot(x, y)
    rim = min(1.0, max(0.0, (r - valley) / 700.0))
    h = peak * rim ** 1.7
    h += 5.0 * noise.noise(Vector((x * 0.004, y * 0.004, 0.0))) * (1 + 6 * rim)
    h += 1.0 * noise.noise(Vector((x * 0.03, y * 0.03, 1.0)))
    return h


def terrain(size=2400, n=200):
    import bmesh
    bm = bmesh.new()
    step = size / n
    verts = [[bm.verts.new((-size / 2 + i * step, -size / 2 + j * step, height(-size / 2 + i * step, -size / 2 + j * step)))
              for j in range(n + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(n):
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    me = bpy.data.meshes.new("terrain")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("terrain", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(pbr("rock_ground", "gravel", rough=0.95, scale=0.3, box=True))
    for p in o.data.polygons:
        p.use_smooth = True
    return o


# ---------- город из Kenney City Kit ----------

def _kenney(kit, name):
    """Коллекция с одной моделью Kenney (импорт один раз), высота приведена к метрам."""
    key = f"kenney_{kit}_{name}"
    coll = bpy.data.collections.get(key)
    if coll:
        return coll
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(KENNEY / kit / "Models" / "GLB format" / f"{name}.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    coll = bpy.data.collections.new(key)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    coll["height"] = max((o.matrix_world @ Vector(c)).z for o in new if o.type == "MESH" for c in o.bound_box)
    return coll


def instance(coll, loc, rot_z=0.0, scale=1.0, name=None):
    e = bpy.data.objects.new(name or coll.name, None)
    e.instance_type, e.instance_collection = "COLLECTION", coll
    e.location, e.rotation_euler, e.scale = loc, (0, 0, rot_z), (scale,) * 3
    bpy.context.scene.collection.objects.link(e)
    return e


def town(seed=3, blocks=12, pitch=14.0, lit=0.1, radius=125):
    """Квартальная сетка домов в долине; часть окон (lit) светится от аварийных фонарей."""
    rnd = random.Random(seed)
    houses = [_kenney("city-kit-suburban", f"building-type-{c}") for c in "abcdefghijklmnopqrstu"]
    units = [_kenney("city-kit-industrial", f"building-{c}") for c in "abcdefg"]
    objs = []
    for i in range(-blocks, blocks + 1):
        for j in range(-blocks, blocks + 1):
            x, y = i * pitch + rnd.uniform(-1.5, 1.5), j * pitch + rnd.uniform(-1.5, 1.5)
            if math.hypot(x, y) > radius or rnd.random() < 0.1:
                continue
            industrial = math.hypot(x - 70, y + 60) < 45
            c = rnd.choice(units if industrial else houses)
            scale = (BUILDING_H * (1.6 if industrial else 1.0)) / c["height"]  # высота модели — в метры
            e = instance(c, (x, y, height(x, y) - 0.2), rot_z=rnd.choice((0, math.pi / 2, math.pi, -math.pi / 2)),
                         scale=scale * rnd.uniform(0.85, 1.15))
            objs.append(e)
            if rnd.random() < lit:  # тёплый свет в окне: кто-то жив
                bpy.ops.object.light_add(type="POINT", location=(x, y, height(x, y) + 3.0))
                L = bpy.context.object
                L.data.energy, L.data.color, L.data.shadow_soft_size = 120, (1.0, 0.72, 0.4), 1.5
    return objs


def forest(n=600, seed=11, inner=60, outer=520):
    """Деревья Kenney по склонам и между домами: силуэты на фоне неба, город не висит на плоском диске.
    (Ель Poly Haven fir_tree_01 — сотни объектов на дерево, 40 штук вешают рендер; для дальних планов не годится.)"""
    rnd = random.Random(seed)
    trees = [_kenney("city-kit-suburban", "tree-large"), _kenney("city-kit-suburban", "tree-small")]
    out = []
    for _ in range(n):
        r, a = rnd.uniform(inner, outer), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if r < 130 and rnd.random() < 0.7:
            continue  # в городе деревья реже
        t = rnd.choice(trees)
        out.append(instance(t, (x, y, height(x, y) - 0.3), rot_z=rnd.uniform(0, 6.28), scale=rnd.uniform(8, 15) / t["height"]))
    return out


def fires(n=4, seed=5):
    """Очаги пожаров: оранжевые точки с дымом (конус дыма — объём)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        x, y = rnd.uniform(-100, 100), rnd.uniform(-100, 100)
        z = height(x, y)
        bpy.ops.object.light_add(type="POINT", location=(x, y, z + 4))
        L = bpy.context.object
        L.name = f"fire{k}"
        L.data.energy, L.data.color, L.data.shadow_soft_size = 20000, (1.0, 0.45, 0.12), 4
        bpy.ops.mesh.primitive_cone_add(radius1=4, radius2=13, depth=80, location=(x + 7, y + 4, z + 38))
        s = bpy.context.object
        s.name = f"smoke{k}"
        s.rotation_euler = (math.radians(8), math.radians(-12), 0)
        s.data.materials.append(_smoke())
        out.append((x, y, z))
    return out


def _smoke():
    m = bpy.data.materials.get("smoke")
    if m:
        return m
    m = bpy.data.materials.new("smoke")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = 0.03
    v.inputs["Color"].default_value = (0.3, 0.27, 0.25, 1)
    nt.links.new(v.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    return m


# ---------- дрон: корпус, четыре луча, винты, огни, прожектор вниз ----------

def drone(loc, name="drone", yaw=0.0, beam=True, size=1.0):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.location, root.rotation_euler = loc, (0, 0, yaw)
    body = pbr("drone_body", color=(0.08, 0.08, 0.09), rough=0.35, metal=0.3)
    nav_r = pbr("drone_red", color=(0.1, 0, 0), emit=((1, 0.05, 0.02), 40))
    nav_g = pbr("drone_green", color=(0, 0.1, 0), emit=((0.1, 1, 0.2), 40))
    parts = []

    def add(o):
        o.parent = root
        parts.append(o)
        return o

    bpy.ops.mesh.primitive_cube_add(size=1)
    b = add(bpy.context.object)
    b.scale = (0.5 * size, 0.5 * size, 0.16 * size)
    b.data.materials.append(body)
    for k, (dx, dy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03 * size, depth=0.75 * size,
                                            location=(dx * 0.32 * size, dy * 0.32 * size, 0),
                                            rotation=(0, math.pi / 2, math.atan2(dy, dx)))
        add(bpy.context.object).data.materials.append(body)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3 * size, depth=0.012 * size,
                                            location=(dx * 0.62 * size, dy * 0.62 * size, 0.06 * size))
        rot = add(bpy.context.object)
        rot.data.materials.append(pbr("drone_rotor", color=(0.3, 0.3, 0.32), rough=0.4))
        rot.name = f"{name}_rotor{k}"
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035 * size, location=(dx * 0.62 * size, dy * 0.62 * size, -0.03 * size))
        add(bpy.context.object).data.materials.append(nav_g if dx > 0 else nav_r)
    if beam:
        bpy.ops.object.light_add(type="SPOT", location=(0, 0, -0.1 * size), rotation=(0, 0, 0))
        L = add(bpy.context.object)
        L.name = f"{name}_beam"
        L.data.energy, L.data.spot_size, L.data.spot_blend = 100000 * size, math.radians(24), 0.3
        L.data.color, L.data.shadow_soft_size = (0.85, 0.92, 1.0), 0.2
        L.rotation_euler = (0, 0, 0)  # прожектор светит по -Z: вниз
    return root


def spin_rotors(root, fps=24, t_end=10.0, rps=20.0):
    for o in root.children:
        if "_rotor" in o.name:
            o.rotation_euler.z = 0
            o.keyframe_insert("rotation_euler", index=2, frame=1)
            o.rotation_euler.z = 2 * math.pi * rps * t_end
            o.keyframe_insert("rotation_euler", index=2, frame=int(t_end * fps) + 1)
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"


# ---------- пропсы Poly Haven ----------

def ph(name):
    """Коллекция с моделью Poly Haven (glTF, импорт один раз)."""
    key = f"ph_{name}"
    coll = bpy.data.collections.get(key)
    if coll:
        return coll
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(PH / "models" / name / f"{name}_1k.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    coll = bpy.data.collections.new(key)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll


def font():
    return bpy.data.fonts.get("Arial") or bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial.ttf")


def box(name, size, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    return o


# ---------- камера и рендер ----------

def camera(loc, look, lens=35, dof=None):
    """Камера; z=None в loc — встать на 60 м над землёй в этой точке."""
    if loc[2] is None:
        loc = (loc[0], loc[1], height(loc[0], loc[1]) + 60)
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.clip_end = 5000
    if dof:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (Vector(look) - Vector(loc)).length
        cam.data.dof.aperture_fstop = dof
    bpy.context.scene.camera = cam
    return cam


def draft(sc):
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    try:
        sc.eevee.taa_render_samples = 12
    except AttributeError:
        pass


def render(out):
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
