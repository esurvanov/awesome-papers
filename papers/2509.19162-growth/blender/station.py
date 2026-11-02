"""Мир «сортировочная станция» в Blender: небо и материалы Poly Haven, модели вагонов (assets/private — только для частного
просмотра, см. assets/MANIFEST.md), рельсы со шпалами на щебне, таблички с номерами, вышка диспетчера, камера.
Используется скриптами кадров shot_*.py рядом: blender -b -P papers/2509.19162-growth/blender/shot_a01.py -- <выход>."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
PH = ROOT / "assets" / "polyhaven"
O3 = ROOT / "assets" / "private" / "o3"

# модели вагонов (файлы — assets/private/o3/<папка>); номер на табличке рисуется отдельно
WAGONS = {
    "серый":    "railroad-freight-boxcar_119305",   # крытый, потрёпанный — вагон-герой
    "рок":      "freight-train-boxcar_132276",      # крытый «The Rock»
    "синий":    "train-boxcar_132262",              # европейский крытый
    "цистерна": "oil-tank-car_119311",              # белая цистерна
    "хром":     "freight-train-tank-car_132266",    # хромированная цистерна
    "платформа": "railroad-flatcar_119309",
}
LOCO = "emd-sd40-diesel-electric-locomotive_124181"
PERSON = "mechanic-man_124845"            # диспетчер
LEVER = "industrial-ground-throw-lever_188836"  # ручной стрелочный рычаг
SIGNAL = "city-railway-stop-signal_185957"
GAUGE, RAIL_TOP = 1.52, 0.42  # колея (м) и высота основания рельса над землёй
RAIL_HEAD = 0.57              # верх головки рельса: на нём стоят колёса
TRACK_SPACING = 4.8           # между осями соседних путей


def enable_importers():
    for e in ("autodesk_3ds_format", "io_scene_max"):
        try:
            bpy.ops.preferences.addon_enable(module=f"bl_ext.blender_org.{e}")
        except Exception:
            pass


def setup(res=(1920, 1080), samples=32, sky_strength=1.0, sun=3.0, haze=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    enable_importers()
    sc = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    try:
        sc.eevee.taa_render_samples = samples
        sc.eevee.use_raytracing = True
        sc.eevee.use_shadows = True
    except AttributeError:
        pass
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(PH / "sky_pure.hdr"))  # небо без земли: своя земля уходит к горизонту
    w.node_tree.links.new(env.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = sky_strength
    if haze:  # дымка к горизонту — земля не обрывается краем
        vol = w.node_tree.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Density"].default_value = 0.0012
        vol.inputs["Color"].default_value = (0.78, 0.84, 0.92, 1)
        w.node_tree.links.new(vol.outputs["Volume"], w.node_tree.nodes["World Output"].inputs["Volume"])
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(68), 0, math.radians(-60)))  # низкое вечернее солнце: длинные тени
    bpy.context.object.data.energy = sun * 1.3
    bpy.context.object.data.color = (1.0, 0.88, 0.72)
    bpy.context.object.data.angle = math.radians(1.5)
    return sc


def pbr(name, prefix=None, color=(0.5, 0.5, 0.5), rough=0.6, metal=0.0, scale=1.0, box=False, tint=None):
    """Материал: цвет или набор текстур Poly Haven (<prefix>_Diffuse/_Rough/_nor_gl.jpg); box — проекция кубом (без развёртки)."""
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

        diff = tex("Diffuse", "sRGB")
        if tint:  # подкраска и крупные пятна оттенка — земля не выглядит плиткой
            mix = n.new("ShaderNodeMix")
            mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            noise = n.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 0.02
            ramp = n.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color = (tint[0] * 0.75, tint[1] * 0.8, tint[2] * 0.7, 1)
            ramp.color_ramp.elements[1].color = (tint[0] * 1.15, tint[1] * 1.1, tint[2] * 0.9, 1)
            nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
            nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(diff.outputs["Color"], mix.inputs["A"])
            nt.links.new(ramp.outputs["Color"], mix.inputs["B"])
            nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
        else:
            nt.links.new(diff.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tex("Rough", "Non-Color").outputs["Color"], b.inputs["Roughness"])
        nm = n.new("ShaderNodeNormalMap")
        nt.links.new(tex("nor_gl", "Non-Color").outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def font():
    """Шрифт с кириллицей для надписей в 3D (встроенный в Blender её не знает)."""
    return bpy.data.fonts.get("Arial") or bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial.ttf")


def box(name, size, loc, mat, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
    o.data.materials.append(mat)
    return o


def ground(size=8000):
    bpy.ops.mesh.primitive_plane_add(size=size)
    g = bpy.context.object
    g.data.materials.append(pbr("ground", "lgrass", rough=0.95, scale=size / 5, tint=(0.42, 0.72, 0.30)))
    return g


def track(length=120, y=0.0, x0=0.0):
    """Путь: насыпь из щебня, деревянные шпалы, стальные рельсы — вдоль X."""
    ballast = pbr("ballast", "gravel", rough=1.0, scale=0.5, box=True)
    wood = pbr("sleeper", "wood", rough=0.9, scale=1.0, box=True)
    steel = pbr("rail", color=(0.42, 0.40, 0.38), rough=0.35, metal=1.0)
    rust = pbr("rail_rust", "rust", rough=0.8, scale=2.0, box=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x0, y, 0.12))
    b = bpy.context.object
    b.scale = (length, 3.4, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    bev = b.modifiers.new("slope", "BEVEL")
    bev.width, bev.segments = 0.25, 1
    b.data.materials.append(ballast)
    n = int(length / 0.6)
    for k in range(n):
        box("sleeper", (0.24, 2.6, 0.16), (x0 - length / 2 + 0.3 + k * 0.6, y, 0.3), wood)
    for s in (-1, 1):
        box("rail_foot", (length, 0.14, 0.03), (x0, y + s * GAUGE / 2, 0.395), rust)
        box("rail_web", (length, 0.03, 0.12), (x0, y + s * GAUGE / 2, 0.46), rust)
        box("rail_head", (length, 0.07, 0.05), (x0, y + s * GAUGE / 2, 0.545), steel)


def _first_model(folder):
    d = O3 / folder
    for pat in ("*.3ds", "*.3DS", "*.max", "*.MAX"):
        f = sorted(d.rglob(pat))
        if f:
            return f[0]
    raise FileNotFoundError(folder)


_CACHE = {}


def _dup(obj, parent, coll):
    c = obj.copy()  # данные сетки общие — копия лёгкая
    coll.objects.link(c)
    c.parent = parent
    if parent is not None:
        c.matrix_parent_inverse = obj.matrix_parent_inverse.copy()
    for ch in obj.children:
        _dup(ch, c, coll)
    return c


def model(folder, length=14.0, name=None):
    """Модель в пустышке-корне: длинная сторона — вдоль X, длина `length` м, низ на головке рельса, центр в 0.
    Файл импортируется один раз; дальше — копии (повторный импорт того же файла ломает размеры)."""
    key = (folder, length)
    if key in _CACHE:
        c = _dup(_CACHE[key], None, bpy.context.scene.collection)
        c.name = name or folder
        c.location = (0, 0, 0)
        bpy.context.view_layer.update()
        c["size"] = _CACHE[key]["size"]
        c.location = _CACHE[key]["home"]
        bpy.context.view_layer.update()
        return c
    before = set(bpy.data.objects)
    f = _first_model(folder)
    if f.suffix.lower() == ".3ds":
        bpy.ops.import_scene.max3ds(filepath=str(f))
    else:
        bpy.ops.import_scene.max(filepath=str(f))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    root = bpy.data.objects.new(name or folder, None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    for o in meshes:  # пустые и розовые (без текстуры) материалы — в спокойный серый
        for slot in o.material_slots:
            mt = slot.material
            if mt and mt.use_nodes:
                for nd in mt.node_tree.nodes:
                    if nd.type != "TEX_IMAGE":
                        continue
                    ok = nd.image is not None and Path(bpy.path.abspath(nd.image.filepath)).exists()
                    if ok:
                        try:
                            nd.image.reload()
                            ok = nd.image.size[0] > 0
                        except Exception:
                            ok = False
                    if not ok:  # нет файла или формат не читается — иначе Blender красит розовым
                        mt.node_tree.nodes.remove(nd)
                        pb = mt.node_tree.nodes.get("Principled BSDF")
                        if pb and not pb.inputs["Base Color"].is_linked:
                            pb.inputs["Base Color"].default_value = (0.28, 0.30, 0.33, 1)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    ext = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    if ext[1] > ext[0]:
        root.rotation_euler.z = math.pi / 2
    if ext[2] > max(ext[0], ext[1]):  # стоит «на торце» — положить
        root.rotation_euler.x = math.pi / 2
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    k = length / max(max(p.x for p in pts) - min(p.x for p in pts), 1e-6)
    root.scale = (k, k, k)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    # посадка по колёсам: нижние 25 % модели — тележки; их середина встаёт на ось пути, низ — на головку рельса
    verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    low = [v for v in verts if v.z < lo.z + 0.25 * (hi.z - lo.z)] or verts
    cx = (min(v.x for v in low) + max(v.x for v in low)) / 2
    cy = (min(v.y for v in low) + max(v.y for v in low)) / 2
    root.location -= Vector((cx, cy, lo.z - RAIL_HEAD))
    bpy.context.view_layer.update()
    # точка вращения — середина по колёсам: вагон поворачивается на съезде вокруг себя, а не вокруг угла модели
    pivot = bpy.data.objects.new(f"{name or folder}_pivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    root.parent = pivot
    root = pivot
    root["size"] = tuple(hi - lo)
    root["home"] = (0.0, 0.0, 0.0)
    # заготовка — в скрытой коллекции; в кадр идут только копии (к заготовке ничего не прикрепляется)
    hidden = bpy.data.collections.get("templates") or bpy.data.collections.new("templates")
    if hidden.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(hidden)
    for o in [root] + list(root.children_recursive):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        hidden.objects.link(o)
    hidden.hide_render = True
    hidden.hide_viewport = True
    _CACHE[key] = root
    return model(folder, length, name)


def place(root, x, y=0.0):
    root.location.x += x
    root.location.y += y
    bpy.context.view_layer.update()
    return root


def number_plate(root, num, side=-1, color=(0.97, 0.97, 0.95)):
    """Табличка с крупным номером на боку вагона, обращённом к камере (side=-1 — сторона −Y)."""
    sx, sy, sz = root["size"]
    c = root.location
    y = c.y + side * (sy / 2 + 0.03)
    z = RAIL_TOP + 0.15 + sz * 0.55
    plate = box(f"plate{num}", (1.8, 0.04, 1.5), (c.x, y, z), pbr("plate", color=color, rough=0.5), bevel=0.05)
    bpy.ops.object.text_add(location=(c.x, y + side * 0.03, z), rotation=(math.pi / 2, 0, 0 if side < 0 else math.pi))
    t = bpy.context.object
    t.data.body = str(num)
    t.data.font = font()
    t.data.size = 1.2
    t.data.align_x, t.data.align_y = "CENTER", "CENTER"
    t.data.extrude = 0.01
    t.data.materials.append(pbr("plate_num", color=(0.03, 0.03, 0.03), rough=0.4))
    plate.parent = t.parent = None
    return plate, t


def tower(loc=(0, 0, 0), floors=2):
    """Вышка диспетчера: кирпичный низ, деревянная кабина с окнами по кругу, крыша."""
    x, y, z = loc
    brick = pbr("brick", "brick", rough=0.9, scale=0.6, box=True)
    wood = pbr("tower_wood", "wood", rough=0.8, scale=0.8, box=True)
    glass = pbr("glass", color=(0.6, 0.75, 0.8), rough=0.05, metal=0.0)
    glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.6
    roof = pbr("roof", "rust", rough=0.7, scale=0.5, box=True)
    h = 3.2 * floors
    box("tower_base", (6, 5, h), (x, y, z + h / 2), brick)
    box("cabin", (7, 6, 2.6), (x, y, z + h + 1.3), wood)
    box("windows", (7.05, 6.05, 1.4), (x, y, z + h + 1.5), glass)
    box("roof", (8, 7, 0.4), (x, y, z + h + 2.8), roof, bevel=0.1)
    box("roof_top", (5.5, 4.5, 0.6), (x, y, z + h + 3.2), roof, bevel=0.1)


def camera(loc, look, lens=35, dof=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.clip_end = 2000
    if dof:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (Vector(look) - Vector(loc)).length
        cam.data.dof.aperture_fstop = dof
    bpy.context.scene.camera = cam
    return cam


def render(out):
    sc = bpy.context.scene
    sc.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)


# ---------- путевая сеть: пути — ломаные; вагоны ездят только по ним ----------

def _seg_track(a, b, mats, sleepers=True):
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = b - a
    L = d.length
    ang = math.atan2(d.y, d.x)
    mid = (a + b) / 2
    ballast, wood, steel, rust = mats
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid.x, mid.y, 0.12), rotation=(0, 0, ang))
    o = bpy.context.object
    o.scale = (L + 1.0, 3.6, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    bev = o.modifiers.new("slope", "BEVEL")
    bev.width, bev.segments = 0.35, 1
    o.data.materials.append(ballast)
    if sleepers:  # одна шпала и массив вдоль пути — тысячи шпал без тысяч объектов
        n = max(1, int(L / 0.6))
        p = a + d * (0.5 / n)
        sl = box("sleeper", (0.24, 2.6, 0.16), (p.x, p.y, 0.3), wood, rot=(0, 0, ang))
        arr = sl.modifiers.new("arr", "ARRAY")
        arr.count = n
        arr.use_relative_offset = True
        arr.relative_offset_displace = (L / n / 0.24, 0, 0)
    side = Vector((-math.sin(ang), math.cos(ang), 0))
    for s in (-1, 1):
        c = mid + side * s * GAUGE / 2
        box("rail_foot", (L, 0.14, 0.03), (c.x, c.y, 0.395), rust, rot=(0, 0, ang))
        box("rail_web", (L, 0.03, 0.12), (c.x, c.y, 0.46), rust, rot=(0, 0, ang))
        box("rail_head", (L, 0.07, 0.05), (c.x, c.y, 0.545), steel, rot=(0, 0, ang))


def track_line(points):
    """Путь по ломаной: насыпь, шпалы, рельсы на каждом отрезке. Возвращает точки — по ним же ездят вагоны."""
    mats = (pbr("ballast", "gravel", rough=1.0, scale=0.5, box=True), pbr("sleeper", "wood", rough=0.9, scale=1.0, box=True),
            pbr("rail", color=(0.42, 0.40, 0.38), rough=0.35, metal=1.0), pbr("rail_rust", "rust", rough=0.8, scale=2.0, box=True))
    for a, b in zip(points, points[1:]):
        _seg_track(a, b, mats)
    return [Vector((x, y, 0)) for x, y in points]


def yard():
    """Сортировочная станция: главный путь, четыре параллельных пути с горловинами-лестницами с обеих сторон и съезд
    у состава (главный ↔ путь 1). Возвращает пути по именам (ломаные) и точки стрелок."""
    S = TRACK_SPACING
    T = {}
    T["main"] = track_line([(-260, 0), (260, 0)])
    # съезд у состава: с главного на путь 1 (уклон 1:4)
    T["cross"] = track_line([(45, 0), (45 + 4 * S, -S)])
    # лестницы горловин: диагонали с главного вниз до пути 4
    T["ladder_w"] = track_line([(-200, 0), (-200 + 4 * 4 * S, -4 * S)])
    T["ladder_e"] = track_line([(200, 0), (200 - 4 * 4 * S, -4 * S)])
    for k in range(1, 5):
        xw = -200 + 4 * k * S
        xe = 200 - 4 * k * S
        T[f"t{k}"] = track_line([(xw, -k * S), (xe, -k * S)])
    T["switches"] = [(45, 0)] + [(-200 + 4 * k * S, -k * S) for k in range(0, 5)] + [(200 - 4 * k * S, -k * S) for k in range(0, 5)]
    return T


def path(*pts):
    return [Vector((x, y, 0)) for x, y in pts]


def drive(obj, pts, t0, t1, fps=24):
    """Вагон едет по ломаной `pts` с t0 до t1 (разгон и торможение), ключ на каждый кадр: место и поворот по направлению пути."""
    seg = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:])]
    total = sum(L for *_, L in seg)
    f0, f1 = int(round(t0 * fps)) + 1, int(round(t1 * fps)) + 1
    z = obj.location.z
    back = (pts[-1] - pts[0]).x < 0  # едет назад: смотрит по-прежнему вперёд (вагон не разворачивается)
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0)
        u = u * u * (3 - 2 * u)  # плавно
        s = u * total
        for a, b, L in seg:
            if s <= L or (a, b, L) == seg[-1]:
                p = a + (b - a) * (min(s, L) / max(L, 1e-9))
                ang = math.atan2((b - a).y, (b - a).x) + (math.pi if back else 0)
                break
            s -= L
        obj.location = (p.x, p.y, z)
        obj.rotation_euler.z = ang
        obj.keyframe_insert("location", frame=f)
        obj.keyframe_insert("rotation_euler", index=2, frame=f)
        for fc in (obj.animation_data.action.fcurves if obj.animation_data and getattr(obj.animation_data.action, "fcurves", None) else []):
            for kp in fc.keyframe_points:
                if kp.co.x == f:
                    kp.interpolation = "LINEAR"


def collisions(wagons, t_end, fps=24, step=6):
    """Конечная проверка мира: вагоны на одном пути не пересекаются ни в один момент (каждые step кадров)."""
    sc = bpy.context.scene
    bad = []
    for f in range(1, int(t_end * fps) + 1, step):
        sc.frame_set(f)
        pos = [(w.name, w.matrix_world.translation.copy(), w["size"][0]) for w in wagons]
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                (n1, p1, l1), (n2, p2, l2) = pos[i], pos[j]
                if abs(p1.y - p2.y) < 2.5 and abs(p1.x - p2.x) < (l1 + l2) / 2 + 0.3:
                    bad.append(f"{f / fps:.1f} с: {n1} и {n2}")
    sc.frame_set(1)
    return bad


def person(loc, rot_z=0.0, height=1.8):
    """Диспетчер: модель человека, рост height м, стоит на земле."""
    before = set(bpy.data.objects)
    f = sorted((O3 / PERSON).rglob("*.3DS"))[0]
    bpy.ops.import_scene.max3ds(filepath=str(f))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new("dispatcher", None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    h = max(p.z for p in pts) - min(p.z for p in pts)
    if h < 0.5 * max(max(p.y for p in pts) - min(p.y for p in pts), 1e-6):  # лежит — поднять
        root.rotation_euler.x = math.pi / 2
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        h = max(p.z for p in pts) - min(p.z for p in pts)
    k = height / h
    root.scale = (k, k, k)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    root.location = Vector(loc) - Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2,
                                          (min(p.y for p in pts) + max(p.y for p in pts)) / 2, min(p.z for p in pts)))
    root.rotation_euler.z += rot_z
    return root


def scenery():
    """Окружение станции: депо, фонари вдоль путей, вышка, кусты травы-насыпи по краям."""
    brick = pbr("brick", "brick", rough=0.9, scale=0.6, box=True)
    roof = pbr("roof", "rust", rough=0.7, scale=0.5, box=True)
    box("depot", (60, 22, 9), (-20, 30, 4.5), brick)
    box("depot_roof", (62, 24, 0.6), (-20, 30, 9.3), roof, bevel=0.2)
    steel = pbr("pole", color=(0.25, 0.26, 0.28), rough=0.5, metal=0.8)
    lamp = pbr("lamp", color=(1, 0.9, 0.7), rough=0.3)
    for x in range(-180, 181, 45):
        box("pole", (0.25, 0.25, 12), (x, 6, 6), steel)
        box("lamp", (1.4, 0.5, 0.3), (x, 5.4, 12), lamp)
    tower2((70, 16, 0))


# ---------- природа: деревья и кусты Poly Haven (CC0) экземплярами коллекции — тяжёлая геометрия один раз в памяти ----------

def _gltf_collection(name):
    coll = bpy.data.collections.get(f"ph_{name}")
    if coll:
        return coll
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(PH / "models" / name / f"{name}.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    coll = bpy.data.collections.new(f"ph_{name}")
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll


def _card_mat(k):
    name = f"card_{k}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, nt = m.node_tree.nodes, m.node_tree
    b = n["Principled BSDF"]
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(PH / f"card_{k}.png"), check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.8
    try:
        m.surface_render_method = "DITHERED"
    except AttributeError:
        m.blend_method = "HASHED"
    return m


def tree_card(loc, height, k=0, rot=0.0):
    """Дерево-«карточка»: две плоскости крест-накрест со снимком настоящего дерева (bake_tree.py) — почти бесплатно в рендере."""
    objs = []
    for a in (0.0, math.pi / 2):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(loc[0], loc[1], height / 2), rotation=(math.pi / 2, 0, rot + a))
        o = bpy.context.object
        o.scale = (height, height, 1)
        o.data.materials.append(_card_mat(k))
        objs.append(o)
    return objs


def nature(seed=7, trees=220, shrubs=70):
    """Лесополоса вокруг станции (карточки деревьев) и кусты у насыпей (настоящие модели Poly Haven, лёгкие)."""
    import random
    rnd = random.Random(seed)
    for k in range(trees):
        north = k % 3 != 0
        x = rnd.uniform(-420, 420)
        y = rnd.uniform(55, 190) if north else -rnd.uniform(160, 300)  # юг — дальше: там камеры
        tree_card((x, y), rnd.uniform(11, 20), k=rnd.choice([0, 1]), rot=rnd.uniform(0, 3.14))
    for k in range(shrubs):
        sh = _gltf_collection(rnd.choice(["shrub_04", "shrub_02"]))
        e = bpy.data.objects.new(f"shrub{k}", None)
        e.instance_type, e.instance_collection = "COLLECTION", sh
        e.location = (rnd.uniform(-260, 260), rnd.choice([rnd.uniform(9, 30), -rnd.uniform(26, 34)]), 0)
        sc_ = rnd.uniform(1.0, 2.2)
        e.scale = (sc_, sc_, sc_)
        e.rotation_euler.z = rnd.uniform(0, 6.28)
        bpy.context.scene.collection.objects.link(e)


def tower2(loc=(70, 14, 0), rot=0.0):
    """Вышка диспетчера: кирпичный низ с окнами, остеклённая кабина с переплётами, вынос крыши, лестница с площадкой и перилами."""
    x, y, z = loc
    brick = pbr("brick", "brick", rough=0.9, scale=0.6, box=True)
    wood = pbr("tower_wood", "wood", rough=0.8, scale=0.8, box=True)
    frame = pbr("frame", color=(0.92, 0.92, 0.88), rough=0.5)
    glass = pbr("glass2", color=(0.55, 0.7, 0.78), rough=0.04, metal=0.2)
    glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.85
    warm = pbr("cabin_light", color=(1.0, 0.82, 0.55), rough=0.6)
    warm.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.8, 0.5, 1)
    warm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.5
    roof = pbr("roof2", "rust", rough=0.7, scale=0.5, box=True)
    steel = pbr("rail_steel", color=(0.18, 0.19, 0.2), rough=0.5, metal=0.8)
    parts = []
    W, D, H = 9.0, 6.5, 7.0
    parts.append(box("t_base", (W, D, H), (x, y, z + H / 2), brick))
    for k in range(3):  # окна низа
        parts.append(box("t_win", (1.3, 0.1, 1.8), (x - 3 + k * 3, y - D / 2 - 0.02, z + 3.8), glass))
        parts.append(box("t_sill", (1.6, 0.25, 0.15), (x - 3 + k * 3, y - D / 2 - 0.1, z + 2.85), frame))
    parts.append(box("t_floor", (W + 0.6, D + 0.6, 0.35), (x, y, z + H + 0.17), frame))
    ch = 3.0
    parts.append(box("t_room", (W - 0.4, D - 0.4, ch), (x, y, z + H + 0.35 + ch / 2), warm))  # тёплый свет внутри
    parts.append(box("t_glass", (W, D, ch * 0.75), (x, y, z + H + 0.35 + ch * 0.52), glass))
    parts.append(box("t_panel", (W + 0.02, D + 0.02, 0.9), (x, y, z + H + 0.35 + 0.45), wood))
    for i in range(7):  # переплёты окон
        parts.append(box("t_mull", (0.12, D + 0.06, ch * 0.75), (x - W / 2 + i * W / 6, y, z + H + 0.35 + ch * 0.52), frame))
    for i in range(5):
        parts.append(box("t_mull", (W + 0.06, 0.12, ch * 0.75), (x, y - D / 2 + i * D / 4, z + H + 0.35 + ch * 0.52), frame))
    top = z + H + 0.35 + ch
    parts.append(box("t_eave", (W + 2.4, D + 2.4, 0.3), (x, y, top + 0.15), roof, bevel=0.08))
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=(W + 2.4) * 0.72, depth=2.2, location=(x, y, top + 1.35), rotation=(0, 0, math.pi / 4))
    cone = bpy.context.object
    cone.scale = (1.0, (D + 2.4) / (W + 2.4), 1.0)
    cone.data.materials.append(roof)
    parts.append(cone)
    parts.append(box("t_chimney", (0.8, 0.8, 2.4), (x + 2.5, y + 1.2, top + 1.6), brick))
    for k in range(18):  # лестница
        parts.append(box("t_step", (1.2, 0.28, 0.06), (x + W / 2 + 0.8, y - D / 2 + 0.5 + k * 0.33, z + 0.4 * (k + 1)), steel))
    parts.append(box("t_land", (2.0, 2.2, 0.12), (x + W / 2 + 0.9, y + D / 2 - 0.4, z + H + 0.2), steel))
    for k in range(9):
        parts.append(box("t_rail", (0.05, 0.05, 1.0), (x + W / 2 + 1.5, y - D / 2 + 0.5 + k * 0.7, z + 0.4 * (k * 2 + 1) + 0.5), steel))
    parts.append(box("t_sign", (3.6, 0.15, 0.7), (x, y - D / 2 - 0.1, z + H - 0.8), frame))
    bpy.ops.object.text_add(location=(x, y - D / 2 - 0.2, z + H - 0.8), rotation=(math.pi / 2, 0, 0))
    t = bpy.context.object
    t.data.body = "ДИСПЕТЧЕРСКАЯ"
    t.data.font = font()
    t.data.size = 0.42
    t.data.align_x, t.data.align_y = "CENTER", "CENTER"
    t.data.materials.append(pbr("plate_num", color=(0.03, 0.03, 0.03), rough=0.4))
    parts.append(t)
    root = bpy.data.objects.new("tower", None)
    bpy.context.scene.collection.objects.link(root)
    root.location = (x, y, z)
    for o in parts:
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
    root.rotation_euler.z = rot
    return root


# ---------- вышка этажей: стеклянные площадки, на каждой — миниатюрные составы своего этажа ----------

def bfs_floors(n, gens):
    """Перебор: этаж каждой расстановки (без manimlib — для Blender)."""
    from collections import deque
    e = tuple(range(n))
    d, q = {e: 0}, deque([e])
    while q:
        s = q.popleft()
        for g in gens:
            t = tuple(s[i] for i in g)
            if t not in d:
                d[t] = d[s] + 1
                q.append(t)
    by = {}
    for s, f in d.items():
        by.setdefault(f, []).append(s)
    return {f: sorted(v) for f, v in by.items()}


def neighbours(n):
    out = []
    for i in range(n - 1):
        g = list(range(n))
        g[i], g[i + 1] = g[i + 1], g[i]
        out.append(tuple(g))
    return out


WAGON_COL = [(0.55, 0.12, 0.08), (0.08, 0.45, 0.55), (0.1, 0.2, 0.45), (0.35, 0.36, 0.34), (0.55, 0.42, 0.1), (0.25, 0.45, 0.2)]


def mini_train(perm, loc, car=0.9, gap=0.12, highlight=None):
    """Миниатюрный состав: кубики-вагоны своего цвета с номером на боку; highlight — цвет подсветки всего состава."""
    g = []
    n = len(perm)
    x0 = loc[0] - (n - 1) * (car + gap) / 2
    for k, v in enumerate(perm):
        col = highlight or WAGON_COL[v % len(WAGON_COL)]
        m = pbr(f"mini_{v}_{highlight}", color=col, rough=0.5)
        b = box(f"mini{v}", (car, car * 0.55, car * 0.6), (x0 + k * (car + gap), loc[1], loc[2] + car * 0.3 + 0.05), m, bevel=0.05)
        bpy.ops.object.text_add(location=(x0 + k * (car + gap), loc[1] - car * 0.28 - 0.01, loc[2] + car * 0.32), rotation=(math.pi / 2, 0, 0))
        t = bpy.context.object
        t.data.body, t.data.font, t.data.size = str(v + 1), font(), car * 0.42
        t.data.align_x, t.data.align_y = "CENTER", "CENTER"
        t.data.materials.append(pbr("mini_num", color=(0.97, 0.97, 0.95), rough=0.4))
        g += [b, t]
    return g


def floors_tower(by_floor, loc=(0, 0, 0), step=2.2, width=26.0, depth=6.0):
    """Вышка этажей: стеклянная площадка на каждый этаж, составы этажа в ряд. Возвращает {этаж: (площадка, обод, составы, номер)}."""
    glass = pbr("plate_glass", color=(0.75, 0.85, 0.95), rough=0.08)
    glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.7
    edge = {"0": pbr("edge_order", color=(0.24, 0.73, 0.31), rough=0.4), "top": pbr("edge_top", color=(0.97, 0.47, 0.73), rough=0.4),
            "mid": pbr("edge_mid", color=(0.35, 0.65, 1.0), rough=0.4)}
    top = max(by_floor)
    out = {}
    x, y, z = loc
    for f in sorted(by_floor):
        zz = z + f * step
        pl = box(f"floor{f}", (width, depth, 0.12), (x, y, zz), glass, bevel=0.03)
        rim = box(f"rim{f}", (width + 0.2, depth + 0.2, 0.06), (x, y, zz - 0.06), edge["0" if f == 0 else "top" if f == top else "mid"])
        trains = by_floor[f]
        span = width / max(1, len(trains))
        objs = []
        for k, p in enumerate(trains):
            car = min(0.9, span / (len(p) + 1.2) * 0.85)
            objs += mini_train(p, (x - width / 2 + span * (k + 0.5), y, zz + 0.06), car=car)
        bpy.ops.object.text_add(location=(x - width / 2 - 1.2, y - depth / 2, zz + 0.2), rotation=(math.pi / 2, 0, 0))
        t = bpy.context.object
        t.data.body, t.data.font, t.data.size = str(f), font(), 0.9
        t.data.materials.append(pbr("floor_num", color=(0.85, 0.88, 0.9), rough=0.5))
        out[f] = (pl, rim, objs, t)
    steel = pbr("pole", color=(0.25, 0.26, 0.28), rough=0.5, metal=0.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("post", (0.15, 0.15, top * step + 0.4), (x + sx * width / 2, y + sy * depth / 2, z + top * step / 2), steel)
    return out


def appear(objs, t, dur=0.6, fps=24):
    """Появление объектов к моменту t: масштаб 0 → 1 (ключи)."""
    f0, f1 = int(round(t * fps)) + 1, int(round((t + dur) * fps)) + 1
    for o in objs:
        s = o.scale.copy()
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=1)
        o.keyframe_insert("scale", frame=f0)
        o.scale = s
        o.keyframe_insert("scale", frame=f1)
