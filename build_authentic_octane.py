"""
Authentic 1:1 Rocket League Octane Builder for Blender 5.x.
Directly reproduces the vehicle in media_1790263831226.png:
- Hard-surface athletic buggy body (angular, faceted, NOT a round bubble)
- Proper Octane proportions (compact, muscular, wide stance, aggressive clearance)
- Big, chunky, aggressive off-road wheels with deep-dish 10-spoke rims, hollow tires, red calipers
- Front tapered nose with tubular bullbar & 4 projector lights (outer cyan halos, lower fog lights)
- Continuous dual Alpine White racing stripes with cyan pinstripes down hood, roof, and spoiler
- Raked tinted cockpit with Titanium White A-pillars & black roof scoop
- Sculpted side body with wasp waist & subtle neon cyan rocker accents
- Exposed rear V8 engine with bright red cylinder heads (#D32F2F) & chrome intake horns
- Dual chrome rocket thruster nozzles with glowing cyan plasma cores
- High-downforce rear wing with Titanium White endplates
- Double-wishbone suspension wishbones connecting chassis to wheels
- Camera perfectly framing the entire car in 3/4 beauty view
"""

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math
import os

TEX_PATH = os.path.abspath("car_livery_blueprint.png")

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)

def make_collection(name, parent=None):
    parent = parent or bpy.context.scene.collection
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        parent.children.link(col)
    return col

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat

def setup_materials():
    mats = {}

    # 1. Cobalt Blue Metallic Base Paint with High-Res Livery
    m_body = get_or_create_material('Mat_Octane_CobaltBlue')
    nt = m_body.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    if os.path.exists(TEX_PATH):
        img = bpy.data.images.load(TEX_PATH, check_existing=True)
        tex_node = nt.nodes.new('ShaderNodeTexImage')
        tex_node.image = img
        nt.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.28, 0.95, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.75
        bsdf.inputs['Coat Roughness'].default_value = 0.05
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['body'] = m_body

    # 2. Titanium White Trim (#FFFFFF) for A-pillars, fender lips, winglets
    m_white = get_or_create_material('Mat_Octane_TitaniumWhite')
    nt = m_white.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.20
    bsdf.inputs['Roughness'].default_value = 0.16
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.60
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['white'] = m_white

    # 3. Dark Metallic Chassis & Bullbar
    m_chassis = get_or_create_material('Mat_Octane_Chassis')
    nt = m_chassis.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.06, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.25
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['chassis'] = m_chassis

    # 4. Racing Red Engine Cylinder Heads (#D32F2F) & Brake Calipers
    m_red = get_or_create_material('Mat_Octane_EngineRed')
    nt = m_red.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.86, 0.05, 0.07, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.40
    bsdf.inputs['Roughness'].default_value = 0.20
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['engine_red'] = m_red

    # 5. Polished Mirror Chrome (Pipes, Nozzles, Hubs)
    m_chrome = get_or_create_material('Mat_Octane_Chrome')
    nt = m_chrome.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.04
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['chrome'] = m_chrome

    # 6. Tinted Aerodynamic Cockpit Glass
    m_glass = get_or_create_material('Mat_Octane_Glass')
    nt = m_glass.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.04, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Metallic'].default_value = 0.30
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.65
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.65
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['glass'] = m_glass

    # 7. Gunmetal Christiano Alloy Wheels
    m_wheel = get_or_create_material('Mat_Octane_WheelAlloy')
    nt = m_wheel.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.14, 0.15, 0.17, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.18
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['wheel_alloy'] = m_wheel

    # 8. Deep-Tread Matte Rubber Tires
    m_tire = get_or_create_material('Mat_Octane_TireRubber')
    nt = m_tire.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.035, 0.035, 0.035, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.02
    bsdf.inputs['Roughness'].default_value = 0.80
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['tire'] = m_tire

    # 9. Drilled Steel Brake Rotor Disc
    m_rotor = get_or_create_material('Mat_Octane_BrakeRotor')
    nt = m_rotor.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.75, 0.77, 0.80, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.30
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['rotor'] = m_rotor

    # 10. Neon Cyan Emissive Accent (#00F0FF)
    m_neon = get_or_create_material('Mat_Octane_NeonCyan')
    nt = m_neon.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.0, 0.92, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.0, 0.92, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 15.0
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['neon_cyan'] = m_neon

    # 11. Glowing Red Taillight
    m_tail = get_or_create_material('Mat_Octane_TailRed')
    nt = m_tail.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.04, 0.04, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.04, 0.04, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 12.0
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['tail_red'] = m_tail

    return mats

def link_hierarchy(obj, col):
    """Recursively links an object and all its children into the collection."""
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects and bpy.context.scene.collection != col:
        try:
            bpy.context.scene.collection.objects.unlink(obj)
        except Exception:
            pass
    for child in obj.children:
        link_hierarchy(child, col)

