"""
Rocket League Forbidden Temple Arena & Multi-Car Animated Aerial Showdown
Includes:
- Full Forbidden Temple Arena with hyper-neon forcefield cage, goals, stadium, and traditional architecture
- The Official Rocket League Ball with glowing cybernetic panel seams
- Blue Team Octane in freestyle aerial flight with fiery rocket boost & neon underglow
- Orange Team Dominus soaring up for an inverted goal-line aerial block with magma boost
- 120-frame keyframe animation across Ball, Octane, Dominus, Boost Orbs, and Cameras
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import os
import random

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 24

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

def setup_all_materials():
    mats = {}

    # 1. Pitch Turf (Rich emerald-slate turf with hexagonal weave)
    m = get_or_create_material('Mat_PitchTurf')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = nodes.new('ShaderNodeTexVoronoi')
    tex.voronoi_dimensions = '2D'
    tex.inputs['Scale'].default_value = 35.0
    c_ramp = nodes.new('ShaderNodeValToRGB')
    c_ramp.color_ramp.elements[0].position = 0.0
    c_ramp.color_ramp.elements[0].color = (0.05, 0.16, 0.13, 1.0)
    c_ramp.color_ramp.elements[1].position = 1.0
    c_ramp.color_ramp.elements[1].color = (0.08, 0.24, 0.18, 1.0)
    links.new(tex.outputs['Distance'], c_ramp.inputs['Fac'])
    links.new(c_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.32
    bsdf.inputs['Specular IOR Level'].default_value = 0.7
    bsdf.inputs['Coat Weight'].default_value = 0.4
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['turf'] = m

    # 2. Hyper-Neon Boundary & Cage Rails
    for name, key, col, em_str in [
        ('Mat_PitchLines_Blue', 'lines_blue', (0.15, 0.65, 1.0, 1.0), 8.0),
        ('Mat_PitchLines_Orange', 'lines_orange', (1.0, 0.42, 0.06, 1.0), 8.0),
        ('Mat_PitchLines_White', 'lines_white', (0.92, 0.96, 1.0, 1.0), 6.0),
        ('Mat_NeonRail_Blue', 'rail_blue', (0.05, 0.55, 1.0, 1.0), 14.0),
        ('Mat_NeonRail_Orange', 'rail_orange', (1.0, 0.32, 0.02, 1.0), 14.0),
        ('Mat_GoalNet_Blue', 'goal_net_blue', (0.1, 0.6, 1.0, 1.0), 5.0),
        ('Mat_GoalNet_Orange', 'goal_net_orange', (1.0, 0.35, 0.05, 1.0), 5.0),
    ]:
        m = get_or_create_material(name)
        nodes = m.node_tree.nodes
        links = m.node_tree.links
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = col
        bsdf.inputs['Emission Color'].default_value = col
        bsdf.inputs['Emission Strength'].default_value = em_str
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        mats[key] = m

    # 3. Holographic Forcefield Cage Glass (Hexagonal cybernetic grid)
    m = get_or_create_material('Mat_CageGlass')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    v_hex = nodes.new('ShaderNodeTexVoronoi')
    v_hex.feature = 'DISTANCE_TO_EDGE'
    v_hex.inputs['Scale'].default_value = 18.0
    c_hex = nodes.new('ShaderNodeValToRGB')
    c_hex.color_ramp.elements[0].position = 0.02
    c_hex.color_ramp.elements[0].color = (0.2, 0.7, 1.0, 1.0)
    c_hex.color_ramp.elements[1].position = 0.10
    c_hex.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    links.new(v_hex.outputs['Distance'], c_hex.inputs['Fac'])
    links.new(c_hex.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 3.5
    bsdf.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.92
    bsdf.inputs['Alpha'].default_value = 0.38
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['cage_glass'] = m

    # 4. Boost Materials
    m = get_or_create_material('Mat_BoostMetal')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.14, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.2
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['boost_metal'] = m

    m = get_or_create_material('Mat_BoostOrb')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.85, 0.2, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.75, 0.15, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 14.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['boost_orb'] = m

    # 5. Traditional Architecture Materials
    m = get_or_create_material('Mat_TempleRedWood')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.6, 0.09, 0.06, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Coat Weight'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['red_wood'] = m

    m = get_or_create_material('Mat_DarkTimber')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.14, 0.09, 0.07, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.65
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['dark_timber'] = m

    m = get_or_create_material('Mat_RoofTile')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.09, 0.11, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.32
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['roof_tile'] = m

    m = get_or_create_material('Mat_GoldTrim')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.75, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.2
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['gold'] = m

    m = get_or_create_material('Mat_LanternGlow')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.85, 0.5, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.68, 0.22, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 7.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['lantern_glow'] = m

    m = get_or_create_material('Mat_StoneWall')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.32, 0.30, 0.33, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['stone'] = m

    # 6. Stadium Crowd & Billboards
    m = get_or_create_material('Mat_GrandstandSeating')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = nodes.new('ShaderNodeTexVoronoi')
    tex.inputs['Scale'].default_value = 85.0
    col_ramp = nodes.new('ShaderNodeValToRGB')
    col_ramp.color_ramp.elements[0].position = 0.22
    col_ramp.color_ramp.elements[0].color = (0.12, 0.08, 0.10, 1.0)
    col_ramp.color_ramp.elements[1].position = 0.62
    col_ramp.color_ramp.elements[1].color = (1.0, 0.40, 0.12, 1.0)
    links.new(tex.outputs['Distance'], col_ramp.inputs['Fac'])
    links.new(col_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(col_ramp.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 4.0
    bsdf.inputs['Roughness'].default_value = 0.6
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['spectators'] = m

    m = get_or_create_material('Mat_RLShieldBoard')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.48, 0.15, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.5, 0.12, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 10.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['rl_board'] = m

    # 7. Environment Materials
    m = get_or_create_material('Mat_CherryBlossom')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.98, 0.44, 0.68, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Subsurface Weight'].default_value = 0.4
    bsdf.inputs['Emission Color'].default_value = (0.75, 0.2, 0.4, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.6
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['blossom'] = m

    m = get_or_create_material('Mat_TreeBark')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.08, 0.06, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['bark'] = m

    m = get_or_create_material('Mat_MountainRock')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.28, 0.23, 0.32, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['rock'] = m

    m = get_or_create_material('Mat_Water')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.06, 0.2, 0.24, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['Transmission Weight'].default_value = 0.88
    bsdf.inputs['IOR'].default_value = 1.333
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['water'] = m

    m = get_or_create_material('Mat_WaterFoam')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.96, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.75, 0.88, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 2.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['foam'] = m

    # 8. ROCKET LEAGUE OFFICIAL BALL MATERIALS
    m = get_or_create_material('Mat_RLBallBody')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0) # Dark metallic carbon
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Coat Weight'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['ball_body'] = m

    m = get_or_create_material('Mat_RLBallGlow')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.8, 0.95, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.4, 0.85, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 16.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['ball_glow'] = m

    # 9. BATTLE CAR MATERIALS
    # Blue Octane
    m = get_or_create_material('Mat_OctaneBlue')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.018, 0.42, 0.96, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.35
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['Coat Weight'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['car_paint_blue'] = m

    # Orange Dominus
    m = get_or_create_material('Mat_DominusOrange')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.35, 0.04, 1.0) # Magma orange
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Roughness'].default_value = 0.18
    bsdf.inputs['Coat Weight'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['car_paint_orange'] = m

    # Car Shared Trim, Glass, Wheels
    for name, key, col, r, met, coat in [
        ('Mat_CarTrim', 'car_trim', (0.08, 0.085, 0.095, 1.0), 0.55, 0.1, 0.0),
        ('Mat_CarGlass', 'car_glass', (0.08, 0.14, 0.22, 1.0), 0.06, 0.0, 0.0),
        ('Mat_CarChrome', 'car_chrome', (0.88, 0.9, 0.94, 1.0), 0.12, 0.95, 0.2),
        ('Mat_CarEngineRed', 'car_red', (0.9, 0.05, 0.04, 1.0), 0.22, 0.0, 0.6),
        ('Mat_CarTire', 'car_tire', (0.04, 0.045, 0.05, 1.0), 0.82, 0.0, 0.0),
        ('Mat_CarRim', 'car_rim', (0.18, 0.20, 0.23, 1.0), 0.25, 0.88, 0.2),
    ]:
        m = get_or_create_material(name)
        nodes = m.node_tree.nodes
        links = m.node_tree.links
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = col
        bsdf.inputs['Roughness'].default_value = r
        bsdf.inputs['Metallic'].default_value = met
        if coat > 0:
            bsdf.inputs['Coat Weight'].default_value = coat
        if key == 'car_glass':
            bsdf.inputs['Transmission Weight'].default_value = 0.85
            bsdf.inputs['Alpha'].default_value = 0.4
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        mats[key] = m

    # Headlights & Boost Flames
    m = get_or_create_material('Mat_OctaneHeadlight')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.95, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.82, 0.94, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 16.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['car_headlight'] = m

    m = get_or_create_material('Mat_BoostFlame')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.55, 0.08, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.48, 0.05, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 32.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['boost_flame'] = m

    m = get_or_create_material('Mat_BoostCore')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.95, 0.6, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.95, 0.7, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 55.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['boost_core'] = m

    # Car Neon Underglows
    m = get_or_create_material('Mat_Underglow_Blue')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.1, 0.6, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.1, 0.6, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 25.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['underglow_blue'] = m

    m = get_or_create_material('Mat_Underglow_Orange')
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.4, 0.05, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.4, 0.05, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 25.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['underglow_orange'] = m

    return mats

def build_pitch_and_cage(col, mats):
    half_w = 40.96
    half_l = 51.20
    corner_cut = 14.0
    cage_h = 20.48

    p = [
        (half_w - corner_cut, half_l),
        (half_w, half_l - corner_cut),
        (half_w, -(half_l - corner_cut)),
        (half_w - corner_cut, -half_l),
        (-(half_w - corner_cut), -half_l),
        (-half_w, -(half_l - corner_cut)),
        (-half_w, half_l - corner_cut),
        (-(half_w - corner_cut), half_l),
    ]

    # Pitch Floor
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, 0.0)) for x, y in p]
    bm.faces.new(verts)
    bm.normal_update()
    mesh = bpy.data.meshes.new('PitchFloorMesh')
    bm.to_mesh(mesh)
    bm.free()
    pitch_obj = bpy.data.objects.new('PitchFloor', mesh)
    pitch_obj.data.materials.append(mats['turf'])
    col.objects.link(pitch_obj)

    # Apron
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=66.0, depth=0.6, location=(0, 0, -0.3))
    apron = bpy.context.active_object
    apron.name = 'ArenaTerraceApron'
    apron.scale = (half_w / 40.0 * 1.16, half_l / 50.0 * 1.16, 1.0)
    apron.data.materials.append(mats['stone'])
    col.objects.link(apron)
    bpy.context.scene.collection.objects.unlink(apron)

    # Outer boundary lines
    n_pts = len(p)
    for i in range(n_pts):
        p1 = p[i]
        p2 = p[(i + 1) % n_pts]
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        slen = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mx, my, 0.03))
        bline = bpy.context.active_object
        bline.scale = (0.28, slen, 0.04)
        bline.rotation_euler = (0, 0, ang - math.pi/2)
        bline.data.materials.append(mats['lines_white'])
        col.objects.link(bline)
        bpy.context.scene.collection.objects.unlink(bline)

    # Center Circle & Badge
    bpy.ops.mesh.primitive_torus_add(major_radius=9.5, minor_radius=0.18, major_segments=64, minor_segments=8, location=(0, 0, 0.05))
    cc = bpy.context.active_object
    cc.data.materials.append(mats['lines_blue'])
    col.objects.link(cc)
    bpy.context.scene.collection.objects.unlink(cc)

    bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.08, location=(0, 0, 0.04))
    cs = bpy.context.active_object
    cs.data.materials.append(mats['boost_metal'])
    col.objects.link(cs)
    bpy.context.scene.collection.objects.unlink(cs)

    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.1, location=(0, 0, 0.06))
    cs_inner = bpy.context.active_object
    cs_inner.data.materials.append(mats['lines_white'])
    col.objects.link(cs_inner)
    bpy.context.scene.collection.objects.unlink(cs_inner)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.04))
    cl = bpy.context.active_object
    cl.scale = (half_w * 1.95, 0.35, 0.05)
    cl.data.materials.append(mats['lines_blue'])
    col.objects.link(cl)
    bpy.context.scene.collection.objects.unlink(cl)

    # Dual Concentric Loops
    for sign, mat_line in [(1.0, mats['lines_orange']), (-1.0, mats['lines_blue'])]:
        bpy.ops.mesh.primitive_torus_add(major_radius=19.0, minor_radius=0.14, major_segments=56, minor_segments=8, location=(0, sign * 26.0, 0.05))
        loop = bpy.context.active_object
        loop.scale = (1.35, 0.85, 1.0)
        loop.data.materials.append(mat_line)
        col.objects.link(loop)
        bpy.context.scene.collection.objects.unlink(loop)

        bpy.ops.mesh.primitive_torus_add(major_radius=12.0, minor_radius=0.14, major_segments=48, minor_segments=8, location=(0, sign * (half_l - 7.0), 0.05))
        garc = bpy.context.active_object
        garc.scale = (1.4, 0.7, 1.0)
        garc.data.materials.append(mat_line)
        col.objects.link(garc)
        bpy.context.scene.collection.objects.unlink(garc)

    # Animated 360-Degree Floating Boost Orbs
    full_boost_coords = [
        (35.0, 44.0), (-35.0, 44.0),
        (35.0, -44.0), (-35.0, -44.0),
        (35.0, 0.0), (-35.0, 0.0)
    ]
    for i, (bx, by) in enumerate(full_boost_coords):
        bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.18, location=(bx, by, 0.08))
        bring = bpy.context.active_object
        bring.data.materials.append(mats['boost_metal'])
        col.objects.link(bring)
        bpy.context.scene.collection.objects.unlink(bring)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(bx, by, 1.5))
        borb = bpy.context.active_object
        borb.name = f"AnimatedBoostOrb_{i}"
        borb.data.materials.append(mats['boost_orb'])
        # Animate continuous rotation
        borb.animation_data_create()
        borb.rotation_euler = (0, 0, 0)
        borb.keyframe_insert(data_path="rotation_euler", frame=1)
        borb.rotation_euler = (0, 0, math.radians(720))
        borb.keyframe_insert(data_path="rotation_euler", frame=120)
        col.objects.link(borb)
        bpy.context.scene.collection.objects.unlink(borb)

        light_data = bpy.data.lights.new(name=f"BoostLight_{i}", type='POINT')
        light_data.energy = 120.0
        light_data.color = (1.0, 0.75, 0.15)
        light_obj = bpy.data.objects.new(name=f"BoostLightObj_{i}", object_data=light_data)
        light_obj.location = (bx, by, 1.8)
        col.objects.link(light_obj)

    # Small Boost Pads
    mini_coords = [
        (0.0, 32.0), (0.0, -32.0),
        (12.0, 18.0), (-12.0, 18.0), (12.0, -18.0), (-12.0, -18.0),
        (22.0, 32.0), (-22.0, 32.0), (22.0, -32.0), (-22.0, -32.0),
        (0.0, 10.0), (0.0, -10.0),
        (16.0, 0.0), (-16.0, 0.0),
        (0.0, 48.0), (0.0, -48.0)
    ]
    for i, (mx, my) in enumerate(mini_coords):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.1, location=(mx, my, 0.06))
        mpad = bpy.context.active_object
        mpad.data.materials.append(mats['boost_orb'])
        col.objects.link(mpad)
        bpy.context.scene.collection.objects.unlink(mpad)

    # Goals with Pulsating Neon Energy Net
    goal_w = 17.85
    goal_h = 6.43
    goal_d = 8.80
    for sign, team_name, frame_mat, net_mat in [
        (1.0, "Orange", mats['red_wood'], mats['goal_net_orange']),
        (-1.0, "Blue", mats['dark_timber'], mats['goal_net_blue'])
    ]:
        goal_y = sign * half_l
        bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=goal_h, location=(-goal_w/2, goal_y, goal_h/2))
        lp = bpy.context.active_object
        lp.data.materials.append(frame_mat)
        col.objects.link(lp)
        bpy.context.scene.collection.objects.unlink(lp)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=goal_h, location=(goal_w/2, goal_y, goal_h/2))
        rp = bpy.context.active_object
        rp.data.materials.append(frame_mat)
        col.objects.link(rp)
        bpy.context.scene.collection.objects.unlink(rp)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, goal_y, goal_h))
        cb = bpy.context.active_object
        cb.scale = (goal_w + 2.4, 1.0, 0.8)
        cb.data.materials.append(frame_mat)
        col.objects.link(cb)
        bpy.context.scene.collection.objects.unlink(cb)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, goal_y, goal_h + 0.9))
        groof = bpy.context.active_object
        groof.scale = (goal_w + 3.6, 2.0, 0.4)
        groof.data.materials.append(mats['roof_tile'])
        col.objects.link(groof)
        bpy.context.scene.collection.objects.unlink(groof)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, goal_y + sign * (goal_d / 2), goal_h / 2))
        gnet = bpy.context.active_object
        gnet.scale = (goal_w, goal_d, goal_h)
        gnet.data.materials.append(net_mat)
        col.objects.link(gnet)
        bpy.context.scene.collection.objects.unlink(gnet)

    # Holographic Cybernetic Cage Mesh
    bm_cage = bmesh.new()
    cage_verts_bottom = [bm_cage.verts.new((x, y, 0.0)) for x, y in p]
    cage_verts_top = [bm_cage.verts.new((x, y, cage_h)) for x, y in p]
    for i in range(n_pts):
        v1 = cage_verts_bottom[i]
        v2 = cage_verts_bottom[(i + 1) % n_pts]
        v3 = cage_verts_top[(i + 1) % n_pts]
        v4 = cage_verts_top[i]
        bm_cage.faces.new([v1, v2, v3, v4])
    bm_cage.normal_update()

    cage_mesh = bpy.data.meshes.new('CageMesh')
    bm_cage.to_mesh(cage_mesh)
    bm_cage.free()
    cage_obj = bpy.data.objects.new('ArenaGlassCage', cage_mesh)
    cage_obj.data.materials.append(mats['cage_glass'])
    col.objects.link(cage_obj)

    # Neon Boundary Edge Rails
    for i in range(n_pts):
        p1 = p[i]
        p2 = p[(i + 1) % n_pts]
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        mat_rail = mats['rail_orange'] if mid_y > 0 else mats['rail_blue']

        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=seg_len, location=(mid_x, mid_y, 0.15))
        strip_b = bpy.context.active_object
        strip_b.rotation_euler = (math.pi/2, 0, angle - math.pi/2)
        strip_b.data.materials.append(mat_rail)
        col.objects.link(strip_b)
        bpy.context.scene.collection.objects.unlink(strip_b)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=seg_len, location=(mid_x, mid_y, cage_h))
        strip_t = bpy.context.active_object
        strip_t.rotation_euler = (math.pi/2, 0, angle - math.pi/2)
        strip_t.data.materials.append(mat_rail)
        col.objects.link(strip_t)
        bpy.context.scene.collection.objects.unlink(strip_t)

def build_stadium_and_walls(col, mats):
    sections = [
        (-46.0, 56.0, math.radians(-32), 36.0, 24.0, 7, 2.0),
        (-18.0, 68.0, math.radians(-10), 30.0, 22.0, 7, 3.5),
        (18.0, 68.0, math.radians(10), 30.0, 22.0, 7, 3.5),
        (46.0, 56.0, math.radians(32), 36.0, 24.0, 7, 2.0),
        (-52.0, 15.0, math.radians(-75), 45.0, 18.0, 5, 1.5),
        (52.0, 15.0, math.radians(75), 45.0, 18.0, 5, 1.5),
    ]

    for sec_idx, (sx, sy, srot, sw, sd, n_t, sbz) in enumerate(sections):
        for t in range(n_t):
            frac = t / n_t
            loc_y = frac * sd
            loc_z = sbz + frac * 12.0
            wx = sx - math.sin(srot) * loc_y
            wy = sy + math.cos(srot) * loc_y
            wz = loc_z

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, wy, wz))
            tier = bpy.context.active_object
            tier.name = f"StandTier_{sec_idx}_{t}"
            tier.scale = (sw, sd / n_t * 1.05, 1.8)
            tier.rotation_euler = (0, 0, srot)
            tier.data.materials.append(mats['spectators'])
            col.objects.link(tier)
            bpy.context.scene.collection.objects.unlink(tier)

    # Fortress Walls
    wall_segments = [
        (-48.0, 76.0, math.radians(-28), 42.0),
        (-16.0, 85.0, math.radians(-8), 34.0),
        (16.0, 85.0, math.radians(8), 34.0),
        (48.0, 76.0, math.radians(28), 42.0),
    ]
    for widx, (wx, wy, wrot, wlen) in enumerate(wall_segments):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, wy, 20.0))
        wall = bpy.context.active_object
        wall.scale = (wlen, 8.0, 14.0)
        wall.rotation_euler = (0, 0, wrot)
        wall.data.materials.append(mats['stone'])
        col.objects.link(wall)
        bpy.context.scene.collection.objects.unlink(wall)

        n_c = int(wlen / 4.5)
        for c in range(n_c):
            c_offset = (c - n_c/2 + 0.5) * 4.5
            cx = wx + math.cos(wrot) * c_offset
            cy = wy + math.sin(wrot) * c_offset
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 27.5))
            crenel = bpy.context.active_object
            crenel.scale = (2.4, 2.5, 2.0)
            crenel.rotation_euler = (0, 0, wrot)
            crenel.data.materials.append(mats['stone'])
            col.objects.link(crenel)
            bpy.context.scene.collection.objects.unlink(crenel)

        for m_offset in [-wlen*0.25, wlen*0.25]:
            mx = wx + math.cos(wrot) * m_offset - math.sin(wrot) * 4.1
            my = wy + math.sin(wrot) * m_offset + math.cos(wrot) * 4.1
            bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.4, location=(mx, my, 20.0))
            med = bpy.context.active_object
            med.rotation_euler = (math.pi/2, 0, wrot)
            med.data.materials.append(mats['gold'])
            col.objects.link(med)
            bpy.context.scene.collection.objects.unlink(med)

    # RL Holographic Billboards
    for bx, by, bz, rot_z in [(-30.0, 62.0, 10.5, math.radians(-18)), (30.0, 62.0, 10.5, math.radians(18))]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz))
        bframe = bpy.context.active_object
        bframe.scale = (17.0, 1.2, 9.5)
        bframe.rotation_euler = (math.radians(-24), 0, rot_z)
        bframe.data.materials.append(mats['boost_metal'])
        col.objects.link(bframe)
        bpy.context.scene.collection.objects.unlink(bframe)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by - 0.7, bz))
        bface = bpy.context.active_object
        bface.scale = (15.5, 0.4, 8.0)
        bface.rotation_euler = (math.radians(-24), 0, rot_z)
        bface.data.materials.append(mats['rl_board'])
        col.objects.link(bface)
        bpy.context.scene.collection.objects.unlink(bface)

        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.8, depth=0.4, location=(bx, by - 1.0, bz))
        emblem = bpy.context.active_object
        emblem.rotation_euler = (math.radians(-24) + math.pi/2, 0, rot_z)
        emblem.data.materials.append(mats['gold'])
        col.objects.link(emblem)
        bpy.context.scene.collection.objects.unlink(emblem)

        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=1.6, depth=0.5, location=(bx, by - 1.1, bz))
        emblem_core = bpy.context.active_object
        emblem_core.rotation_euler = (math.radians(-24) + math.pi/2, 0, rot_z)
        emblem_core.data.materials.append(mats['lines_white'])
        col.objects.link(emblem_core)
        bpy.context.scene.collection.objects.unlink(emblem_core)

    # Floodlights
    for lx, ly, rot_z in [(-38, 72, math.radians(-20)), (0, 80, 0), (38, 72, math.radians(20))]:
        light_data = bpy.data.lights.new(name=f"StadiumFlood_{lx}", type='SPOT')
        light_data.energy = 50000.0
        light_data.color = (1.0, 0.85, 0.72)
        light_data.spot_size = math.radians(70)
        light_data.spot_blend = 0.5
        light_obj = bpy.data.objects.new(name=f"StadiumFloodObj_{lx}", object_data=light_data)
        light_obj.location = (lx, ly, 30.0)
        light_obj.rotation_euler = (math.radians(-42), 0, math.radians(180) + rot_z)
        col.objects.link(light_obj)

def create_pagoda_tier(col, mats, tier_num, base_pos, width, height, is_top=False):
    bx, by, bz = base_pos
    post_inset = width * 0.42
    for px in [-post_inset, post_inset]:
        for py in [-post_inset, post_inset]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=height, location=(bx + px, by + py, bz + height/2))
            post = bpy.context.active_object
            post.data.materials.append(mats['red_wood'])
            col.objects.link(post)
            bpy.context.scene.collection.objects.unlink(post)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz + height/2))
    core = bpy.context.active_object
    core.scale = (width * 0.82, width * 0.82, height * 0.88)
    core.data.materials.append(mats['lantern_glow'])
    col.objects.link(core)
    bpy.context.scene.collection.objects.unlink(core)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz + 0.6))
    railing = bpy.context.active_object
    railing.scale = (width * 0.95, width * 0.95, 0.45)
    railing.data.materials.append(mats['dark_timber'])
    col.objects.link(railing)
    bpy.context.scene.collection.objects.unlink(railing)

    roof_z = bz + height
    roof_w = width * 1.55
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=roof_w, radius2=roof_w*0.35, depth=height*0.75, location=(bx, by, roof_z + height*0.35))
    roof = bpy.context.active_object
    roof.rotation_euler = (0, 0, math.pi/4)
    roof.data.materials.append(mats['roof_tile'])
    col.objects.link(roof)
    bpy.context.scene.collection.objects.unlink(roof)

    corner_dist = roof_w * 0.92
    for cx in [-corner_dist, corner_dist]:
        for cy in [-corner_dist, corner_dist]:
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1.2, radius2=0.1, depth=1.6, location=(bx + cx, by + cy, roof_z + 0.4))
            eave_tip = bpy.context.active_object
            eave_tip.rotation_euler = (math.radians(35 if cy > 0 else -35), math.radians(35 if cx > 0 else -35), 0)
            eave_tip.data.materials.append(mats['gold'])
            col.objects.link(eave_tip)
            bpy.context.scene.collection.objects.unlink(eave_tip)

            bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.85, location=(bx + cx*0.88, by + cy*0.88, roof_z - 0.45))
            lant = bpy.context.active_object
            lant.data.materials.append(mats['lantern_glow'])
            col.objects.link(lant)
            bpy.context.scene.collection.objects.unlink(lant)

    light_data = bpy.data.lights.new(name=f"PagodaLight_{tier_num}_{bx}", type='POINT')
    light_data.energy = 220.0
    light_data.color = (1.0, 0.72, 0.3)
    light_obj = bpy.data.objects.new(name=f"PagodaLightObj_{tier_num}_{bx}", object_data=light_data)
    light_obj.location = (bx, by, bz + height/2)
    col.objects.link(light_obj)

    if is_top:
        spire_z = roof_z + height * 0.75
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=7.0, location=(bx, by, spire_z + 3.5))
        spire = bpy.context.active_object
        spire.data.materials.append(mats['gold'])
        col.objects.link(spire)
        bpy.context.scene.collection.objects.unlink(spire)

        for r in range(5):
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0 - r*0.12, minor_radius=0.16, location=(bx, by, spire_z + 1.2 + r * 0.9))
            ring = bpy.context.active_object
            ring.data.materials.append(mats['gold'])
            col.objects.link(ring)
            bpy.context.scene.collection.objects.unlink(ring)

def build_pagodas_and_bridge(col, mats):
    pagoda_x = -24.0
    pagoda_y = 86.0
    current_z = 27.0
    base_w = 11.5
    tier_h = 3.8
    for t in range(5):
        w = base_w * (1.0 - t * 0.09)
        is_top = (t == 4)
        create_pagoda_tier(col, mats, t+1, (pagoda_x, pagoda_y, current_z), w, tier_h, is_top=is_top)
        current_z += tier_h + 1.9

    hall_x = 22.0
    hall_y = 88.0
    hall_z = 27.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hall_x, hall_y, hall_z + 1.5))
    hplinth = bpy.context.active_object
    hplinth.scale = (28.0, 20.0, 3.0)
    hplinth.data.materials.append(mats['stone'])
    col.objects.link(hplinth)
    bpy.context.scene.collection.objects.unlink(hplinth)

    current_z = hall_z + 3.0
    for t, (lw, lh, depth_scale) in enumerate([(24.0, 4.8, 16.0), (18.5, 4.2, 12.5), (14.0, 3.8, 9.5)]):
        for px in [-lw*0.42, 0, lw*0.42]:
            for py in [-depth_scale*0.42, depth_scale*0.42]:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=lh, location=(hall_x + px, hall_y + py, current_z + lh/2))
                hp = bpy.context.active_object
                hp.data.materials.append(mats['red_wood'])
                col.objects.link(hp)
                bpy.context.scene.collection.objects.unlink(hp)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hall_x, hall_y, current_z + lh/2))
        hcore = bpy.context.active_object
        hcore.scale = (lw * 0.82, depth_scale * 0.82, lh * 0.9)
        hcore.data.materials.append(mats['lantern_glow'])
        col.objects.link(hcore)
        bpy.context.scene.collection.objects.unlink(hcore)

        rf_z = current_z + lh
        rf_w = lw * 1.45
        rf_d = depth_scale * 1.45
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hall_x, hall_y, rf_z + 0.9))
        hroof = bpy.context.active_object
        hroof.scale = (rf_w, rf_d, 1.5)
        hroof.data.materials.append(mats['roof_tile'])
        col.objects.link(hroof)
        bpy.context.scene.collection.objects.unlink(hroof)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hall_x, hall_y, rf_z + 1.8))
        ridge = bpy.context.active_object
        ridge.scale = (rf_w * 0.82, 1.4, 0.7)
        ridge.data.materials.append(mats['gold'])
        col.objects.link(ridge)
        bpy.context.scene.collection.objects.unlink(ridge)

        for lx in [-rf_w*0.42, -rf_w*0.2, 0, rf_w*0.2, rf_w*0.42]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.8, location=(hall_x + lx, hall_y - rf_d*0.48, rf_z - 0.4))
            hlant = bpy.context.active_object
            hlant.data.materials.append(mats['lantern_glow'])
            col.objects.link(hlant)
            bpy.context.scene.collection.objects.unlink(hlant)

        if t == 2:
            for sx in [-rf_w * 0.38, rf_w * 0.38]:
                bpy.ops.mesh.primitive_cone_add(radius1=0.9, depth=2.0, location=(hall_x + sx, hall_y, rf_z + 2.5))
                shachi = bpy.context.active_object
                shachi.data.materials.append(mats['gold'])
                col.objects.link(shachi)
                bpy.context.scene.collection.objects.unlink(shachi)

        current_z += lh + 1.8

    # Moon Bridge
    bridge_len = 18.0
    bridge_w = 7.5
    bridge_h = 5.2
    bm_bridge = bmesh.new()
    steps = 18
    half_bw = bridge_w / 2.0
    verts_top = []
    verts_bot = []
    bridge_start_y = 54.0
    base_elev = 2.0
    for s in range(steps + 1):
        u = s / steps
        theta = u * math.pi
        by = bridge_start_y + u * bridge_len
        bz = base_elev + math.sin(theta) * bridge_h
        vt_l = bm_bridge.verts.new((-half_bw, by, bz))
        vt_r = bm_bridge.verts.new((half_bw, by, bz))
        vb_l = bm_bridge.verts.new((-half_bw, by, max(0.5, bz - 1.1)))
        vb_r = bm_bridge.verts.new((half_bw, by, max(0.5, bz - 1.1)))
        verts_top.append((vt_l, vt_r))
        verts_bot.append((vb_l, vb_r))

    for s in range(steps):
        tl1, tr1 = verts_top[s]
        tl2, tr2 = verts_top[s+1]
        bl1, br1 = verts_bot[s]
        bl2, br2 = verts_bot[s+1]
        bm_bridge.faces.new([tl1, tr1, tr2, tl2])
        bm_bridge.faces.new([tl1, tl2, bl2, bl1])
        bm_bridge.faces.new([tr1, br1, br2, tr2])
        bm_bridge.faces.new([bl1, bl2, br2, br1])

    bm_bridge.normal_update()
    bmesh_obj = bpy.data.meshes.new('MoonBridgeMesh')
    bm_bridge.to_mesh(bmesh_obj)
    bm_bridge.free()
    bridge_obj = bpy.data.objects.new('MoonBridge', bmesh_obj)
    bridge_obj.data.materials.append(mats['stone'])
    col.objects.link(bridge_obj)

    for sign_x in [-1, 1]:
        rx = sign_x * (half_bw - 0.25)
        for s in range(0, steps + 1, 2):
            u = s / steps
            theta = u * math.pi
            by = bridge_start_y + u * bridge_len
            bz = base_elev + math.sin(theta) * bridge_h
            bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.3, location=(rx, by, bz + 0.65))
            bpost = bpy.context.active_object
            bpost.data.materials.append(mats['red_wood'])
            col.objects.link(bpost)
            bpy.context.scene.collection.objects.unlink(bpost)

    # Torii Gate
    torii_x = 56.0
    torii_y = 18.0
    torii_w = 13.0
    torii_h = 11.0
    for tx in [-torii_w/2, torii_w/2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=torii_h, location=(torii_x + tx, torii_y, torii_h/2))
        tcol = bpy.context.active_object
        tcol.data.materials.append(mats['red_wood'])
        col.objects.link(tcol)
        bpy.context.scene.collection.objects.unlink(tcol)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(torii_x, torii_y, torii_h + 0.4))
    tlint = bpy.context.active_object
    tlint.scale = (torii_w * 1.45, 2.0, 0.9)
    tlint.data.materials.append(mats['red_wood'])
    col.objects.link(tlint)
    bpy.context.scene.collection.objects.unlink(tlint)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(torii_x, torii_y, torii_h + 1.3))
    troof = bpy.context.active_object
    troof.scale = (torii_w * 1.55, 3.2, 0.6)
    troof.data.materials.append(mats['roof_tile'])
    col.objects.link(troof)
    bpy.context.scene.collection.objects.unlink(troof)

    for bx in [-torii_w*0.32, torii_w*0.32]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(torii_x + bx, torii_y, torii_h - 2.8))
        banner = bpy.context.active_object
        banner.scale = (1.5, 0.1, 4.5)
        banner.data.materials.append(mats['lines_blue'] if bx < 0 else mats['lines_orange'])
        col.objects.link(banner)
        bpy.context.scene.collection.objects.unlink(banner)

    # Right Pavilion
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(62.0, 36.0, 6.0))
    rpav = bpy.context.active_object
    rpav.scale = (13.0, 11.0, 7.0)
    rpav.data.materials.append(mats['dark_timber'])
    col.objects.link(rpav)
    bpy.context.scene.collection.objects.unlink(rpav)

    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=12.0, depth=4.0, location=(62.0, 36.0, 11.5))
    rpav_rf = bpy.context.active_object
    rpav_rf.rotation_euler = (0, 0, math.pi/4)
    rpav_rf.data.materials.append(mats['roof_tile'])
    col.objects.link(rpav_rf)
    bpy.context.scene.collection.objects.unlink(rpav_rf)

    # Guardian Lions
    for sx, sy, srot in [(-52.0, 36.0, 0.4), (52.0, 36.0, -0.4), (-48.0, -8.0, 1.2)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, 2.5))
        splinth = bpy.context.active_object
        splinth.scale = (6.5, 6.5, 5.0)
        splinth.data.materials.append(mats['stone'])
        col.objects.link(splinth)
        bpy.context.scene.collection.objects.unlink(splinth)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=2.2, location=(sx, sy, 6.4))
        lion_body = bpy.context.active_object
        lion_body.scale = (1.0, 1.4, 1.1)
        lion_body.rotation_euler = (0, 0, srot)
        lion_body.data.materials.append(mats['stone'])
        col.objects.link(lion_body)
        bpy.context.scene.collection.objects.unlink(lion_body)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(sx, sy + 0.9, 8.2))
        lion_head = bpy.context.active_object
        lion_head.rotation_euler = (0, 0, srot)
        lion_head.data.materials.append(mats['stone'])
        col.objects.link(lion_head)
        bpy.context.scene.collection.objects.unlink(lion_head)

def create_cherry_tree(col, mats, pos, scale=1.0, rot=0.0):
    tx, ty, tz = pos
    bm_trunk = bmesh.new()
    h = 8.5 * scale
    rad = 0.8 * scale
    segments = 6
    trunk_verts = []
    for s in range(segments + 1):
        frac = s / segments
        curv_x = math.sin(frac * math.pi) * 1.4 * scale
        curv_y = math.cos(frac * math.pi * 0.5) * 0.9 * scale
        cz = frac * h
        r = rad * (1.15 - frac * 0.5)
        ring = []
        for a in range(8):
            ang = a * math.pi / 4
            vx = curv_x + math.cos(ang) * r
            vy = curv_y + math.sin(ang) * r
            ring.append(bm_trunk.verts.new((vx, vy, cz)))
        trunk_verts.append(ring)

    for s in range(segments):
        r1 = trunk_verts[s]
        r2 = trunk_verts[s+1]
        for a in range(8):
            a_next = (a + 1) % 8
            bm_trunk.faces.new([r1[a], r1[a_next], r2[a_next], r2[a]])

    bm_trunk.normal_update()
    tmesh = bpy.data.meshes.new('SakuraTrunkMesh')
    bm_trunk.to_mesh(tmesh)
    bm_trunk.free()
    tobj = bpy.data.objects.new('SakuraTrunk', tmesh)
    tobj.location = (tx, ty, tz)
    tobj.rotation_euler = (0, 0, rot)
    tobj.data.materials.append(mats['bark'])
    col.objects.link(tobj)

    for b_ang, b_h in [(0.5, 0.65), (2.3, 0.75), (4.2, 0.85)]:
        bx = math.cos(b_ang) * 2.8 * scale
        by = math.sin(b_ang) * 2.8 * scale
        bz = h * b_h
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35*scale, depth=4.0*scale, location=(tx + bx*0.5, ty + by*0.5, tz + bz))
        branch = bpy.context.active_object
        branch.rotation_euler = (math.radians(35), math.radians(20), b_ang)
        branch.data.materials.append(mats['bark'])
        col.objects.link(branch)
        bpy.context.scene.collection.objects.unlink(branch)

    blossom_offsets = [
        (0.0, 0.5, h * 1.05, 4.2),
        (-2.4 * scale, 1.4 * scale, h * 0.95, 3.6),
        (2.6 * scale, -1.2 * scale, h * 0.9, 3.4),
        (1.4 * scale, 2.8 * scale, h * 0.85, 3.2),
        (-1.6 * scale, -2.2 * scale, h * 0.8, 3.0),
        (0.0, -1.0 * scale, h * 1.25, 2.8),
    ]
    for ox, oy, oz, brad in blossom_offsets:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=brad * scale, location=(tx + ox, ty + oy, tz + oz))
        bcloud = bpy.context.active_object
        bcloud.scale = (1.15, 1.2, 0.78)
        bcloud.data.materials.append(mats['blossom'])
        col.objects.link(bcloud)
        bpy.context.scene.collection.objects.unlink(bcloud)

def build_environment(col, mats):
    random.seed(42)
    mountain_coords = [
        (-80.0, 160.0, 180.0, 36.0),
        (-30.0, 185.0, 210.0, 42.0),
        (35.0, 175.0, 195.0, 38.0),
        (90.0, 150.0, 170.0, 34.0),
        (0.0, 220.0, 240.0, 46.0),
        (-105.0, 105.0, 130.0, 30.0),
        (-95.0, 45.0, 115.0, 28.0),
        (-90.0, -20.0, 100.0, 25.0),
        (100.0, 90.0, 125.0, 28.0),
        (95.0, 30.0, 110.0, 26.0),
        (90.0, -30.0, 95.0, 24.0),
    ]
    for i, (mx, my, mh, mrad) in enumerate(mountain_coords):
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=mrad, radius2=mrad*0.25, depth=mh, location=(mx, my, mh/2 - 10.0))
        peak = bpy.context.active_object
        peak.name = f"KarstPeak_{i}"
        peak.scale = (1.0 + random.uniform(-0.12, 0.12), 1.0 + random.uniform(-0.12, 0.12), 1.0)
        peak.data.materials.append(mats['rock'])
        col.objects.link(peak)
        bpy.context.scene.collection.objects.unlink(peak)

    for i in range(14):
        rx = -58.0 + random.uniform(-6.0, 3.0)
        ry = -30.0 + i * 7.5
        rz = 10.0 + random.uniform(-3.0, 8.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, ry, rz))
        boulder = bpy.context.active_object
        boulder.scale = (random.uniform(10.0, 16.0), random.uniform(9.0, 13.0), random.uniform(10.0, 18.0))
        boulder.rotation_euler = (random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25), random.uniform(0, 3.14))
        boulder.data.materials.append(mats['rock'])
        col.objects.link(boulder)
        bpy.context.scene.collection.objects.unlink(boulder)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-54.5, 12.0, 12.0))
    wf = bpy.context.active_object
    wf.name = 'WaterfallMesh'
    wf.scale = (0.7, 7.0, 22.0)
    wf.rotation_euler = (math.radians(-16), 0, 0)
    wf.data.materials.append(mats['water'])
    col.objects.link(wf)
    bpy.context.scene.collection.objects.unlink(wf)

    for f_z in [1.5, 7.0, 13.0, 19.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-54.0, 12.0 - (22.0 - f_z)*0.18, f_z))
        wfoam = bpy.context.active_object
        wfoam.scale = (2.2, 7.5, 1.0)
        wfoam.data.materials.append(mats['foam'])
        col.objects.link(wfoam)
        bpy.context.scene.collection.objects.unlink(wfoam)

    bpy.ops.mesh.primitive_cylinder_add(radius=15.0, depth=0.4, location=(-52.0, 8.0, 0.1))
    pond = bpy.context.active_object
    pond.name = 'GardenPond'
    pond.scale = (1.3, 2.2, 1.0)
    pond.data.materials.append(mats['water'])
    col.objects.link(pond)
    bpy.context.scene.collection.objects.unlink(pond)

    sakura_locations = [
        ((-49.0, 4.0, 1.5), 1.35, 0.5),
        ((-53.0, 34.0, 4.0), 1.5, 1.2),
        ((-60.0, 60.0, 14.0), 1.65, 2.1),
        ((-32.0, 78.0, 16.0), 1.4, 0.8),
        ((34.0, 78.0, 16.0), 1.45, 1.4),
        ((46.0, 64.0, 15.0), 1.55, 1.7),
        ((56.0, 26.0, 2.0), 1.5, 3.0),
        ((54.0, -10.0, 1.2), 1.35, 2.4),
        ((-40.0, -36.0, 1.2), 1.3, 0.3),
        ((38.0, -36.0, 1.2), 1.3, 1.1),
    ]
    for pos, sc, rot in sakura_locations:
        create_cherry_tree(col, mats, pos, scale=sc, rot=rot)

    lantern_coords = [
        (-44.0, 22.0, 0.6), (-44.0, -22.0, 0.6),
        (44.0, 22.0, 0.6), (44.0, -22.0, 0.6),
        (-26.0, 52.0, 1.2), (26.0, 52.0, 1.2),
        (0.0, 74.0, 3.5),
    ]
    for lx, ly, lz in lantern_coords:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.8, location=(lx, ly, lz + 0.9))
        lpillar = bpy.context.active_object
        lpillar.data.materials.append(mats['stone'])
        col.objects.link(lpillar)
        bpy.context.scene.collection.objects.unlink(lpillar)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, lz + 2.0))
        lbox = bpy.context.active_object
        lbox.scale = (0.75, 0.75, 0.65)
        lbox.data.materials.append(mats['lantern_glow'])
        col.objects.link(lbox)
        bpy.context.scene.collection.objects.unlink(lbox)

        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.0, depth=0.45, location=(lx, ly, lz + 2.5))
        lcap = bpy.context.active_object
        lcap.rotation_euler = (0, 0, math.pi/4)
        lcap.data.materials.append(mats['stone'])
        col.objects.link(lcap)
        bpy.context.scene.collection.objects.unlink(lcap)

        pt_data = bpy.data.lights.new(name=f"ToroLight_{lx}_{ly}", type='POINT')
        pt_data.energy = 60.0
        pt_data.color = (1.0, 0.75, 0.35)
        pt_obj = bpy.data.objects.new(name=f"ToroLightObj_{lx}_{ly}", object_data=pt_data)
        pt_obj.location = (lx, ly, lz + 2.0)
        col.objects.link(pt_obj)

def setup_world_and_lighting(col):
    scene = bpy.context.scene
    world = bpy.data.worlds.new('ForbiddenTempleWorld')
    scene.world = world

    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputWorld')
    bg = nodes.new('ShaderNodeBackground')

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = 'LINEAR'
    col_ramp = nodes.new('ShaderNodeValToRGB')

    col_ramp.color_ramp.elements[0].position = 0.0
    col_ramp.color_ramp.elements[0].color = (0.45, 0.18, 0.36, 1.0)
    col_ramp.color_ramp.elements[1].position = 0.5
    col_ramp.color_ramp.elements[1].color = (0.28, 0.14, 0.44, 1.0)
    
    e3 = col_ramp.color_ramp.elements.new(0.92)
    e3.color = (0.08, 0.06, 0.22, 1.0)

    mapping.inputs['Rotation'].default_value = (math.pi/2, 0, 0)
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], col_ramp.inputs['Fac'])
    links.new(col_ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.6
    links.new(bg.outputs['Background'], out.inputs['Surface'])

    # Warm Dusk Sun
    sun_data = bpy.data.lights.new(name='TwilightSun', type='SUN')
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.7, 0.78)
    sun_obj = bpy.data.objects.new(name='TwilightSunObj', object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(110), math.radians(-25), math.radians(60))
    col.objects.link(sun_obj)

    # Ambient Fill
    fill_data = bpy.data.lights.new(name='AmbientFill', type='SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.55, 0.58, 0.95)
    fill_obj = bpy.data.objects.new(name='AmbientFillObj', object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-120))
    col.objects.link(fill_obj)

    # Arena Downlight Fill
    arena_light = bpy.data.lights.new(name='ArenaSoftLight', type='POINT')
    arena_light.energy = 10000.0
    arena_light.color = (0.75, 0.85, 1.0)
    arena_light.shadow_soft_size = 8.0
    arena_light_obj = bpy.data.objects.new(name='ArenaSoftLightObj', object_data=arena_light)
    arena_light_obj.location = (0.0, 0.0, 36.0)
    col.objects.link(arena_light_obj)


# ==============================================================================
# OFFICIAL ROCKET LEAGUE BALL
# ==============================================================================

def build_rocket_league_ball(col, mats, radius=2.0):
    """Constructs the official Rocket League ball with glowing cybernetic seams."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    ball_root = bpy.context.active_object
    ball_root.name = "RL_Ball_Root"
    col.objects.link(ball_root)
    bpy.context.scene.collection.objects.unlink(ball_root)

    # Main carbon sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=(0, 0, 0))
    ball_body = bpy.context.active_object
    ball_body.name = "RL_Ball_Body"
    ball_body.data.materials.append(mats['ball_body'])
    ball_body.parent = ball_root
    col.objects.link(ball_body)
    bpy.context.scene.collection.objects.unlink(ball_body)

    # Glowing Seam Rings (Latitude & Longitude energy rings)
    for r_axis, r_angle in [
        ((0, 0, 0), 0),
        ((math.pi/2, 0, 0), math.pi/2),
        ((0, math.pi/2, 0), math.pi/2),
        ((math.pi/4, math.pi/4, 0), math.pi/4),
        ((-math.pi/4, math.pi/4, 0), -math.pi/4),
    ]:
        bpy.ops.mesh.primitive_torus_add(major_radius=radius * 1.01, minor_radius=0.045, major_segments=48, minor_segments=6)
        ring = bpy.context.active_object
        ring.rotation_euler = r_axis
        ring.data.materials.append(mats['ball_glow'])
        ring.parent = ball_root
        col.objects.link(ring)
        bpy.context.scene.collection.objects.unlink(ring)

    # Pentagonal Core Shields (6 around the ball)
    core_dirs = [
        (0, 0, radius * 1.01), (0, 0, -radius * 1.01),
        (radius * 1.01, 0, 0), (-radius * 1.01, 0, 0),
        (0, radius * 1.01, 0), (0, -radius * 1.01, 0)
    ]
    for cx, cy, cz in core_dirs:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.55, depth=0.06, location=(cx, cy, cz))
        core = bpy.context.active_object
        if abs(cx) > 0:
            core.rotation_euler = (0, math.pi/2, 0)
        elif abs(cy) > 0:
            core.rotation_euler = (math.pi/2, 0, 0)
        core.data.materials.append(mats['ball_glow'])
        core.parent = ball_root
        col.objects.link(core)
        bpy.context.scene.collection.objects.unlink(core)

    # Ball glow light
    blight_data = bpy.data.lights.new(name="BallGlowLight", type='POINT')
    blight_data.energy = 800.0
    blight_data.color = (0.5, 0.88, 1.0)
    blight_obj = bpy.data.objects.new(name="BallGlowLightObj", object_data=blight_data)
    blight_obj.parent = ball_root
    col.objects.link(blight_obj)

    return ball_root


