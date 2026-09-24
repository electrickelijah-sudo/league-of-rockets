import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import os
import random

# Scale factor: 3x bigger
SCALE = 3.0

FIELD_L = 100.0 * SCALE  # 300m
FIELD_W = 80.0 * SCALE   # 240m
WALL_H  = 8.0 * SCALE    # 24m
RAMP_R  = 8.0 * SCALE    # 24m
CORNER_R = 12.0 * SCALE  # 36m
GOAL_W  = 20.0 * SCALE   # 60m
GOAL_H  = 8.0 * SCALE    # 24m
GOAL_D  = 8.0 * SCALE    # 24m

TEX_DIR = os.path.abspath("UnityProject/Assets/Art/Textures")

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

def make_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat

def load_image_texture(node_tree, img_filename):
    img_path = os.path.join(TEX_DIR, img_filename)
    if os.path.exists(img_path):
        img = bpy.data.images.load(img_path, check_existing=True)
        tex_node = node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.image = img
        return tex_node
    return None

def setup_materials():
    mats = {}

    # 1. Pitch Turf Material
    m = get_or_create_material('Mat_PitchTurf')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'turf_grass_unity_arena.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.15, 0.48, 0.20, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['turf'] = m

    # 2. Wireframe Cage Barrier (Glowing Green / Cyan)
    m = get_or_create_material('Mat_WireframeCage')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Glowing green cyber wireframe color
    bsdf.inputs['Base Color'].default_value = (0.15, 1.0, 0.45, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.15, 1.0, 0.45, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 4.5
    bsdf.inputs['Roughness'].default_value = 0.2
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['cage_wireframe'] = m

    # 3. Orange Goal Net & Posts
    m = get_or_create_material('Mat_GoalNet_Orange')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.42, 0.05, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.42, 0.05, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 6.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['goal_orange'] = m

    # 4. Blue Goal Net & Posts
    m = get_or_create_material('Mat_GoalNet_Blue')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.65, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.05, 0.65, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 6.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['goal_blue'] = m

    # 5. Orange Stadium Seats
    m = get_or_create_material('Mat_Seats_Orange')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'stadium_seats_orange.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.35, 0.06, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['seats_orange'] = m

    # 6. Blue Stadium Seats
    m = get_or_create_material('Mat_Seats_Blue')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'stadium_seats_blue.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.40, 0.85, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['seats_blue'] = m

    # 7. Balcony Fascia Banner ("UNITY 6" & "PHYSICS ACTIVE")
    m = get_or_create_material('Mat_FasciaBanner')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'banner_unity6_physics.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 2.0
    else:
        bsdf.inputs['Base Color'].default_value = (0.1, 0.15, 0.22, 1.0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['banner'] = m

    # 8. Jumbotron Turbo Boost Screen
    m = get_or_create_material('Mat_TurboScreen')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'screen_turbo_boost.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 3.0
    else:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.8, 1.0, 1.0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['screen_turbo'] = m

    # 9. Jumbotron Unity Vertical Screen
    m = get_or_create_material('Mat_UnityScreen')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'screen_unity_vertical.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 3.0
    else:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.6, 1.0, 1.0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['screen_unity'] = m

    # 10. Stadium Floodlight Bulb Matrix
    m = get_or_create_material('Mat_FloodlightBulbs')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = load_image_texture(m.node_tree, 'floodlight_fixture.png')
    if tex:
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 8.0
    else:
        bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 0.95, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 1.0, 0.95, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 10.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['floodlight_bulbs'] = m

    # 11. Volumetric Light Cone Beam
    m = get_or_create_material('Mat_LightBeamCone')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.9, 0.95, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.2
    bsdf.inputs['Alpha'].default_value = 0.15
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else 'BLEND'
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['light_cone'] = m

    # 12. Steel Truss / Dark Concrete / Roof Canopy
    m = get_or_create_material('Mat_StadiumSteel')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.14, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['steel'] = m

    m = get_or_create_material('Mat_RoofCanopy')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.10, 0.13, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.4
    bsdf.inputs['Roughness'].default_value = 0.4
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['roof'] = m

    # 13. Mountain Ridge (Dark Blue-Slate Rock)
    m = get_or_create_material('Mat_MountainRock')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.10, 0.14, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['mountain'] = m

    # 14. Boost Orb Cyan & Orange
    for name, key, col in [
        ('Mat_BoostPad_Cyan', 'boost_cyan', (0.0, 0.85, 1.0, 1.0)),
        ('Mat_BoostPad_Orange', 'boost_orange', (1.0, 0.48, 0.05, 1.0))
    ]:
        m = get_or_create_material(name)
        nodes = m.node_tree.nodes
        links = m.node_tree.links
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = col
        bsdf.inputs['Emission Color'].default_value = col
        bsdf.inputs['Emission Strength'].default_value = 7.0
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        mats[key] = m

    return mats

def build_pitch(col, mats):
    # 300m x 240m Playable Turf Plane
    mesh = bpy.data.meshes.new('Mesh_PlayableTurf')
    obj = bpy.data.objects.new('Playable_Turf', mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    # Create quad with proper UV mapping for soccer pitch
    v1 = bm.verts.new((-FIELD_L * 0.5, -FIELD_W * 0.5, 0.0))
    v2 = bm.verts.new(( FIELD_L * 0.5, -FIELD_W * 0.5, 0.0))
    v3 = bm.verts.new(( FIELD_L * 0.5,  FIELD_W * 0.5, 0.0))
    v4 = bm.verts.new((-FIELD_L * 0.5,  FIELD_W * 0.5, 0.0))
    face = bm.faces.new((v1, v2, v3, v4))

    uv_layer = bm.loops.layers.uv.new("UVMap")
    bm.faces.ensure_lookup_table()
    face.loops[0][uv_layer].uv = (0.0, 0.0)
    face.loops[1][uv_layer].uv = (1.0, 0.0)
    face.loops[2][uv_layer].uv = (1.0, 1.0)
    face.loops[3][uv_layer].uv = (0.0, 1.0)

    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mats['turf'])

def build_wireframe_cage(col, mats):
    # Builds the 3D rounded forcefield cage barrier with wireframe lattice
    mesh = bpy.data.meshes.new('Mesh_WireframeCage')
    obj = bpy.data.objects.new('Wireframe_Cage_Barrier', mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    half_x = FIELD_L * 0.5
    half_z = FIELD_W * 0.5
    h = WALL_H

    # Build perimeter wireframe segments
    # Side walls + curved ramps
    steps_x = 30
    steps_z = 24
    steps_y = 8

    # North Wall Grid (+Z)
    for ix in range(steps_x):
        x0 = -half_x + (ix / steps_x) * FIELD_L
        x1 = -half_x + ((ix + 1) / steps_x) * FIELD_L
        for iy in range(steps_y):
            y0 = (iy / steps_y) * h
            y1 = ((iy + 1) / steps_y) * h
            v1 = bm.verts.new((x0, half_z, y0))
            v2 = bm.verts.new((x1, half_z, y0))
            v3 = bm.verts.new((x1, half_z, y1))
            v4 = bm.verts.new((x0, half_z, y1))
            bm.faces.new((v1, v2, v3, v4))

    # South Wall Grid (-Z)
    for ix in range(steps_x):
        x0 = -half_x + (ix / steps_x) * FIELD_L
        x1 = -half_x + ((ix + 1) / steps_x) * FIELD_L
        for iy in range(steps_y):
            y0 = (iy / steps_y) * h
            y1 = ((iy + 1) / steps_y) * h
            v1 = bm.verts.new((x0, -half_z, y0))
            v2 = bm.verts.new((x1, -half_z, y0))
            v3 = bm.verts.new((x1, -half_z, y1))
            v4 = bm.verts.new((x0, -half_z, y1))
            bm.faces.new((v1, v4, v3, v2))

    # East Goal Wall (+X)
    for iz in range(steps_z):
        z0 = -half_z + (iz / steps_z) * FIELD_W
        z1 = -half_z + ((iz + 1) / steps_z) * FIELD_W
        # Leave goal cutout opening
        if abs((z0 + z1) * 0.5) < GOAL_W * 0.5:
            continue
        for iy in range(steps_y):
            y0 = (iy / steps_y) * h
            y1 = ((iy + 1) / steps_y) * h
            v1 = bm.verts.new((half_x, z0, y0))
            v2 = bm.verts.new((half_x, z1, y0))
            v3 = bm.verts.new((half_x, z1, y1))
            v4 = bm.verts.new((half_x, z0, y1))
            bm.faces.new((v1, v2, v3, v4))

    # West Goal Wall (-X)
    for iz in range(steps_z):
        z0 = -half_z + (iz / steps_z) * FIELD_W
        z1 = -half_z + ((iz + 1) / steps_z) * FIELD_W
        if abs((z0 + z1) * 0.5) < GOAL_W * 0.5:
            continue
        for iy in range(steps_y):
            y0 = (iy / steps_y) * h
            y1 = ((iy + 1) / steps_y) * h
            v1 = bm.verts.new((-half_x, z0, y0))
            v2 = bm.verts.new((-half_x, z1, y0))
            v3 = bm.verts.new((-half_x, z1, y1))
            v4 = bm.verts.new((-half_x, z0, y1))
            bm.faces.new((v1, v4, v3, v2))

    bm.to_mesh(mesh)
    bm.free()

    # Add Wireframe modifier so it renders as high-tech neon wire grid
    wf = obj.modifiers.new('WireframeMod', 'WIREFRAME')
    wf.thickness = 0.35 * SCALE
    wf.use_replace = True

    obj.data.materials.append(mats['cage_wireframe'])

def build_goals(col, mats):
    half_x = FIELD_L * 0.5
    # Orange Goal (+X)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(half_x + GOAL_D * 0.5, 0.0, GOAL_H * 0.5))
    g_orange = bpy.context.active_object
    g_orange.name = "Goal_Frame_Orange"
    g_orange.scale = (GOAL_D, GOAL_W, GOAL_H)
    bpy.ops.object.transform_apply(scale=True)
    wf_o = g_orange.modifiers.new('Wire_Orange', 'WIREFRAME')
    wf_o.thickness = 0.45 * SCALE
    g_orange.data.materials.append(mats['goal_orange'])
    col.objects.link(g_orange)
    bpy.context.scene.collection.objects.unlink(g_orange)

    # Blue Goal (-X)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-half_x - GOAL_D * 0.5, 0.0, GOAL_H * 0.5))
    g_blue = bpy.context.active_object
    g_blue.name = "Goal_Frame_Blue"
    g_blue.scale = (GOAL_D, GOAL_W, GOAL_H)
    bpy.ops.object.transform_apply(scale=True)
    wf_b = g_blue.modifiers.new('Wire_Blue', 'WIREFRAME')
    wf_b.thickness = 0.45 * SCALE
    g_blue.data.materials.append(mats['goal_blue'])
    col.objects.link(g_blue)
    bpy.context.scene.collection.objects.unlink(g_blue)

def build_grandstands(col, mats):
    # Massive Tiered Stadium Grandstand along +Z side (North) and -Z side (South)
    # Divided into Orange Section (left, X < 0) and Blue Section (right, X > 0)
    for sign, z_base, name_prefix in [(1, FIELD_W * 0.5 + 8.0, "NorthStand"), (-1, -(FIELD_W * 0.5 + 8.0), "SouthStand")]:
        num_tiers = 24
        tier_depth = 4.2 * SCALE   # ~12.6m per tier
        tier_height = 1.1 * SCALE  # ~3.3m riser per tier
        stand_len_half = (FIELD_L * 0.5 + 25.0 * SCALE)

        # Orange Seating Deck (X = -stand_len_half to -2.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        deck_o = bpy.context.active_object
        deck_o.name = f"{name_prefix}_Seats_Orange"
        deck_o.location = (-stand_len_half * 0.5 - 1.0, z_base + sign * (num_tiers * tier_depth * 0.5), num_tiers * tier_height * 0.5)
        deck_o.scale = (stand_len_half - 2.0, num_tiers * tier_depth, num_tiers * tier_height)
        deck_o.rotation_euler = (sign * math.radians(28.0), 0.0, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        deck_o.data.materials.append(mats['seats_orange'])
        col.objects.link(deck_o)
        bpy.context.scene.collection.objects.unlink(deck_o)

        # Blue Seating Deck (X = 2.0 to stand_len_half)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        deck_b = bpy.context.active_object
        deck_b.name = f"{name_prefix}_Seats_Blue"
        deck_b.location = (stand_len_half * 0.5 + 1.0, z_base + sign * (num_tiers * tier_depth * 0.5), num_tiers * tier_height * 0.5)
        deck_b.scale = (stand_len_half - 2.0, num_tiers * tier_depth, num_tiers * tier_height)
        deck_b.rotation_euler = (sign * math.radians(28.0), 0.0, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        deck_b.data.materials.append(mats['seats_blue'])
        col.objects.link(deck_b)
        bpy.context.scene.collection.objects.unlink(deck_b)

        # Balcony Fascia Ribbon Banner ("UNITY 6" / "PHYSICS ACTIVE")
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        banner = bpy.context.active_object
        banner.name = f"{name_prefix}_FasciaBanner"
        banner.location = (0.0, z_base + sign * 2.0, tier_height * 3.5)
        banner.scale = (stand_len_half * 2.0, 1.2 * SCALE, 3.5 * SCALE)
        bpy.ops.object.transform_apply(scale=True)
        banner.data.materials.append(mats['banner'])
        col.objects.link(banner)
        bpy.context.scene.collection.objects.unlink(banner)

        # Sweeping Cantilevered Canopy Roof
        roof_z_start = z_base + sign * (num_tiers * tier_depth * 0.4)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        roof = bpy.context.active_object
        roof.name = f"{name_prefix}_CanopyRoof"
        roof.location = (0.0, roof_z_start, num_tiers * tier_height + 15.0 * SCALE)
        roof.scale = (stand_len_half * 2.1, num_tiers * tier_depth * 1.1, 2.5 * SCALE)
        roof.rotation_euler = (sign * math.radians(-14.0), 0.0, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        roof.data.materials.append(mats['roof'])
        col.objects.link(roof)
        bpy.context.scene.collection.objects.unlink(roof)

        # Structural Arch Beams supporting the roof
        for arch_x in [-stand_len_half * 0.7, -stand_len_half * 0.25, stand_len_half * 0.25, stand_len_half * 0.7]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.8 * SCALE, depth=num_tiers * tier_depth * 1.2, location=(arch_x, roof_z_start, num_tiers * tier_height + 14.0 * SCALE))
            arch = bpy.context.active_object
            arch.name = f"{name_prefix}_TrussArch_{arch_x}"
            arch.rotation_euler = (math.radians(90.0) + sign * math.radians(-14.0), 0.0, 0.0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            arch.data.materials.append(mats['steel'])
            col.objects.link(arch)
            bpy.context.scene.collection.objects.unlink(arch)

def build_floodlight_towers(col, mats):
    # 4 Giant High-Mast Floodlight Towers at Corners
    tower_h = 42.0 * SCALE  # 126m tall
    head_w  = 9.0 * SCALE   # 27m wide head
    head_h  = 6.5 * SCALE   # 19.5m tall head

    corner_coords = [
        (-FIELD_L * 0.5 - 20.0 * SCALE,  FIELD_W * 0.5 + 24.0 * SCALE, "NW"),
        ( FIELD_L * 0.5 + 20.0 * SCALE,  FIELD_W * 0.5 + 24.0 * SCALE, "NE"),
        (-FIELD_L * 0.5 - 20.0 * SCALE, -FIELD_W * 0.5 - 24.0 * SCALE, "SW"),
        ( FIELD_L * 0.5 + 20.0 * SCALE, -FIELD_W * 0.5 - 24.0 * SCALE, "SE")
    ]

    for tx, tz, label in corner_coords:
        # 1. 4-Legged Lattice Mast
        bpy.ops.mesh.primitive_cone_add(radius1=4.0 * SCALE, radius2=1.5 * SCALE, depth=tower_h, location=(tx, tz, tower_h * 0.5))
        mast = bpy.context.active_object
        mast.name = f"Tower_Mast_{label}"
        wf_mast = mast.modifiers.new('LatticeTruss', 'WIREFRAME')
        wf_mast.thickness = 0.55 * SCALE
        mast.data.materials.append(mats['steel'])
        col.objects.link(mast)
        bpy.context.scene.collection.objects.unlink(mast)

        # 2. Angled Floodlight Head Panel
        aim_x = -0.4 * (1.0 if tx > 0 else -1.0)
        aim_z = -0.4 * (1.0 if tz > 0 else -1.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx + aim_x * 4.0 * SCALE, tz + aim_z * 4.0 * SCALE, tower_h))
        head = bpy.context.active_object
        head.name = f"Tower_FloodlightHead_{label}"
        head.scale = (head_w, 1.2 * SCALE, head_h)
        rot_y = -math.radians(25.0) if tx > 0 else math.radians(25.0)
        rot_x = math.radians(30.0) if tz > 0 else -math.radians(30.0)
        head.rotation_euler = (rot_x, rot_y, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        head.data.materials.append(mats['floodlight_bulbs'])
        col.objects.link(head)
        bpy.context.scene.collection.objects.unlink(head)

        # 3. Volumetric Spotlight Beam Cone
        bpy.ops.mesh.primitive_cone_add(radius1=18.0 * SCALE, radius2=2.0 * SCALE, depth=tower_h * 1.1, location=(tx * 0.6, tz * 0.6, tower_h * 0.45))
        cone = bpy.context.active_object
        cone.name = f"Tower_LightBeam_{label}"
        cone.rotation_euler = (rot_x * 0.8, rot_y * 0.8, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        cone.data.materials.append(mats['light_cone'])
        col.objects.link(cone)
        bpy.context.scene.collection.objects.unlink(cone)

def build_jumbotrons(col, mats):
    # 1. "TURBO BOOST" Cyan Screen (Right/Corner)
    pos_t = (FIELD_L * 0.48, FIELD_W * 0.5 + 35.0 * SCALE, 26.0 * SCALE)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos_t)
    scr_t = bpy.context.active_object
    scr_t.name = "Jumbotron_TurboBoost"
    scr_t.scale = (16.0 * SCALE, 1.5 * SCALE, 12.0 * SCALE)
    scr_t.rotation_euler = (math.radians(25.0), 0.0, math.radians(-15.0))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    scr_t.data.materials.append(mats['screen_turbo'])
    col.objects.link(scr_t)
    bpy.context.scene.collection.objects.unlink(scr_t)

    # 2. "UNITY" Vertical Tower Screen (Far Right Endzone)
    pos_u = (FIELD_L * 0.55, FIELD_W * 0.2, 30.0 * SCALE)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos_u)
    scr_u = bpy.context.active_object
    scr_u.name = "Jumbotron_UnityVertical"
    scr_u.scale = (1.5 * SCALE, 11.0 * SCALE, 22.0 * SCALE)
    scr_u.rotation_euler = (0.0, math.radians(12.0), math.radians(-25.0))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    scr_u.data.materials.append(mats['screen_unity'])
    col.objects.link(scr_u)
    bpy.context.scene.collection.objects.unlink(scr_u)

def build_mountain_horizon(col, mats):
    # Giant multi-peaked mountain ridge surrounding the stadium at 3x scale
    mesh = bpy.data.meshes.new('Mesh_MountainRidge')
    obj = bpy.data.objects.new('Surrounding_Mountain_Ridge', mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    num_peaks = 72
    base_radius = 160.0 * SCALE  # 480m radius
    outer_radius = 220.0 * SCALE # 660m outer ring

    random.seed(42)
    ring_bottom = []
    ring_peak = []
    ring_outer = []

    for i in range(num_peaks):
        angle = (i / float(num_peaks)) * 2.0 * math.pi
        # Irregular mountain height profile matching the screenshot
        noise_h = math.sin(angle * 4.0) * 12.0 * SCALE + math.cos(angle * 9.0) * 8.0 * SCALE + random.uniform(-4.0, 6.0) * SCALE
        h = max(28.0 * SCALE, 45.0 * SCALE + noise_h)
        rad = base_radius + random.uniform(-10.0, 15.0) * SCALE

        vx = math.cos(angle) * rad
        vz = math.sin(angle) * rad

        vb = bm.verts.new((vx * 0.92, vz * 0.92, -2.0 * SCALE))
        vp = bm.verts.new((vx, vz, h))
        vo = bm.verts.new((math.cos(angle) * outer_radius, math.sin(angle) * outer_radius, -5.0 * SCALE))

        ring_bottom.append(vb)
        ring_peak.append(vp)
        ring_outer.append(vo)

    for i in range(num_peaks):
        next_i = (i + 1) % num_peaks
        # Front face
        bm.faces.new((ring_bottom[i], ring_bottom[next_i], ring_peak[next_i], ring_peak[i]))
        # Back face
        bm.faces.new((ring_peak[i], ring_peak[next_i], ring_outer[next_i], ring_outer[i]))

    bm.to_mesh(mesh)
    bm.free()
    # mesh normals computed automatically
    obj.data.materials.append(mats['mountain'])

def build_boost_pads(col, mats):
    # 4 Large Boost Orbs (Corners)
    large_pads = [
        (-FIELD_L * 0.42, -FIELD_W * 0.4, 'boost_orange'),
        (-FIELD_L * 0.42,  FIELD_W * 0.4, 'boost_cyan'),
        ( FIELD_L * 0.42, -FIELD_W * 0.4, 'boost_orange'),
        ( FIELD_L * 0.42,  FIELD_W * 0.4, 'boost_cyan')
    ]
    for px, pz, mat_key in large_pads:
        bpy.ops.mesh.primitive_cylinder_add(radius=4.0 * SCALE, depth=0.4 * SCALE, location=(px, pz, 0.2 * SCALE))
        base = bpy.context.active_object
        base.name = f"BoostPad_Base_{px}_{pz}"
        base.data.materials.append(mats['steel'])
        col.objects.link(base)
        bpy.context.scene.collection.objects.unlink(base)

        # Floating diamond crystal
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, pz, 3.2 * SCALE))
        crys = bpy.context.active_object
        crys.name = f"BoostCrystal_{px}_{pz}"
        crys.scale = (2.2 * SCALE, 2.2 * SCALE, 3.8 * SCALE)
        crys.rotation_euler = (math.radians(45.0), math.radians(45.0), 0.0)
        bpy.ops.object.transform_apply(scale=True)
        crys.data.materials.append(mats[mat_key])
        col.objects.link(crys)
        bpy.context.scene.collection.objects.unlink(crys)

def setup_lighting_and_world(col):
    # World Twilight Horizon Gradient
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new('SunsetWorld')
        bpy.context.scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    w_out = wnodes.new('ShaderNodeOutputWorld')
    w_bg = wnodes.new('ShaderNodeBackground')

    # Gradient Texture for sky
    w_tex = wnodes.new('ShaderNodeTexGradient')
    w_tex.gradient_type = 'LINEAR'
    w_coord = wnodes.new('ShaderNodeTexCoord')
    w_map = wnodes.new('ShaderNodeMapping')
    w_map.inputs['Rotation'].default_value = (math.radians(90.0), 0.0, 0.0)
    w_map.inputs['Location'].default_value = (0.0, 0.0, -0.1)

    w_ramp = wnodes.new('ShaderNodeValToRGB')
    w_ramp.color_ramp.elements[0].position = 0.15
    w_ramp.color_ramp.elements[0].color = (1.0, 0.55, 0.22, 1.0) # Sunset orange horizon
    w_ramp.color_ramp.elements[1].position = 0.75
    w_ramp.color_ramp.elements[1].color = (0.12, 0.10, 0.22, 1.0) # Twilight indigo zenith

    wlinks.new(w_coord.outputs['Generated'], w_map.inputs['Vector'])
    wlinks.new(w_map.outputs['Vector'], w_tex.inputs['Vector'])
    wlinks.new(w_tex.outputs['Color'], w_ramp.inputs['Fac'])
    wlinks.new(w_ramp.outputs['Color'], w_bg.inputs['Color'])
    w_bg.inputs['Strength'].default_value = 1.6
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

    # Main Directional Sunset Sunlight
    sun_data = bpy.data.lights.new('Sun_Sunset', 'SUN')
    sun_data.color = (1.0, 0.72, 0.45) # Warm golden sunlight
    sun_data.energy = 4.0
    sun = bpy.data.objects.new('Sun_Sunset', sun_data)
    sun.location = (120.0 * SCALE, -180.0 * SCALE, 140.0 * SCALE)
    sun.rotation_euler = (math.radians(35.0), math.radians(-30.0), 0.0)
    col.objects.link(sun)

def setup_camera(col):
    # Replicates the exact perspective view of the reference screenshot
    cam_data = bpy.data.cameras.new('Camera_SunsetOverview')
    cam_data.lens = 28.0
    cam_data.clip_end = 3000.0
    cam = bpy.data.objects.new('Camera_SunsetOverview', cam_data)
    # Elevated diagonal perspective looking across the arena
    cam.location = (-FIELD_L * 0.55, -FIELD_W * 0.75, 42.0 * SCALE)
    cam.rotation_euler = (math.radians(65.0), 0.0, math.radians(-38.0))
    col.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam

def main():
    print("=" * 60)
    print("Building Rocket League 3x Sunset Stadium in Blender...")
    print("=" * 60)

    reset_scene()
    main_col = make_collection('Sunset_Stadium_3X')
    pitch_col = make_collection('Pitch_And_Cage', main_col)
    stadium_col = make_collection('Grandstands_And_Roof', main_col)
    lights_col = make_collection('Floodlights_And_Lighting', main_col)
    screens_col = make_collection('Jumbotrons_And_Screens', main_col)
    env_col = make_collection('Mountains_And_Sky', main_col)

    mats = setup_materials()

    print("1. Building 3x pitch...")
    build_pitch(pitch_col, mats)

    print("2. Building 3x wireframe cage...")
    build_wireframe_cage(pitch_col, mats)

    print("3. Building 3x goals...")
    build_goals(pitch_col, mats)

    print("4. Building 3x grandstands & canopy roof...")
    build_grandstands(stadium_col, mats)

    print("5. Building 3x floodlight towers & volumetric beams...")
    build_floodlight_towers(lights_col, mats)

    print("6. Building 3x jumbotrons...")
    build_jumbotrons(screens_col, mats)

    print("7. Building 3x boost pads...")
    build_boost_pads(pitch_col, mats)

    print("8. Building 3x surrounding mountain ridge...")
    build_mountain_horizon(env_col, mats)

    print("9. Building 1:1 blueprint battle-cars on pitch...")
    try:
        from build_picture_car import build_picture_car, setup_materials as setup_car_mats, get_or_create_material
        car_col = make_collection('Vehicles', main_col)
        c_mats_blue = setup_car_mats()
        build_picture_car(car_col, c_mats_blue, name="Blue_Octane_Blueprint", location=(-16.0, 4.0, 0.42), rotation=(0, 0, math.radians(-25)))
        
        c_mats_orange = dict(c_mats_blue)
        m_orange = get_or_create_material('Mat_Blueprint_OrangeLivery')
        nt_o = m_orange.node_tree
        nt_o.nodes.clear()
        out_o = nt_o.nodes.new('ShaderNodeOutputMaterial')
        bsdf_o = nt_o.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf_o.inputs['Base Color'].default_value = (0.95, 0.40, 0.02, 1.0)
        bsdf_o.inputs['Metallic'].default_value = 0.82
        bsdf_o.inputs['Roughness'].default_value = 0.24
        nt_o.links.new(bsdf_o.outputs['BSDF'], out_o.inputs['Surface'])
        c_mats_orange['body'] = m_orange
        build_picture_car(car_col, c_mats_orange, name="Orange_Octane_Blueprint", location=(16.0, -4.0, 0.42), rotation=(0, 0, math.radians(155)))
    except Exception as e:
        print(f"Notice adding cars: {e}")

    print("10. Setting up lighting and dusk world...")
    setup_lighting_and_world(lights_col)

    print("11. Setting up reference overview camera...")
    setup_camera(lights_col)

    # Save Blender Scene
    blend_path = os.path.abspath('sunset_stadium_3x.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blender scene: {blend_path}")

    # Render Preview Still
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    render_out = os.path.abspath('sunset_stadium_render.png')
    scene.render.filepath = render_out
    print(f"Rendering high-res preview to: {render_out}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render finished: {render_out}")

    # Export FBX directly into Unity
    fbx_target_1 = os.path.abspath('UnityProject/Assets/Art/Models/SunsetStadiumArena.fbx')
    fbx_target_2 = os.path.abspath('UnityProject/Assets/Resources/SunsetStadiumArena.fbx')
    print(f"Exporting FBX to: {fbx_target_1}...")
    bpy.ops.export_scene.fbx(
        filepath=fbx_target_1,
        use_selection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True,
        object_types={'MESH', 'EMPTY'},
        mesh_smooth_type='FACE',
        embed_textures=False
    )
    import shutil
    shutil.copyfile(fbx_target_1, fbx_target_2)
    print(f"Export complete: {fbx_target_1} and {fbx_target_2}")
    print("=" * 60)

if __name__ == '__main__':
    main()