def create_sloped_hood(name, mat):
    """
    Creates the authentic sloped aerodynamic Octane hood:
    - Central channel with dual continuous Alpine White racing stripes and cyan pinstripes
    - Flanked by angled bevels and side crease ridges
    - UV mapped precisely to car_livery_blueprint.png
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Stations from front nose (+Y = 1.70) up to base of windshield (+Y = 0.48)
    stations = [
        # Y, center_z, ridge_w, ridge_z, outer_w, outer_z
        (1.70, 0.40, 0.20, 0.38, 0.38, 0.34),
        (1.45, 0.48, 0.24, 0.47, 0.46, 0.42),
        (1.15, 0.58, 0.28, 0.57, 0.52, 0.52),
        (0.82, 0.69, 0.32, 0.68, 0.56, 0.62),
        (0.48, 0.80, 0.36, 0.79, 0.58, 0.74),
    ]

    grid = []
    for py, cz, rw, rz, ow, oz in stations:
        row = [
            bm.verts.new(Vector((-ow, py, oz))),
            bm.verts.new(Vector((-rw, py, rz))),
            bm.verts.new(Vector((0.0, py, cz))),
            bm.verts.new(Vector((rw, py, rz))),
            bm.verts.new(Vector((ow, py, oz))),
        ]
        grid.append(row)

    # UV layout: center is 0.50, stripes are between 0.44 and 0.56
    u_vals = [0.10, 0.36, 0.50, 0.64, 0.90]
    n_st = len(stations)
    for s in range(n_st - 1):
        v0 = 0.92 - (s / (n_st - 1)) * 0.48
        v1 = 0.92 - ((s + 1) / (n_st - 1)) * 0.48
        for c in range(4):
            va = grid[s][c]
            vb = grid[s][c+1]
            vc = grid[s+1][c+1]
            vd = grid[s+1][c]
            face = bm.faces.new((va, vb, vc, vd))
            for loop in face.loops:
                if loop.vert == va: loop[uv_layer].uv = (u_vals[c], v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u_vals[c+1], v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u_vals[c+1], v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u_vals[c], v1)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    for p in obj.data.polygons: p.use_smooth = True
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.014
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    return obj

def create_angular_cockpit(name, mats):
    """
    Creates the iconic angular Octane cockpit cabin:
    - Flat 42° raked tinted windshield
    - Titanium White A-pillars running up into the roof rails
    - Flat low-profile sports roof with dual white stripes
    - Dark tinted side triangular windows
    - Black roof air scoop on top
    """
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    # 1. Raked Tinted Windshield Glass
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    windshield = bpy.context.active_object
    windshield.parent = root
    windshield.location = (0, 0.20, 1.04)
    windshield.scale = (0.76, 0.60, 0.028)
    windshield.rotation_euler = (math.radians(-42), 0, 0)
    windshield.data.materials.append(mats['glass'])
    windshield.name = f"{name}_Windshield"

    # 2. Titanium White Structural A-Pillars
    for px in [-0.40, 0.40]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        pillar = bpy.context.active_object
        pillar.parent = root
        pillar.location = (px, 0.20, 1.04)
        pillar.scale = (0.075, 0.64, 0.055)
        pillar.rotation_euler = (math.radians(-42), 0, 0)
        pillar.data.materials.append(mats['white'])
        pillar.name = f"{name}_APillar_{'L' if px > 0 else 'R'}"
        for p in pillar.data.polygons: p.use_smooth = True
        bev = pillar.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.010
        bev.segments = 2

    # 3. Flat Low-Profile Sports Roof Deck with Continuing Stripes
    r_mesh = bpy.data.meshes.new(f"{name}_RoofMesh")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    # Roof rectangle: x from -0.38 to +0.38, y from -0.62 to -0.04, z = 1.25
    v0 = bm.verts.new(Vector((-0.38, -0.04, 1.25)))
    v1 = bm.verts.new(Vector((0.38, -0.04, 1.25)))
    v2 = bm.verts.new(Vector((0.38, -0.62, 1.22)))
    v3 = bm.verts.new(Vector((-0.38, -0.62, 1.22)))
    f = bm.faces.new((v0, v1, v2, v3))
    # Map UVs so center stripes continue cleanly: u=0.5 in center
    for loop in f.loops:
        if loop.vert == v0: loop[uv].uv = (0.15, 0.42)
        elif loop.vert == v1: loop[uv].uv = (0.85, 0.42)
        elif loop.vert == v2: loop[uv].uv = (0.85, 0.20)
        elif loop.vert == v3: loop[uv].uv = (0.15, 0.20)
    bm.to_mesh(r_mesh)
    bm.free()

    roof = bpy.data.objects.new(f"{name}_RoofDeck", r_mesh)
    roof.parent = root
    roof.data.materials.append(mats['body'])
    for p in roof.data.polygons: p.use_smooth = True
    sol = roof.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.04

    # Titanium White Roof Side Rails
    for rx in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        rail = bpy.context.active_object
        rail.parent = root
        rail.location = (rx, -0.33, 1.24)
        rail.scale = (0.05, 0.58, 0.05)
        rail.data.materials.append(mats['white'])
        rail.name = f"{name}_RoofRail_{'L' if rx > 0 else 'R'}"
        for p in rail.data.polygons: p.use_smooth = True

    # 4. Side Window Glass
    for wx in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        swin = bpy.context.active_object
        swin.parent = root
        swin.location = (wx, -0.22, 1.05)
        swin.scale = (0.02, 0.52, 0.30)
        swin.data.materials.append(mats['glass'])
        swin.name = f"{name}_SideWindow_{'L' if wx > 0 else 'R'}"

    # 5. Black Aerodynamic Dual-Port Roof Air Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    r_scoop = bpy.context.active_object
    r_scoop.parent = root
    r_scoop.location = (0, -0.30, 1.34)
    r_scoop.scale = (0.36, 0.36, 0.09)
    r_scoop.rotation_euler = (math.radians(6), 0, 0)
    r_scoop.data.materials.append(mats['chassis'])
    r_scoop.name = f"{name}_RoofAirScoop"
    for p in r_scoop.data.polygons: p.use_smooth = True
    bev = r_scoop.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.012
    bev.segments = 2

    # Dual scoop front intake nostrils
    for sx in [-0.10, 0.10]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        nostril = bpy.context.active_object
        nostril.parent = root
        nostril.location = (sx, -0.11, 1.34)
        nostril.scale = (0.10, 0.03, 0.05)
        nostril.data.materials.append(mats['chassis'])
        nostril.name = f"{name}_ScoopNostril_{sx}"

    return root

def build_hollow_sports_wheel(name, mats, outer_r=0.48, width=0.34, is_left=True):
    """
    Builds large, chunky, aggressive off-road racing wheel matching media_1790263831226.png:
    - Hollow rubber tire with rounded shoulders and flat tread face
    - Deep-dish gunmetal 10-spoke rim recessed inside the tire
    - Drilled steel brake rotor disc
    - Bright Racing Red brake caliper clamping the rotor
    - Polished chrome center hub cap
    """
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    face_dir = 1.0 if is_left else -1.0
    inner_rim_r = outer_r * 0.62

    # 1. Hollow Tire Mesh (Revolving profile along X axle)
    t_mesh = bpy.data.meshes.new(f"{name}_TireMesh")
    bm = bmesh.new()

    profile = [
        (-width * 0.44, inner_rim_r),                   # Inner bead
        (-width * 0.52, (inner_rim_r + outer_r) * 0.5), # Inner bulging sidewall
        (-width * 0.48, outer_r - 0.02),               # Inner rounded shoulder
        (-width * 0.32, outer_r),                      # Tread surface inner
        (0.0, outer_r + 0.005),                        # Tread surface center crown
        (width * 0.32, outer_r),                       # Tread surface outer
        (width * 0.48, outer_r - 0.02),                # Outer rounded shoulder
        (width * 0.52, (inner_rim_r + outer_r) * 0.5), # Outer bulging sidewall
        (width * 0.44, inner_rim_r)                    # Outer rim bead
    ]

    segments = 24
    rings = []
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        ring_verts = []
        for x_off, r in profile:
            ring_verts.append(bm.verts.new(Vector((x_off, cos_a * r, sin_a * r))))
        rings.append(ring_verts)

    p_len = len(profile)
    for s in range(segments):
        next_s = (s + 1) % segments
        for p in range(p_len - 1):
            bm.faces.new((rings[s][p], rings[next_s][p], rings[next_s][p + 1], rings[s][p + 1]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(t_mesh)
    bm.free()

    tire = bpy.data.objects.new(f"{name}_Tire", t_mesh)
    tire.data.materials.append(mats['tire'])
    tire.parent = root
    for poly in tire.data.polygons:
        poly.use_smooth = True

    # 2. Deep-Dish Gunmetal Outer Rim Bezel
    rim_outer_x = face_dir * (width * 0.44)
    bpy.ops.mesh.primitive_torus_add(major_radius=inner_rim_r + 0.015, minor_radius=0.024)
    rim = bpy.context.active_object
    rim.parent = root
    rim.location = (rim_outer_x, 0, 0)
    rim.rotation_euler = (0, math.pi/2, 0)
    rim.data.materials.append(mats['wheel_alloy'])
    rim.name = f"{name}_RimBezel"
    for poly in rim.data.polygons: poly.use_smooth = True

    # 3. Recessed Inner Rim Barrel
    barrel_depth = 0.18
    barrel_x = face_dir * (width * 0.44 - barrel_depth * 0.5)
    bpy.ops.mesh.primitive_cylinder_add(radius=inner_rim_r, depth=barrel_depth, end_fill_type='NOTHING')
    barrel = bpy.context.active_object
    barrel.parent = root
    barrel.location = (barrel_x, 0, 0)
    barrel.rotation_euler = (0, math.pi/2, 0)
    barrel.data.materials.append(mats['wheel_alloy'])
    barrel.name = f"{name}_RimBarrel"
    for poly in barrel.data.polygons: poly.use_smooth = True

    # 4. 10 Alloy Spokes
    spoke_x = face_dir * (width * 0.44 - 0.06)
    for s_idx in range(10):
        ang = s_idx * (2.0 * math.pi / 10.0)
        sy = math.cos(ang) * (inner_rim_r * 0.52)
        sz = math.sin(ang) * (inner_rim_r * 0.52)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        spoke = bpy.context.active_object
        spoke.parent = root
        spoke.location = (spoke_x, sy, sz)
        spoke.scale = (0.024, 0.042, inner_rim_r * 0.88)
        spoke.rotation_euler = (ang, 0, 0)
        spoke.data.materials.append(mats['wheel_alloy'])
        spoke.name = f"{name}_Spoke_{s_idx}"
        for poly in spoke.data.polygons: poly.use_smooth = True

    # 5. Polished Chrome Center Hub
    hub_x = face_dir * (width * 0.44 - 0.04)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.045)
    hub = bpy.context.active_object
    hub.parent = root
    hub.location = (hub_x, 0, 0)
    hub.rotation_euler = (0, math.pi/2, 0)
    hub.data.materials.append(mats['chrome'])
    hub.name = f"{name}_Hub"

    # 6. Steel Brake Rotor Disc
    rotor_x = face_dir * (width * 0.44 - 0.13)
    bpy.ops.mesh.primitive_cylinder_add(radius=inner_rim_r * 0.78, depth=0.018)
    rotor = bpy.context.active_object
    rotor.parent = root
    rotor.location = (rotor_x, 0, 0)
    rotor.rotation_euler = (0, math.pi/2, 0)
    rotor.data.materials.append(mats['rotor'])
    rotor.name = f"{name}_BrakeRotor"

    # 7. Bright Racing Red Brake Caliper
    caliper_x = face_dir * (width * 0.44 - 0.12)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    caliper = bpy.context.active_object
    caliper.parent = root
    caliper.location = (caliper_x, 0.17, 0.16)
    caliper.scale = (0.055, 0.14, 0.10)
    caliper.rotation_euler = (-0.6, 0, 0)
    caliper.data.materials.append(mats['engine_red'])
    caliper.name = f"{name}_BrakeCaliper"
    bev = caliper.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.008
    bev.segments = 2

    return root

def build_sculpted_fender_arch(name, mats, outer_r=0.52, width=0.28, is_rear=False, is_left=True):
    """
    Builds the iconic Octane curved fender arch flare:
    - Arches gracefully over the top of the tire
    - Features a sweeping Titanium White lower accent trim
    - Integrates cleanly into the body
    """
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    x_sign = 1.0 if is_left else -1.0
    start_deg = 32.0
    end_deg = 148.0
    arc_pts = 10

    # 1. Main Cobalt Blue Arch
    mesh = bpy.data.meshes.new(f"{name}_ArchMesh")
    bm = bmesh.new()
    in_v, out_v = [], []
    for i in range(arc_pts):
        t = i / (arc_pts - 1)
        ang = math.radians(start_deg + t * (end_deg - start_deg))
        y = math.cos(ang) * outer_r
        z = math.sin(ang) * outer_r
        v0 = bm.verts.new(Vector((-width * 0.5 * x_sign, y, z)))
        v1 = bm.verts.new(Vector((width * 0.5 * x_sign, y, z)))
        in_v.append(v0)
        out_v.append(v1)

    for i in range(arc_pts - 1):
        bm.faces.new((in_v[i], out_v[i], out_v[i+1], in_v[i+1]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    arch = bpy.data.objects.new(f"{name}_Arch", mesh)
    arch.parent = root
    arch.data.materials.append(mats['body'])
    for p in arch.data.polygons: p.use_smooth = True
    bev = arch.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.012
    bev.segments = 2

    # 2. Titanium White Outer Accent Lip
    lip_mesh = bpy.data.meshes.new(f"{name}_LipMesh")
    bm_lip = bmesh.new()
    lip_r = outer_r + 0.016
    lip_w = 0.055
    l_in, l_out = [], []
    for i in range(arc_pts):
        t = i / (arc_pts - 1)
        ang = math.radians(start_deg + t * (end_deg - start_deg))
        y = math.cos(ang) * lip_r
        z = math.sin(ang) * lip_r
        l_in.append(bm_lip.verts.new(Vector((0.0, y, z))))
        l_out.append(bm_lip.verts.new(Vector((x_sign * lip_w, y, z - 0.035))))

    for i in range(arc_pts - 1):
        bm_lip.faces.new((l_in[i], l_out[i], l_out[i+1], l_in[i+1]))

    bmesh.ops.recalc_face_normals(bm_lip, faces=bm_lip.faces)
    bm_lip.to_mesh(lip_mesh)
    bm_lip.free()

    lip = bpy.data.objects.new(f"{name}_Lip", lip_mesh)
    lip.parent = root
    lip.location = (x_sign * (width * 0.48), 0, 0)
    lip.data.materials.append(mats['white'])
    for p in lip.data.polygons: p.use_smooth = True

    # 3. Rear Taillight if rear fender
    if is_rear:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.08)
        tl = bpy.context.active_object
        tl.parent = root
        tl.location = (0, -0.42, 0.28)
        tl.rotation_euler = (math.pi/2, 0, 0)
        tl.data.materials.append(mats['tail_red'])
        tl.name = f"{name}_TailLight"

    return root

def build_authentic_octane(col, mats, name="Authentic_Octane", location=(0, 0, 0), rotation=(0, 0, 0)):
    """Builds the complete authentic 1:1 Rocket League Octane in Blender."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    root = bpy.context.active_object
    root.name = name
    root.rotation_euler = rotation

    # =========================================================================
    # 1. LOWER CHASSIS PAN & SCULPTED SIDE SILLS
    # =========================================================================
    # Bottom skid pan
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    pan = bpy.context.active_object
    pan.parent = root
    pan.location = (0, 0.0, 0.32)
    pan.scale = (0.92, 2.70, 0.20)
    pan.data.materials.append(mats['chassis'])
    pan.name = f"{name}_ChassisPan"
    for p in pan.data.polygons: p.use_smooth = True

    # Sculpted Side Sills / Rocker Panels with Wasp Waist
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        sill = bpy.context.active_object
        sill.parent = root
        sill.location = (sx * 0.54, -0.10, 0.42)
        sill.scale = (0.18, 1.45, 0.28)
        sill.data.materials.append(mats['body'])
        sill.name = f"{name}_SideSill_{'L' if sx > 0 else 'R'}"
        for p in sill.data.polygons: p.use_smooth = True
        bev = sill.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.02
        bev.segments = 2

        # Titanium White lower accent runner
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        runner = bpy.context.active_object
        runner.parent = root
        runner.location = (sx * 0.64, -0.10, 0.30)
        runner.scale = (0.04, 1.40, 0.04)
        runner.data.materials.append(mats['white'])
        runner.name = f"{name}_RockerRunner_{'L' if sx > 0 else 'R'}"

        # Subtle thin neon cyan rocker light tube
        bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=1.35)
        neon_t = bpy.context.active_object
        neon_t.parent = root
        neon_t.location = (sx * 0.62, -0.10, 0.24)
        neon_t.rotation_euler = (math.pi/2, 0, 0)
        neon_t.data.materials.append(mats['neon_cyan'])
        neon_t.name = f"{name}_NeonRocker_{'L' if sx > 0 else 'R'}"

    # =========================================================================
    # 2. SCULPTED CONTINUOUS HOOD (Cobalt Blue with Dual Stripes)
    # =========================================================================
    hood = create_sloped_hood(f"{name}_Hood", mats['body'])
    hood.parent = root

    # Titanium White Chamfer Accents along Hood Edges
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        chamf = bpy.context.active_object
        chamf.parent = root
        chamf.location = (sx * 0.44, 1.15, 0.58)
        chamf.scale = (0.08, 0.70, 0.04)
        chamf.rotation_euler = (-0.22, sx * 0.32, 0)
        chamf.data.materials.append(mats['white'])
        chamf.name = f"{name}_HoodTrim_{'L' if sx > 0 else 'R'}"
        for p in chamf.data.polygons: p.use_smooth = True

    # =========================================================================
    # 3. FRONT TUBULAR BULLBAR & 4 PROJECTOR LIGHTS
    # =========================================================================
    # Lower bumper tube
    bpy.ops.mesh.primitive_cylinder_add(radius=0.044, depth=1.16)
    b_low = bpy.context.active_object
    b_low.parent = root
    b_low.location = (0, 1.84, 0.26)
    b_low.rotation_euler = (0, math.pi/2, 0)
    b_low.data.materials.append(mats['chassis'])
    b_low.name = f"{name}_Bullbar_Lower"

    # Upper bumper tube
    bpy.ops.mesh.primitive_cylinder_add(radius=0.040, depth=1.00)
    b_high = bpy.context.active_object
    b_high.parent = root
    b_high.location = (0, 1.78, 0.46)
    b_high.rotation_euler = (0, math.pi/2, 0)
    b_high.data.materials.append(mats['chassis'])
    b_high.name = f"{name}_Bullbar_Upper"

    # Push uprights
    for px in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        upright = bpy.context.active_object
        upright.parent = root
        upright.location = (px, 1.81, 0.36)
        upright.scale = (0.05, 0.07, 0.24)
        upright.data.materials.append(mats['chassis'])
        upright.name = f"{name}_Bullbar_Upright_{px}"

    # Honeycomb Front Radiator Grille
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    grille = bpy.context.active_object
    grille.parent = root
    grille.location = (0, 1.70, 0.38)
    grille.scale = (0.80, 0.05, 0.24)
    grille.data.materials.append(mats['chassis'])
    grille.name = f"{name}_FrontGrille"

    # Two Outer Rally Headlights with Glowing Cyan Halos
    for hx in [-0.46, 0.46]:
        # Casing
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.12)
        hl_case = bpy.context.active_object
        hl_case.parent = root
        hl_case.location = (hx, 1.78, 0.52)
        hl_case.rotation_euler = (math.pi/2, 0, 0)
        hl_case.data.materials.append(mats['chassis'])
        hl_case.name = f"{name}_Headlight_Casing_{hx}"

        # Chrome Lens
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.03)
        hl_lens = bpy.context.active_object
        hl_lens.parent = root
        hl_lens.location = (hx, 1.84, 0.52)
        hl_lens.rotation_euler = (math.pi/2, 0, 0)
        hl_lens.data.materials.append(mats['chrome'])
        hl_lens.name = f"{name}_Headlight_Lens_{hx}"

        # Glowing Cyan Halo Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.105, minor_radius=0.016)
        halo = bpy.context.active_object
        halo.parent = root
        halo.location = (hx, 1.86, 0.52)
        halo.rotation_euler = (math.pi/2, 0, 0)
        halo.data.materials.append(mats['neon_cyan'])
        halo.name = f"{name}_Headlight_Halo_{hx}"

        # Bright Projector Bulb
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.02)
        bulb = bpy.context.active_object
        bulb.parent = root
        bulb.location = (hx, 1.86, 0.52)
        bulb.rotation_euler = (math.pi/2, 0, 0)
        bulb.data.materials.append(mats['white'])
        bulb.name = f"{name}_Headlight_Bulb_{hx}"

    # Two Lower Central Fog Lights
    for fx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.05)
        fog = bpy.context.active_object
        fog.parent = root
        fog.location = (fx, 1.86, 0.26)
        fog.rotation_euler = (math.pi/2, 0, 0)
        fog.data.materials.append(mats['chrome'])
        fog.name = f"{name}_FogLight_{fx}"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.02)
        fog_l = bpy.context.active_object
        fog_l.parent = root
        fog_l.location = (fx, 1.89, 0.26)
        fog_l.rotation_euler = (math.pi/2, 0, 0)
        fog_l.data.materials.append(mats['white'])
        fog_l.name = f"{name}_FogLight_Lens_{fx}"

    # =========================================================================
    # 4. ANGULAR COCKPIT CANOPY & ROOF SCOOP
    # =========================================================================
    cockpit = create_angular_cockpit(f"{name}_Cockpit", mats)
    cockpit.parent = root

    # =========================================================================
    # 5. EXPOSED REAR V8 ENGINE & TWIN ROCKET THRUSTERS
    # =========================================================================
    # Engine Block (Dark Cast Iron)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    eng_block = bpy.context.active_object
    eng_block.parent = root
    eng_block.location = (0, -0.98, 0.62)
    eng_block.scale = (0.64, 0.66, 0.38)
    eng_block.data.materials.append(mats['chassis'])
    eng_block.name = f"{name}_EngineBlock"
    for p in eng_block.data.polygons: p.use_smooth = True

    # Racing Red Cylinder Valve Covers (#D32F2F)
    for ex in [-0.24, 0.24]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        v_cov = bpy.context.active_object
        v_cov.parent = root
        v_cov.location = (ex, -0.98, 0.82)
        v_cov.scale = (0.16, 0.58, 0.12)
        v_cov.rotation_euler = (0, ex * 0.45, 0)
        v_cov.data.materials.append(mats['engine_red'])
        v_cov.name = f"{name}_ValveCover_{'L' if ex > 0 else 'R'}"
        for p in v_cov.data.polygons: p.use_smooth = True

        # Chrome Ignition Conduits
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.52)
        wire = bpy.context.active_object
        wire.parent = root
        wire.location = (ex, -0.98, 0.90)
        wire.rotation_euler = (math.pi/2, 0, 0)
        wire.data.materials.append(mats['chrome'])
        wire.name = f"{name}_IgnitionConduit_{ex}"

    # 4 Chrome Intake Manifold Velocity Stacks
    for iy in [-1.16, -1.04, -0.92, -0.80]:
        for ix in [-0.08, 0.08]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.15)
            stack = bpy.context.active_object
            stack.parent = root
            stack.location = (ix, iy, 0.88)
            stack.data.materials.append(mats['chrome'])
            stack.name = f"{name}_IntakeStack_{ix}_{iy}"

    # Dual Polished Chrome Rocket Thruster Nozzles with Glowing Cyan Cores
    for tx in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.28)
        nozzle = bpy.context.active_object
        nozzle.parent = root
        nozzle.location = (tx, -1.56, 0.54)
        nozzle.rotation_euler = (math.pi/2, 0, 0)
        nozzle.data.materials.append(mats['chrome'])
        nozzle.name = f"{name}_ThrusterNozzle_{tx}"
        for p in nozzle.data.polygons: p.use_smooth = True

        bpy.ops.mesh.primitive_torus_add(major_radius=0.132, minor_radius=0.018)
        t_ring = bpy.context.active_object
        t_ring.parent = root
        t_ring.location = (tx, -1.70, 0.54)
        t_ring.rotation_euler = (math.pi/2, 0, 0)
        t_ring.data.materials.append(mats['chassis'])
        t_ring.name = f"{name}_ThrusterRing_{tx}"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.095, depth=0.18)
        core = bpy.context.active_object
        core.parent = root
        core.location = (tx, -1.66, 0.54)
        core.rotation_euler = (math.pi/2, 0, 0)
        core.data.materials.append(mats['neon_cyan'])
        core.name = f"{name}_PlasmaCore_{tx}"

    # =========================================================================
    # 6. HIGH-DOWNFORCE REAR WING
    # =========================================================================
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    wing = bpy.context.active_object
    wing.parent = root
    wing.location = (0, -1.35, 1.44)
    wing.scale = (1.56, 0.38, 0.045)
    wing.rotation_euler = (math.radians(-8), 0, 0)
    wing.data.materials.append(mats['body'])
    wing.name = f"{name}_RearWing"
    for p in wing.data.polygons: p.use_smooth = True
    bev = wing.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.012
    bev.segments = 2

    for wx in [-0.78, 0.78]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        winglet = bpy.context.active_object
        winglet.parent = root
        winglet.location = (wx, -1.35, 1.46)
        winglet.scale = (0.04, 0.44, 0.24)
        winglet.rotation_euler = (math.radians(-8), (0.18 if wx > 0 else -0.18), 0)
        winglet.data.materials.append(mats['white'])
        winglet.name = f"{name}_Winglet_{'L' if wx > 0 else 'R'}"
        for p in winglet.data.polygons: p.use_smooth = True

    for sx in [-0.34, 0.34]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=0.78)
        strut = bpy.context.active_object
        strut.parent = root
        strut.location = (sx, -1.22, 1.05)
        strut.rotation_euler = (math.radians(-24), 0, 0)
        strut.data.materials.append(mats['chassis'])
        strut.name = f"{name}_WingStrut_{sx}"

    # =========================================================================
    # 7. FOUR CHUNKY WHEELS WITH RED CALIPERS & INTEGRATED ARCHES
    # =========================================================================
    wheel_coords = [
        ("Wheel_Front_Left", 1.05, 1.08, 0.46, 0.46, 0.32, True),
        ("Wheel_Front_Right", -1.05, 1.08, 0.46, 0.46, 0.32, False),
        ("Wheel_Rear_Left", 1.12, -1.05, 0.50, 0.50, 0.35, True),
        ("Wheel_Rear_Right", -1.12, -1.05, 0.50, 0.50, 0.35, False),
    ]

    for w_name, wx, wy, wz, outer_r, width, is_left in wheel_coords:
        w_obj = build_hollow_sports_wheel(f"{name}_{w_name}", mats, outer_r=outer_r, width=width, is_left=is_left)
        w_obj.location = (wx, wy, wz)
        w_obj.parent = root

        is_rear = (wy < 0)
        f_obj = build_sculpted_fender_arch(f"{name}_Fender_{w_name}", mats, outer_r=outer_r + 0.05, width=width * 0.88, is_rear=is_rear, is_left=is_left)
        f_obj.location = (wx, wy, wz)
        f_obj.parent = root

    # Double-wishbone suspension tubular A-arms
    for sx in [-1, 1]:
        # Front Upper
        bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.52)
        fua = bpy.context.active_object
        fua.parent = root
        fua.location = (sx * 0.72, 1.08, 0.48)
        fua.rotation_euler = (0, math.pi/2, 0)
        fua.data.materials.append(mats['chassis'])
        fua.name = f"{name}_FrontUpperArm_{sx}"

        # Front Lower + Shock
        bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.52)
        fla = bpy.context.active_object
        fla.parent = root
        fla.location = (sx * 0.72, 1.08, 0.32)
        fla.rotation_euler = (0, math.pi/2, 0)
        fla.data.materials.append(mats['chassis'])
        fla.name = f"{name}_FrontLowerArm_{sx}"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.45)
        fsh = bpy.context.active_object
        fsh.parent = root
        fsh.location = (sx * 0.70, 1.08, 0.42)
        fsh.rotation_euler = (0, math.radians(sx * 35), 0)
        fsh.data.materials.append(mats['chrome'])
        fsh.name = f"{name}_FrontShock_{sx}"

        # Rear Upper
        bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.56)
        rua = bpy.context.active_object
        rua.parent = root
        rua.location = (sx * 0.78, -1.05, 0.52)
        rua.rotation_euler = (0, math.pi/2, 0)
        rua.data.materials.append(mats['chassis'])
        rua.name = f"{name}_RearUpperArm_{sx}"

        # Rear Lower + Shock
        bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.56)
        rla = bpy.context.active_object
        rla.parent = root
        rla.location = (sx * 0.78, -1.05, 0.34)
        rla.rotation_euler = (0, math.pi/2, 0)
        rla.data.materials.append(mats['chassis'])
        rla.name = f"{name}_RearLowerArm_{sx}"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.040, depth=0.48)
        rsh = bpy.context.active_object
        rsh.parent = root
        rsh.location = (sx * 0.76, -1.05, 0.45)
        rsh.rotation_euler = (0, math.radians(sx * 35), 0)
        rsh.data.materials.append(mats['chrome'])
        rsh.name = f"{name}_RearShock_{sx}"

    link_hierarchy(root, col)
    return root