# ==============================================================================
# CAR BUILDERS: OCTANE (BLUE) & DOMINUS (ORANGE)
# ==============================================================================

def create_wheel(col, mats, parent, name_prefix, loc, radius=0.48, width=0.42):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=width, location=loc)
    tire = bpy.context.active_object
    tire.name = f"{name_prefix}_Tire"
    tire.rotation_euler = (0, math.pi/2, 0)
    tire.data.materials.append(mats['car_tire'])
    tire.parent = parent
    col.objects.link(tire)
    bpy.context.scene.collection.objects.unlink(tire)

    rim_r = radius * 0.65
    bpy.ops.mesh.primitive_cylinder_add(radius=rim_r, depth=width * 0.95, location=loc)
    rim = bpy.context.active_object
    rim.rotation_euler = (0, math.pi/2, 0)
    rim.data.materials.append(mats['car_rim'])
    rim.parent = parent
    col.objects.link(rim)
    bpy.context.scene.collection.objects.unlink(rim)

    for sp in range(5):
        sp_ang = sp * (2 * math.pi / 5)
        sp_y = loc[1] + math.sin(sp_ang) * (rim_r * 0.45)
        sp_z = loc[2] + math.cos(sp_ang) * (rim_r * 0.45)
        outer_sign = 1.0 if loc[0] > 0 else -1.0
        sp_x = loc[0] + outer_sign * (width * 0.42)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sp_x, sp_y, sp_z))
        spoke = bpy.context.active_object
        spoke.scale = (0.05, 0.08, rim_r * 0.8)
        spoke.rotation_euler = (sp_ang, 0, 0)
        spoke.data.materials.append(mats['car_chrome'])
        spoke.parent = parent
        col.objects.link(spoke)
        bpy.context.scene.collection.objects.unlink(spoke)

    # Strut & Red Coil
    inner_x = loc[0] - (1.0 if loc[0] > 0 else -1.0) * (width * 0.35)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.55, location=(inner_x, loc[1], loc[2] + 0.2))
    strut = bpy.context.active_object
    strut.rotation_euler = (0, (0.35 if loc[0] > 0 else -0.35), 0)
    strut.data.materials.append(mats['car_chrome'])
    strut.parent = parent
    col.objects.link(strut)
    bpy.context.scene.collection.objects.unlink(strut)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.35, location=(inner_x, loc[1], loc[2] + 0.18))
    coil = bpy.context.active_object
    coil.rotation_euler = (0, (0.35 if loc[0] > 0 else -0.35), 0)
    coil.data.materials.append(mats['car_red'])
    coil.parent = parent
    col.objects.link(coil)
    bpy.context.scene.collection.objects.unlink(coil)

