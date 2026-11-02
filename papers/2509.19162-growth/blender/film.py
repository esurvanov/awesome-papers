"""Общее для 3D-сцен фильма: время фраз по готовой озвучке, ключи камеры и объектов по фразам, рендер сразу в mp4.
Сцена задаётся скриптом shot_<КОД>.py: строит мир (station.py), ставит ключи через cam_at()/move_at() и вызывает finish().
Запуск: blender -b -P papers/2509.19162-growth/blender/shot_A01.py -- <выход.mp4> [--draft]"""
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ROOT = PAPER.parents[1]
FPS = 24
LEAD, TAIL = 0.4, 0.8  # тишина до и после речи — как в core/pipeline/build.py


def phrases(code, engine="realtime"):
    """Начала фраз сцены (с учётом тишины перед речью) и полная длина сцены, секунды."""
    out = subprocess.run([sys.executable if False else "uv", "run", "python", "-c",
                          "import sys, json; sys.path.insert(0, 'core/pipeline'); sys.path.insert(0, sys.argv[1]);"
                          "from timing import phrase_starts; import narration as N;"
                          "st, L = phrase_starts(sys.argv[2], N.TEXT[sys.argv[3]]); print(json.dumps([st, L]))",
                          str(PAPER), str(ROOT / "videos" / PAPER.name / "audio" / f"{code}.{engine}.wav"), code],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    import json
    st, length = json.loads(out.strip().splitlines()[-1])
    return [LEAD + t for t in st], LEAD + length + TAIL


def frame(t):
    return int(round(t * FPS)) + 1


def cam_at(cam, t, loc, look, lens=None, ease="BEZIER"):
    """Ключ камеры в момент t: где стоит и куда смотрит (через пустышку-цель)."""
    sc = bpy.context.scene
    tgt = cam.get("target_obj")
    if tgt is None:
        e = bpy.data.objects.new("cam_target", None)
        sc.collection.objects.link(e)
        con = cam.constraints.new("TRACK_TO")
        con.target, con.track_axis, con.up_axis = e, "TRACK_NEGATIVE_Z", "UP_Y"
        cam["target_obj"] = e.name
        tgt = e.name
    e = bpy.data.objects[tgt]
    cam.location = loc
    cam.keyframe_insert("location", frame=frame(t))
    e.location = look
    e.keyframe_insert("location", frame=frame(t))
    if lens:
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=frame(t))
    if cam.data.dof.use_dof:
        cam.data.dof.focus_distance = (Vector(look) - Vector(loc)).length
        cam.data.dof.keyframe_insert("focus_distance", frame=frame(t))


def move_at(obj, t, loc=None, rot_z=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame(t))
    if rot_z is not None:
        obj.rotation_euler.z = rot_z
        obj.keyframe_insert("rotation_euler", index=2, frame=frame(t))


def finish(out, length, draft=True):
    """Рендер всей сцены сразу в mp4 (без промежуточных картинок — диска мало)."""
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, frame(length)
    if draft:
        sc.render.resolution_x, sc.render.resolution_y = 960, 540
        try:
            sc.eevee.taa_render_samples = 12
            sc.eevee.use_raytracing = False  # черновик: отражения не считаем
            sc.eevee.shadow_resolution_scale = 0.5
        except AttributeError:
            pass
    for a in bpy.data.actions:  # плавные разгоны и торможения
        for fc in getattr(a, "fcurves", []):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "AUTO"
    if hasattr(sc.render.image_settings, "media_type"):  # Blender 5: сначала тип — видео, потом формат
        sc.render.image_settings.media_type = "VIDEO"
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath = str(out)
    bpy.ops.render.render(animation=True)