def setup_studio_lighting():
    """Sets up bright daylight stadium 3-point lighting + pitch floor."""
    # Key Light (Warm daylight sun)
    key_data = bpy.data.lights.new(name="Light_Key", type='AREA')
    key_data.energy = 950.0
    key_data.size = 5.0
    key_data.color = (1.0, 0.97, 0.92)
    key_obj = bpy.data.objects.new("Light_Key", key_data)
    key_obj.location = (4.8, 4.4, 5.2)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-42))
    bpy.context.scene.collection.objects.link(key_obj)

    # Fill Light (Cool sky blue fill)
    fill_data = bpy.data.lights.new(name="Light_Fill", type='AREA')
    fill_data.energy = 500.0
    fill_data.size = 6.0
    fill_data.color = (0.75, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
    fill_obj.location = (-5.0, 3.4, 3.8)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-15), math.radians(45))
    bpy.context.scene.collection.objects.link(fill_obj)

    # Rim / Backlight
    rim_data = bpy.data.lights.new(name="Light_Rim", type='AREA')
    rim_data.energy = 850.0
    rim_data.size = 4.0
    rim_data.color = (1.0, 0.70, 0.40)
    rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
    rim_obj.location = (0.0, -5.4, 4.2)
    rim_obj.rotation_euler = (math.radians(-55), 0, math.radians(180))
    bpy.context.scene.collection.objects.link(rim_obj)

    # Stadium Sun Light for high-gloss metallic paint highlights
    sun_data = bpy.data.lights.new(name="Light_Sun", type='SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.angle = math.radians(8)
    sun_obj = bpy.data.objects.new("Light_Sun", sun_data)
    sun_obj.rotation_euler = (math.radians(52), math.radians(16), math.radians(-38))
    bpy.context.scene.collection.objects.link(sun_obj)

    # Ground Studio Turf Pitch Floor
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Stadium_Pitch_Floor"
    m_floor = get_or_create_material('Mat_StadiumFloor')
    nt = m_floor.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.10, 0.06, 1.0) # Rich pitch green
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Metallic'].default_value = 0.08
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    floor.data.materials.append(m_floor)

    # White Field Sideline
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -0.6, 0.003))
    line = bpy.context.active_object
    line.scale = (28.0, 0.18, 1.0)
    m_line = get_or_create_material('Mat_PitchLine')
    nt = m_line.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.94, 0.96, 0.98, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    line.data.materials.append(m_line)