def build_octane(col, mats, name="Octane_Blue", paint_mat=None, underglow_mat=None):
    """Builds the complete Blue Team Octane battle-car."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = name
    col.objects.link(root)
    bpy.context.scene.collection.objects.unlink(root)

    paint = paint_mat or mats['car_paint_blue']
    underglow = underglow_mat or mats['underglow_blue']

    # 1. Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 0.42))
    chassis = bpy.context.active_object
    chassis.scale = (1.5, 3.2, 0.35)
    chassis.data.materials.append(mats['car_trim'])
    chassis.parent = root
    col.objects.link(chassis)
    bpy.context.scene.collection.objects.unlink(chassis)

    # 2. Sloped Hood
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.95, 0.72))
    hood = bpy.context.active_object
    hood.scale = (1.35, 1.45, 0.45)
    hood.rotation_euler = (math.radians(-14), 0, 0)
    hood.data.materials.append(paint)
    hood.parent = root
    col.objects.link(hood)
    bpy.context.scene.collection.objects.unlink(hood)

    # Grille
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.72, 0.52))
    grille = bpy.context.active_object
    grille.scale = (1.05, 0.1, 0.4)
    grille.data.materials.append(mats['car_trim'])
    grille.parent = root
    col.objects.link(grille)
    bpy.context.scene.collection.objects.unlink(grille)

    # 3. Bullbar & Rally Headlights
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.5, location=(0, 1.88, 0.55))
    bbar = bpy.context.active_object
    bbar.rotation_euler = (0, math.pi/2, 0)
    bbar.data.materials.append(mats['car_chrome'])
    bbar.parent = root
    col.objects.link(bbar)
    bpy.context.scene.collection.objects.unlink(bbar)

    for lx in [-0.62, 0.62]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.18, location=(lx, 1.84, 0.8))
        hl_case = bpy.context.active_object
        hl_case.rotation_euler = (math.pi/2, 0, 0)
        hl_case.data.materials.append(mats['car_chrome'])
        hl_case.parent = root
        col.objects.link(hl_case)
        bpy.context.scene.collection.objects.unlink(hl_case)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.06, location=(lx, 1.92, 0.8))
        hl_lens = bpy.context.active_object
        hl_lens.rotation_euler = (math.pi/2, 0, 0)
        hl_lens.data.materials.append(mats['car_headlight'])
        hl_lens.parent = root
        col.objects.link(hl_lens)
        bpy.context.scene.collection.objects.unlink(hl_lens)

    # 4. Cabin & Windows
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 1.15))
    cabin = bpy.context.active_object
    cabin.scale = (1.25, 1.45, 0.65)
    cabin.data.materials.append(paint)
    cabin.parent = root
    col.objects.link(cabin)
    bpy.context.scene.collection.objects.unlink(cabin)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.52, 1.18))
    windshield = bpy.context.active_object
    windshield.scale = (1.1, 0.1, 0.5)
    windshield.rotation_euler = (math.radians(35), 0, 0)
    windshield.data.materials.append(mats['car_glass'])
    windshield.parent = root
    col.objects.link(windshield)
    bpy.context.scene.collection.objects.unlink(windshield)

    for wx_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx_sign * 0.62, -0.05, 1.16))
        swindow = bpy.context.active_object
        swindow.scale = (0.05, 1.0, 0.42)
        swindow.data.materials.append(mats['car_glass'])
        swindow.parent = root
        col.objects.link(swindow)
        bpy.context.scene.collection.objects.unlink(swindow)

    # Roof fins
    for rf_y in [-0.35, -0.05, 0.25]:
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.08, depth=0.18, location=(0, rf_y, 1.52))
        fin = bpy.context.active_object
        fin.rotation_euler = (math.radians(-25), 0, 0)
        fin.data.materials.append(mats['car_trim'])
        fin.parent = root
        col.objects.link(fin)
        bpy.context.scene.collection.objects.unlink(fin)

    # 5. Fenders
    for fx_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx_sign * 1.08, 1.05, 0.78))
        f_fender = bpy.context.active_object
        f_fender.scale = (0.65, 1.1, 0.32)
        f_fender.rotation_euler = (math.radians(-10), fx_sign * math.radians(-8), 0)
        f_fender.data.materials.append(paint)
        f_fender.parent = root
        col.objects.link(f_fender)
        bpy.context.scene.collection.objects.unlink(f_fender)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx_sign * 1.15, -1.05, 0.88))
        r_fender = bpy.context.active_object
        r_fender.scale = (0.72, 1.25, 0.42)
        r_fender.rotation_euler = (math.radians(8), fx_sign * math.radians(6), 0)
        r_fender.data.materials.append(paint)
        r_fender.parent = root
        col.objects.link(r_fender)
        bpy.context.scene.collection.objects.unlink(r_fender)

    # 6. Exposed Engine & Red Valve Heads
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.92, 0.75))
    eng = bpy.context.active_object
    eng.scale = (0.95, 0.9, 0.55)
    eng.data.materials.append(mats['car_trim'])
    eng.parent = root
    col.objects.link(eng)
    bpy.context.scene.collection.objects.unlink(eng)

    for ex_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex_sign * 0.35, -0.92, 0.95))
        vhead = bpy.context.active_object
        vhead.scale = (0.28, 0.75, 0.2)
        vhead.rotation_euler = (0, ex_sign * math.radians(-25), 0)
        vhead.data.materials.append(mats['car_red'])
        vhead.parent = root
        col.objects.link(vhead)
        bpy.context.scene.collection.objects.unlink(vhead)

    # 7. Spoiler
    for sx in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.8, location=(sx, -1.42, 1.25))
        strut = bpy.context.active_object
        strut.rotation_euler = (math.radians(-25), 0, 0)
        strut.data.materials.append(mats['car_trim'])
        strut.parent = root
        col.objects.link(strut)
        bpy.context.scene.collection.objects.unlink(strut)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.58, 1.62))
    wing = bpy.context.active_object
    wing.scale = (1.95, 0.42, 0.08)
    wing.rotation_euler = (math.radians(-12), 0, 0)
    wing.data.materials.append(paint)
    wing.parent = root
    col.objects.link(wing)
    bpy.context.scene.collection.objects.unlink(wing)

    for wx_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx_sign * 0.98, -1.58, 1.64))
        endplate = bpy.context.active_object
        endplate.scale = (0.05, 0.48, 0.28)
        endplate.rotation_euler = (math.radians(-12), 0, 0)
        endplate.data.materials.append(paint)
        endplate.parent = root
        col.objects.link(endplate)
        bpy.context.scene.collection.objects.unlink(endplate)

    # 8. Wheels
    wheel_positions = [
        ("FL", (-1.12, 1.08, 0.44), 0.44, 0.38),
        ("FR", (1.12, 1.08, 0.44), 0.44, 0.38),
        ("RL", (-1.22, -1.08, 0.50), 0.50, 0.44),
        ("RR", (1.22, -1.08, 0.50), 0.50, 0.44),
    ]
    for wname, wpos, wrad, wwid in wheel_positions:
        create_wheel(col, mats, root, f"{name}_{wname}", wpos, radius=wrad, width=wwid)

    # 9. Rocket Boost Plume
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.85, radius2=0.15, depth=5.5, location=(0, -4.6, 0.65))
    flame = bpy.context.active_object
    flame.rotation_euler = (math.pi/2, 0, 0)
    flame.data.materials.append(mats['boost_flame'])
    flame.parent = root
    col.objects.link(flame)
    bpy.context.scene.collection.objects.unlink(flame)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.45, radius2=0.08, depth=3.2, location=(0, -3.3, 0.65))
    core_flame = bpy.context.active_object
    core_flame.rotation_euler = (math.pi/2, 0, 0)
    core_flame.data.materials.append(mats['boost_core'])
    core_flame.parent = root
    col.objects.link(core_flame)
    bpy.context.scene.collection.objects.unlink(core_flame)

    # 10. Neon Underglow
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2))
    uglow = bpy.context.active_object
    uglow.scale = (1.35, 2.6, 0.04)
    uglow.data.materials.append(underglow)
    uglow.parent = root
    col.objects.link(uglow)
    bpy.context.scene.collection.objects.unlink(uglow)

    return root

def build_dominus(col, mats, name="Dominus_Orange"):
    """Builds the muscular Orange Team Dominus battle-car."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = name
    col.objects.link(root)
    bpy.context.scene.collection.objects.unlink(root)

    paint = mats['car_paint_orange']
    underglow = mats['underglow_orange']

    # 1. Wide Low Muscle Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.1, 0.38))
    chassis = bpy.context.active_object
    chassis.scale = (1.65, 3.6, 0.32)
    chassis.data.materials.append(mats['car_trim'])
    chassis.parent = root
    col.objects.link(chassis)
    bpy.context.scene.collection.objects.unlink(chassis)

    # 2. Long Low Hood
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.95, 0.62))
    hood = bpy.context.active_object
    hood.scale = (1.55, 1.85, 0.32)
    hood.rotation_euler = (math.radians(-6), 0, 0)
    hood.data.materials.append(paint)
    hood.parent = root
    col.objects.link(hood)
    bpy.context.scene.collection.objects.unlink(hood)

    # Black Dual Racing Stripes on Hood
    for sx in [-0.28, 0.28]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.95, 0.79))
        stripe = bpy.context.active_object
        stripe.scale = (0.22, 1.82, 0.04)
        stripe.rotation_euler = (math.radians(-6), 0, 0)
        stripe.data.materials.append(mats['car_trim'])
        stripe.parent = root
        col.objects.link(stripe)
        bpy.context.scene.collection.objects.unlink(stripe)

    # Exposed Supercharger Blower
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.85, 0.92))
    blower = bpy.context.active_object
    blower.scale = (0.5, 0.65, 0.35)
    blower.data.materials.append(mats['car_chrome'])
    blower.parent = root
    col.objects.link(blower)
    bpy.context.scene.collection.objects.unlink(blower)

    # Rectangular Front Grille & Headlights
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.9, 0.52))
    grille = bpy.context.active_object
    grille.scale = (1.45, 0.08, 0.38)
    grille.data.materials.append(mats['car_trim'])
    grille.parent = root
    col.objects.link(grille)
    bpy.context.scene.collection.objects.unlink(grille)

    for hx in [-0.58, 0.58]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, 1.94, 0.54))
        hl = bpy.context.active_object
        hl.scale = (0.24, 0.04, 0.16)
        hl.data.materials.append(mats['car_headlight'])
        hl.parent = root
        col.objects.link(hl)
        bpy.context.scene.collection.objects.unlink(hl)

    # 3. Chopped Roof Cabin & Dark Glass
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.35, 0.98))
    cabin = bpy.context.active_object
    cabin.scale = (1.35, 1.35, 0.52)
    cabin.data.materials.append(paint)
    cabin.parent = root
    col.objects.link(cabin)
    bpy.context.scene.collection.objects.unlink(cabin)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.28, 0.98))
    windshield = bpy.context.active_object
    windshield.scale = (1.25, 0.08, 0.42)
    windshield.rotation_euler = (math.radians(38), 0, 0)
    windshield.data.materials.append(mats['car_glass'])
    windshield.parent = root
    col.objects.link(windshield)
    bpy.context.scene.collection.objects.unlink(windshield)

    # 4. Rear Deck & Ducktail Spoiler
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.25, 0.72))
    rear_deck = bpy.context.active_object
    rear_deck.scale = (1.52, 0.95, 0.38)
    rear_deck.data.materials.append(paint)
    rear_deck.parent = root
    col.objects.link(rear_deck)
    bpy.context.scene.collection.objects.unlink(rear_deck)

    # Ducktail spoiler lip
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.72, 0.98))
    spoil = bpy.context.active_object
    spoil.scale = (1.68, 0.22, 0.18)
    spoil.rotation_euler = (math.radians(22), 0, 0)
    spoil.data.materials.append(mats['car_trim'])
    spoil.parent = root
    col.objects.link(spoil)
    bpy.context.scene.collection.objects.unlink(spoil)

    # 5. Dominus Wheels
    wheel_positions = [
        ("FL", (-1.15, 1.15, 0.42), 0.42, 0.38),
        ("FR", (1.15, 1.15, 0.42), 0.42, 0.38),
        ("RL", (-1.25, -1.15, 0.48), 0.48, 0.45),
        ("RR", (1.25, -1.15, 0.48), 0.48, 0.45),
    ]
    for wname, wpos, wrad, wwid in wheel_positions:
        create_wheel(col, mats, root, f"{name}_{wname}", wpos, radius=wrad, width=wwid)

    # 6. Magma Rocket Boost Flame
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.88, radius2=0.15, depth=5.8, location=(0, -4.8, 0.62))
    flame = bpy.context.active_object
    flame.rotation_euler = (math.pi/2, 0, 0)
    flame.data.materials.append(mats['boost_flame'])
    flame.parent = root
    col.objects.link(flame)
    bpy.context.scene.collection.objects.unlink(flame)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.48, radius2=0.08, depth=3.4, location=(0, -3.4, 0.62))
    core_flame = bpy.context.active_object
    core_flame.rotation_euler = (math.pi/2, 0, 0)
    core_flame.data.materials.append(mats['boost_core'])
    core_flame.parent = root
    col.objects.link(core_flame)
    bpy.context.scene.collection.objects.unlink(core_flame)

    # 7. Neon Underglow
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.18))
    uglow = bpy.context.active_object
    uglow.scale = (1.45, 3.0, 0.04)
    uglow.data.materials.append(underglow)
    uglow.parent = root
    col.objects.link(uglow)
    bpy.context.scene.collection.objects.unlink(uglow)

    return root


