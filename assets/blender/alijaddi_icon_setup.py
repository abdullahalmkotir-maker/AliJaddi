"""
AliJaddi — مشهد أيقونة التطبيق (Blender 4.x) — إصدار موسّع
==========================================================
هوية: مربع مستدير، تدرج كحلي عميق → أزرق فولاذي، لمسة دفء في الزاوية،
ذهب لامع بملمس طبيعي خفيف، حلقات زجاجية، طبقة «طلاء» لامعة على القاعدة.

تشغيل:
  blender --background --python alijaddi_icon_setup.py
أو Scripting → Run Script

بعدها: استورد SVG لع+ج، طبّق MAT_Gold، أخفِ HINT_Text، ورندر.
"""
from __future__ import annotations

import math
import bpy
from mathutils import Euler


# True = أيقونة بخلفية شفافة (مناسب لمتاجر التطبيقات)
RENDER_TRANSPARENT = False


def _clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.curves:
        bpy.data.curves.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.collections:
        if block.name.startswith("ALI_"):
            bpy.data.collections.remove(block)


def _principled_set(bsdf, key: str, value) -> None:
    inp = bsdf.inputs.get(key)
    if inp is not None:
        inp.default_value = value


def _material_plate_premium(name: str):
    """قاعدة الأيقونة: تدرج عمودي + حبيبات دقيقة + طلاء لامع (Coat)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (520, 0)

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-600, 200)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-400, 200)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-180, 200)
    cr = ramp.color_ramp
    stops = list(cr.elements)
    if len(stops) >= 2:
        stops[0].position = 0.0
        stops[0].color = (0.018, 0.038, 0.095, 1.0)
        stops[1].position = 1.0
        stops[1].color = (0.11, 0.20, 0.42, 1.0)
    emid = cr.elements.new(0.45)
    emid.color = (0.05, 0.10, 0.24, 1.0)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, -120)
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.55

    mix_col = nt.nodes.new("ShaderNodeMixRGB")
    mix_col.location = (80, 120)
    mix_col.blend_type = "OVERLAY"
    mix_col.inputs["Fac"].default_value = 0.12

    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix_col.inputs["Color1"])
    nt.links.new(noise.outputs["Fac"], mix_col.inputs["Color2"])
    nt.links.new(mix_col.outputs["Color"], bsdf.inputs["Base Color"])

    _principled_set(bsdf, "Metallic", 0.22)
    _principled_set(bsdf, "Roughness", 0.24)
    _principled_set(bsdf, "Specular IOR Level", 0.55)
    if "Specular" in bsdf.inputs and "Specular IOR Level" not in bsdf.inputs:
        _principled_set(bsdf, "Specular", 0.55)

    _principled_set(bsdf, "Coat Weight", 0.42)
    _principled_set(bsdf, "Coat Roughness", 0.06)
    _principled_set(bsdf, "Coat IOR", 1.5)

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (200, -280)
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _material_gold_premium(name: str):
    """ذهب غني مع تباين لوني خفيف وSheen للإحساس الفاخر."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (820, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (480, 0)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-420, 80)
    noise.inputs["Scale"].default_value = 42.0
    noise.inputs["Detail"].default_value = 8.0

    tint_a = nt.nodes.new("ShaderNodeRGB")
    tint_a.location = (-200, 140)
    tint_a.outputs[0].default_value = (0.92, 0.72, 0.32, 1.0)
    tint_b = nt.nodes.new("ShaderNodeRGB")
    tint_b.location = (-200, -40)
    tint_b.outputs[0].default_value = (0.62, 0.42, 0.14, 1.0)

    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.location = (40, 60)
    mix.blend_type = "MIX"
    nt.links.new(noise.outputs["Fac"], mix.inputs["Fac"])
    nt.links.new(tint_a.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(tint_b.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    _principled_set(bsdf, "Metallic", 1.0)
    _principled_set(bsdf, "Roughness", 0.14)
    _principled_set(bsdf, "Specular IOR Level", 0.65)
    if "Specular" in bsdf.inputs and "Specular IOR Level" not in bsdf.inputs:
        _principled_set(bsdf, "Specular", 0.65)

    _principled_set(bsdf, "Sheen Weight", 0.22)
    _principled_set(bsdf, "Sheen Roughness", 0.38)
    _principled_set(bsdf, "Anisotropic", 0.25)
    _principled_set(bsdf, "Anisotropic Rotation", 0.15)

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _material_glass_rings(name: str):
    """حلقات زجاجية باردة مع لون يميل للسماوي."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (640, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)

    bsdf.inputs["Base Color"].default_value = (0.72, 0.88, 1.0, 1.0)
    _principled_set(bsdf, "Metallic", 0.0)
    _principled_set(bsdf, "Roughness", 0.045)
    _principled_set(bsdf, "IOR", 1.52)
    tw = bsdf.inputs.get("Transmission Weight")
    if tw is not None:
        tw.default_value = 0.94
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.94

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _rounded_icon_plate(name: str, size_xy: float = 1.85, thickness: float = 0.22, bevel_w: float = 0.32):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, -thickness * 0.5))
    plate = bpy.context.active_object
    plate.name = name
    plate.scale = (size_xy / 2.0, size_xy / 2.0, thickness / 2.0)
    bpy.ops.object.transform_apply(scale=True)
    bev = plate.modifiers.new(name="BevelPlate", type="BEVEL")
    bev.affect = "EDGES"
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(34)
    bev.width = bevel_w
    bev.segments = 12
    bev.profile = 0.52
    subs = plate.modifiers.new(name="Subsurf", type="SUBSURF")
    subs.levels = 1
    subs.render_levels = 2
    return plate


def _torus_ring(name: str, major: float, minor: float, z: float, mat, rot_z_deg: float = 0.0):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=128,
        minor_segments=18,
        location=(0, 0, z),
    )
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = Euler((math.radians(90), 0, math.radians(rot_z_deg)), "XYZ")
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    return ob


def _camera_icon_front():
    bpy.ops.object.camera_add(location=(0, -3.15, 0.32))
    cam = bpy.context.active_object
    cam.name = "CAM_IconFront"
    cam.rotation_euler = Euler((math.radians(83), 0, 0), "XYZ")
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.28
    cam.data.clip_start = 0.05
    cam.data.clip_end = 120
    bpy.context.scene.camera = cam
    return cam


def _camera_icon_hero():
    """زاوية ثلاثية أبعاد خفيفة لصور ترويجية."""
    bpy.ops.object.camera_add(location=(1.35, -2.55, 1.05))
    cam = bpy.context.active_object
    cam.name = "CAM_IconHero"
    cam.rotation_euler = Euler((math.radians(68), 0, math.radians(28)), "XYZ")
    cam.data.type = "PERSP"
    cam.data.lens = 50
    cam.data.clip_start = 0.05
    cam.data.clip_end = 120
    return cam


def _lights():
    bpy.ops.object.light_add(type="AREA", location=(-1.55, -1.05, 2.15))
    k = bpy.context.active_object
    k.name = "LIGHT_Key"
    k.data.energy = 920
    k.data.shape = "DISK"
    k.data.size = 1.15
    k.data.color = (1.0, 0.98, 1.0)

    bpy.ops.object.light_add(type="AREA", location=(1.95, -0.35, 0.95))
    f = bpy.context.active_object
    f.name = "LIGHT_Fill"
    f.data.energy = 280
    f.data.shape = "DISK"
    f.data.size = 1.6
    f.data.color = (0.75, 0.88, 1.0)

    bpy.ops.object.light_add(type="AREA", location=(0.85, -0.2, 0.15))
    w = bpy.context.active_object
    w.name = "LIGHT_WarmAccent"
    w.data.energy = 95
    w.data.shape = "DISK"
    w.data.size = 0.45
    w.data.color = (1.0, 0.72, 0.42)

    bpy.ops.object.light_add(type="AREA", location=(-0.2, 1.35, -0.15))
    r = bpy.context.active_object
    r.name = "LIGHT_RimCool"
    r.data.energy = 210
    r.data.shape = "DISK"
    r.data.size = 0.95
    r.data.color = (0.55, 0.75, 1.0)


def _world_gradient_navy():
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_AliJaddi")
        bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    tex = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (200, 0)
    cr = ramp.color_ramp
    cr.elements[0].color = (0.02, 0.04, 0.09, 1.0)
    cr.elements[1].color = (0.06, 0.11, 0.22, 1.0)

    bg = nt.nodes.new("ShaderNodeBackground")
    bg.location = (480, 0)
    bg.inputs["Strength"].default_value = 0.62
    out = nt.nodes.new("ShaderNodeOutputWorld")
    out.location = (720, 0)

    nt.links.new(tex.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def _setup_compositor_soft_glare():
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    for n in list(tree.nodes):
        tree.nodes.remove(n)

    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.location = (0, 0)

    glare = tree.nodes.new("CompositorNodeGlare")
    glare.location = (300, 0)
    glare.glare_type = "FOG_GLOW"
    glare.threshold = 0.76
    glare.mix = -0.2
    glare.size = 5

    comp = tree.nodes.new("CompositorNodeComposite")
    comp.location = (620, 0)
    vout = tree.nodes.new("CompositorNodeViewer")
    vout.location = (620, -200)

    tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
    tree.links.new(glare.outputs["Image"], vout.inputs["Image"])


def _collections_pack(objs: list, col_name: str):
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)
    for ob in objs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)


def _empty_marker(name: str, loc: tuple[float, float, float]):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc, radius=0.12)
    e = bpy.context.active_object
    e.name = name
    return e


def main():
    _clear_scene()

    scene = bpy.context.scene
    scene.name = "AliJaddi_Icon"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 320
    scene.cycles.use_denoising = True
    if hasattr(scene.cycles, "denoiser"):
        try:
            scene.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass

    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = RENDER_TRANSPARENT

    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Base Contrast"
    except Exception:
        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.15
    scene.view_settings.gamma = 1.0

    mat_plate = _material_plate_premium("MAT_IconBase")
    mat_gold = _material_gold_premium("MAT_Gold")
    mat_glass = _material_glass_rings("MAT_GlassRing")

    plate = _rounded_icon_plate("ALI_ICON_PLATE")
    if plate.data.materials:
        plate.data.materials[0] = mat_plate
    else:
        plate.data.materials.append(mat_plate)

    rings = [
        _torus_ring("DECO_RingOuter", 0.98, 0.026, 0.062, mat_glass, rot_z_deg=4),
        _torus_ring("DECO_RingMid", 0.74, 0.021, 0.052, mat_glass, rot_z_deg=-6),
        _torus_ring("DECO_RingInner", 0.53, 0.017, 0.044, mat_glass, rot_z_deg=8),
    ]

    marker = _empty_marker("IMPORT_SVG_ع_ج_HERE", (0, 0, 0.175))

    _camera_icon_front()
    _camera_icon_hero()
    _lights()
    _world_gradient_navy()
    _setup_compositor_soft_glare()

    all_geo = [plate, marker] + rings
    _collections_pack(all_geo, "ALI_Geometry")
    _collections_pack([o for o in bpy.data.objects if o.type == "LIGHT"], "ALI_Lighting")
    _collections_pack([o for o in bpy.data.objects if o.type == "CAMERA"], "ALI_Cameras")

    try:
        bpy.ops.object.text_add(location=(0, 0, 0.26))
        tx = bpy.context.active_object
        tx.name = "HINT_Text"
        tx.data.body = "استورد SVG لع+ج هنا"
        tx.data.size = 0.055
        tx.data.extrude = 0.012
        tx.data.align_x = "CENTER"
        tx.data.align_y = "CENTER"
        if tx.data.materials:
            tx.data.materials[0] = mat_gold
        else:
            tx.data.materials.append(mat_gold)
        tx.hide_render = True
        col = bpy.data.collections.get("ALI_Geometry")
        if col:
            for c in list(tx.users_collection):
                c.objects.unlink(tx)
            col.objects.link(tx)
    except Exception:
        pass

    print(
        "AliJaddi: Scene ready.\n"
        "  • MAT_IconBase = تدرج كحلي + طلاء (Coat) + حبيبات دقيقة\n"
        "  • MAT_Gold = ذهب غني + Sheen + Anisotropic خفيف\n"
        "  • LIGHT_WarmAccent = وهج ذهبي في الزاوية (كالمرجع)\n"
        "  • CAM_IconHero = لقطة ترويجية من زاوية | Compositor = Fog Glow خفيف\n"
        "  Import SVG → MAT_Gold → hide HINT_Text → Render."
    )


if __name__ == "__main__":
    main()