def setup_camera():
    """Sets up camera with 3/4 beauty perspective matching media_1790263831226.png with full car in view."""
    cam_data = bpy.data.cameras.new(name="Camera_BlueprintView")
    cam_data.lens = 50.0
    cam_obj = bpy.data.objects.new("Camera_BlueprintView", cam_data)
    cam_obj.location = (3.8, 4.2, 2.05)
    direction = Vector((0, 0.08, 0.68)) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    return cam_obj

def render_scene(filepath, resolution=(1280, 720), samples=32):
    """Renders the scene with high quality Cycles CPU and saves to filepath."""
    scene = bpy.context.scene
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.filepath = os.path.abspath(filepath)
    
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
            
    print(f"Rendering blueprint beauty shot to {scene.render.filepath}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render complete: {scene.render.filepath}")

def main():
    print("=== BUILDING AUTHENTIC 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    car_col = make_collection("RocketLeague_Octane_Car")
    mats = setup_materials()
    car = build_authentic_octane(car_col, mats, name="Octane_Championship")
    setup_studio_lighting()
    setup_camera()
    
    # Save standalone .blend file
    blend_path = os.path.abspath("rocket_league_car.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved standalone car scene to {blend_path}")
    
    # Render beauty shot
    render_path = os.path.abspath("blueprint_car_render.png")
    render_scene(render_path)

if __name__ == '__main__':
    main()