# ==============================================================================
# KEYFRAME ANIMATION GENERATOR (120 FRAMES)
# ==============================================================================

def animate_showdown(ball, octane, dominus, cam):
    """Applies 120-frame keyframed trajectories to Ball, Cars, and Camera."""
    # 1. ROCKET LEAGUE BALL TRAJECTORY
    # Frame 1: Low arc over Blue midfield
    # Frame 60: Peak aerial height, contested by Octane & Dominus
    # Frame 120: Screaming towards the top-corner of Orange goal
    ball_traj = [
        (1,   (0.0, -10.0, 6.5),  (0, 0, 0)),
        (30,  (0.8, 8.0, 11.2),   (math.radians(180), 0, math.radians(120))),
        (60,  (1.8, 24.0, 13.8),  (math.radians(360), 0, math.radians(240))),
        (90,  (2.2, 38.0, 12.0),  (math.radians(540), 0, math.radians(360))),
        (120, (2.6, 50.8, 6.2),   (math.radians(720), 0, math.radians(480))),
    ]
    for frame, loc, rot in ball_traj:
        ball.location = loc
        ball.rotation_euler = rot
        ball.keyframe_insert(data_path="location", frame=frame)
        ball.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 2. BLUE OCTANE AERIAL STRIKE TRAJECTORY
    # Flying forward and upward with a freestyle barrel-roll
    octane_traj = [
        (1,   (-10.0, -22.0, 3.5), (math.radians(-32), math.radians(-15), math.radians(25))),
        (30,  (-4.5, 0.0, 8.8),    (math.radians(-28), math.radians(-180), math.radians(15))),
        (60,  (0.2, 21.5, 13.2),   (math.radians(-22), math.radians(-360), math.radians(10))),
        (90,  (4.2, 36.0, 11.5),   (math.radians(-15), math.radians(-420), math.radians(5))),
        (120, (7.5, 48.0, 8.0),    (math.radians(-10), math.radians(-480), 0)),
    ]
    for frame, loc, rot in octane_traj:
        octane.location = loc
        octane.rotation_euler = rot
        octane.keyframe_insert(data_path="location", frame=frame)
        octane.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 3. ORANGE DOMINUS INVERTED DEFENSIVE SAVE TRAJECTORY
    # Rocketing off the Orange goal line upwards to challenge the shot
    dominus_traj = [
        (1,   (6.0, 49.0, 1.5),   (math.radians(10), 0, math.radians(175))),
        (30,  (5.2, 40.0, 7.5),   (math.radians(35), math.radians(45), math.radians(185))),
        (60,  (3.4, 26.5, 14.2),  (math.radians(55), math.radians(180), math.radians(195))),
        (90,  (1.8, 14.0, 10.5),  (math.radians(35), math.radians(240), math.radians(205))),
        (120, (0.5, 2.0, 3.5),    (math.radians(15), math.radians(360), math.radians(210))),
    ]
    for frame, loc, rot in dominus_traj:
        dominus.location = loc
        dominus.rotation_euler = rot
        dominus.keyframe_insert(data_path="location", frame=frame)
        dominus.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 4. CINEMATIC ACTION CAMERA
    # Sweeps dynamically to keep the ball and both aerial cars in the sweet spot
    cam_traj = [
        (1,   (-16.0, -38.0, 12.0), (math.radians(72), 0, math.radians(-22))),
        (60,  (-9.5, 8.0, 16.5),    (math.radians(68), 0, math.radians(-48))),
        (120, (14.0, 32.0, 15.0),   (math.radians(75), 0, math.radians(-115))),
    ]
    for frame, loc, rot in cam_traj:
        cam.location = loc
        cam.rotation_euler = rot
        cam.keyframe_insert(data_path="location", frame=frame)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame)


def setup_cameras(col):
    # 1. Action Clash Camera (Framed on the aerial showdown with the Pagoda in background)
    cam_action_data = bpy.data.cameras.new('Camera_ActionClash')
    cam_action_data.lens = 28.0
    cam_action_data.clip_end = 1500.0
    cam_action = bpy.data.objects.new('Camera_ActionClash', cam_action_data)
    cam_action.location = (-9.5, 8.0, 16.5)
    cam_action.rotation_euler = (math.radians(68), 0, math.radians(-48))
    col.objects.link(cam_action)
    bpy.context.scene.camera = cam_action

    # 2. Stadium Reference Overview Camera
    cam_ref_data = bpy.data.cameras.new('Camera_ReferenceView')
    cam_ref_data.lens = 25.0
    cam_ref_data.clip_end = 1500.0
    cam_ref = bpy.data.objects.new('Camera_ReferenceView', cam_ref_data)
    cam_ref.location = (0.0, -102.0, 48.0)
    cam_ref.rotation_euler = (math.radians(72.5), 0.0, 0.0)
    col.objects.link(cam_ref)

    return cam_action


def build_scene():
    print('=' * 60)
    print('Building Rocket League Forbidden Temple OVERDRIVE in Blender 5.1...')
    print('=' * 60)

    reset_scene()

    main_col = make_collection('ForbiddenTemple_Overdrive')
    pitch_col = make_collection('Pitch_And_Cage', main_col)
    stadium_col = make_collection('Stadium_Architecture', main_col)
    temple_col = make_collection('Pagodas_And_Temples', main_col)
    env_col = make_collection('Environment_And_Nature', main_col)
    actors_col = make_collection('BattleCars_And_Ball', main_col)
    light_col = make_collection('Lighting_And_Cameras', main_col)

    print('Setting up materials...')
    mats = setup_all_materials()

    print('Building pitch, forcefield cage, and boost pads...')
    build_pitch_and_cage(pitch_col, mats)

    print('Building stadium grandstands and fortress walls...')
    build_stadium_and_walls(stadium_col, mats)

    print('Building pagodas, main hall, bridge, and torii gates...')
    build_pagodas_and_bridge(temple_col, mats)

    print('Building environment, mountains, waterfall, and sakura trees...')
    build_environment(env_col, mats)

    print('Building Official Rocket League Ball...')
    ball = build_rocket_league_ball(actors_col, mats, radius=2.1)

    print('Building Blue Team Octane...')
    octane = build_octane(actors_col, mats, name="Octane_Blue")

    print('Building Orange Team Dominus...')
    dominus = build_dominus(actors_col, mats, name="Dominus_Orange")

    print('Setting up twilight sky and lighting...')
    setup_world_and_lighting(light_col)

    print('Setting up action cameras...')
    action_cam = setup_cameras(light_col)

    print('Applying 120-frame Rocket League aerial animation...')
    animate_showdown(ball, octane, dominus, action_cam)

    # Set timeline to Frame 60 (Peak aerial strike)
    bpy.context.scene.frame_set(60)

    # Configure Fast High-Quality Cycles Settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    try:
        cprefs = bpy.context.preferences.addons['cycles'].preferences
        cprefs.compute_device_type = 'METAL'
        scene.cycles.device = 'GPU'
        print('Cycles Metal GPU enabled.')
    except Exception as e:
        print(f'Cycles notice: {e}')

    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.06
    scene.cycles.volume_max_steps = 12
    scene.cycles.volume_step_rate = 6.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    blend_path = os.path.abspath('forbidden_temple.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f'Scene successfully saved to: {blend_path}')

    # Render Peak Aerial Action Frame (Frame 60)
    action_render_path = os.path.abspath('forbidden_temple_action_render.png')
    scene.render.filepath = action_render_path
    print(f'Rendering peak action frame (Frame 60) to: {action_render_path}...')
    bpy.ops.render.render(write_still=True)
    print(f'Action render complete: {action_render_path}')

    print('=' * 60)

if __name__ == '__main__':
    build_scene()
