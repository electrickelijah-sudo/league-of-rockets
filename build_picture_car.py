"""
Procedural 1:1 Reference Blueprint Car Builder for Blender 5.x.
Builds the exact Rocket League style car shown in media_1790263831226.png:
- Cobalt Blue Metallic body (#0052F5)
- Continuous Dual Alpine White Racing Stripes with Cyan Pinstripe Borders
- Titanium White Trim on A-pillars, fender arch lips, and spoiler winglets
- Sleek aerodynamic arched fenders (NOT bulky boxes)
- Open dune-buggy stance with exposed double-wishbone suspension & coilover shocks
- Deep-dish 10-spoke gunmetal alloy wheels, hollow treaded rubber tires, red brake calipers
- Front tubular bullbar with 4 projector headlights (cyan glowing halos + fog lights)
- Raked tinted cockpit glass canopy with black dual-port roof scoop
- Exposed rear V8 engine with bright racing red cylinder heads (#D32F2F) and chrome intake horns
- Dual chrome rocket thruster nozzles with glowing cyan plasma cores
- High-downforce rear wing with white endplates
- Dual red LED taillights & subtle neon rocker accent tubes
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

def make_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat

def setup_materials():
    mats = {}

    # 1. Cobalt Blue Metallic with Dual Racing Stripe Livery
    m_body = get_or_create_material('Mat_Blueprint_CobaltBlueLivery')
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
        
    bsdf.inputs['Metallic'].default_value = 0.82
    bsdf.inputs['Roughness'].default_value = 0.24
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.70
        bsdf.inputs['Coat Roughness'].default_value = 0.06
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['body'] = m_body

    # 2. Titanium White Trim (#FFFFFF) for A-pillars, fender arch lips, winglets
    m_white = get_or_create_material('Mat_Blueprint_TitaniumWhite')
    nt = m_white.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.20
    bsdf.inputs['Roughness'].default_value = 0.18
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.60
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['white'] = m_white

    # 3. Dark Metallic Chassis & Bullbar
    m_chassis = get_or_create_material('Mat_Blueprint_Chassis')
    nt = m_chassis.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.06, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.28
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['chassis'] = m_chassis

    # 4. Racing Red Engine Cylinder Heads (#D32F2F) & Brake Calipers
    m_red = get_or_create_material('Mat_Blueprint_EngineRed')
    nt = m_red.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.86, 0.05, 0.07, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.45
    bsdf.inputs['Roughness'].default_value = 0.20
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['engine_red'] = m_red

    # 5. Polished Chrome (Pipes, Nozzles, Bumper Highlights, Hub Nut)
    m_chrome = get_or_create_material('Mat_Blueprint_Chrome')
    nt = m_chrome.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.05
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['chrome'] = m_chrome

    # 6. Tinted Aerodynamic Cockpit Glass
    m_glass = get_or_create_material('Mat_Blueprint_Glass')
    nt = m_glass.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.04, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value = 0.35
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.65
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.65
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['glass'] = m_glass

    # 7. Gunmetal Christiano Alloy Wheels
    m_wheel = get_or_create_material('Mat_Blueprint_WheelAlloy')
    nt = m_wheel.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.15, 0.16, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.20
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['wheel_alloy'] = m_wheel

    # 8. Deep-Tread Matte Rubber Tires
    m_tire = get_or_create_material('Mat_Blueprint_TireRubber')
    nt = m_tire.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.02
    bsdf.inputs['Roughness'].default_value = 0.80
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['tire'] = m_tire

    # 9. Drilled Steel Brake Rotor Disc
    m_rotor = get_or_create_material('Mat_Blueprint_BrakeRotor')
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
    m_neon = get_or_create_material('Mat_Blueprint_NeonCyan')
    nt = m_neon.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.0, 0.90, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.0, 0.90, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 14.0
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['neon_cyan'] = m_neon

    # 11. Glowing Red Taillight
    m_tail = get_or_create_material('Mat_Blueprint_TailRed')
    nt = m_tail.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.04, 0.04, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.04, 0.04, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 10.0
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['tail_red'] = m_tail

    return mats

def link_hierarchy(obj, col):
    """Recursively links an object and all its children into the target collection."""
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects and bpy.context.scene.collection != col:
        try:
            bpy.context.scene.collection.objects.unlink(obj)
        except Exception:
            pass
    for child in obj.children:
        link_hierarchy(child, col)

def create_sculpted_hood(name, mat):
    """Creates the aerodynamic sloped sports hood with UV mapping for racing stripes."""
    profiles = [
        # py, half_w_belt, z_belt, half_w_ridge, z_ridge, z_center
        (1.68, 0.34, 0.36, 0.22, 0.38, 0.37),
        (1.44, 0.39, 0.42, 0.26, 0.46, 0.44),
        (1.15, 0.44, 0.50, 0.30, 0.56, 0.54),
        (0.85, 0.49, 0.58, 0.34, 0.66, 0.64),
        (0.65, 0.54, 0.66, 0.38, 0.74, 0.72),
        (0.50, 0.57, 0.72, 0.41, 0.80, 0.78)
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    grid_verts = []
    num_stations = len(profiles)
    for s_idx, (py, w_belt, z_belt, w_ridge, z_ridge, z_center) in enumerate(profiles):
        row = [
            bm.verts.new(Vector((-w_belt, py, z_belt))),
            bm.verts.new(Vector((-w_ridge, py, z_ridge))),
            bm.verts.new(Vector((0.0, py, z_center))),
            bm.verts.new(Vector((w_ridge, py, z_ridge))),
            bm.verts.new(Vector((w_belt, py, z_belt)))
        ]
        grid_verts.append(row)

    # UV layout: center is u=0.5, stations go from v=0.9 down to v=0.4
    u_vals = [0.10, 0.35, 0.50, 0.65, 0.90]
    for s in range(num_stations - 1):
        v_start = 0.90 - (s / (num_stations - 1)) * 0.50
        v_end = 0.90 - ((s + 1) / (num_stations - 1)) * 0.50
        for c in range(4):
            v0 = grid_verts[s][c]
            v1 = grid_verts[s][c+1]
            v2 = grid_verts[s+1][c+1]
            v3 = grid_verts[s+1][c]
            face = bm.faces.new((v0, v1, v2, v3))
            for loop in face.loops:
                if loop.vert == v0: loop[uv_layer].uv = (u_vals[c], v_start)
                elif loop.vert == v1: loop[uv_layer].uv = (u_vals[c+1], v_start)
                elif loop.vert == v2: loop[uv_layer].uv = (u_vals[c+1], v_end)
                elif loop.vert == v3: loop[uv_layer].uv = (u_vals[c], v_end)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.015
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    return obj

def create_sleek_fender_arch(name, mats, is_rear=False, is_left=True):
    """
    Creates a sleek aerodynamic curved arch flare that sits snugly OVER the tire.
    """
    x_sign = 1.0 if is_left else -1.0
    center_y = -1.05 if is_rear else 1.08
    center_x = x_sign * (1.14 if is_rear else 1.05)
    center_z = 0.46 if is_rear else 0.42

    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.location = (center_x, center_y, center_z)

    outer_r = 0.52 if is_rear else 0.48
    width = 0.24
    arc_pts = 9
    start_deg = 35.0
    end_deg = 145.0

    # 1. Main Arch (Cobalt Blue)
    mesh = bpy.data.meshes.new(f"{name}_ArchMesh")
    bm = bmesh.new()

    inner_verts = []
    outer_verts = []
    for i in range(arc_pts):
        t = i / (arc_pts - 1)
        ang = math.radians(start_deg + t * (end_deg - start_deg))
        y = math.cos(ang) * outer_r
        z = math.sin(ang) * outer_r

        v_in = bm.verts.new(Vector((-width * 0.5 * x_sign, y, z)))
        v_out = bm.verts.new(Vector((width * 0.5 * x_sign, y, z)))
        inner_verts.append(v_in)
        outer_verts.append(v_out)

    for i in range(arc_pts - 1):
        v0 = inner_verts[i]
        v1 = outer_verts[i]
        v2 = outer_verts[i+1]
        v3 = inner_verts[i+1]
        bm.faces.new((v0, v1, v2, v3))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    cowl = bpy.data.objects.new(f"{name}_Arch", mesh)
    cowl.location = (0, 0, 0)
    cowl.data.materials.append(mats['body'])
    for poly in cowl.data.polygons:
        poly.use_smooth = True
    cowl.parent = root

    bev = cowl.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.012
    bev.segments = 2

    # 2. Titanium White Outer Arch Lip
    lip_mesh = bpy.data.meshes.new(f"{name}_LipMesh")
    bm_lip = bmesh.new()
    lip_r = outer_r + 0.015
    lip_w = 0.05
    l_in, l_out = [], []
    for i in range(arc_pts):
        t = i / (arc_pts - 1)
        ang = math.radians(start_deg + t * (end_deg - start_deg))
        y = math.cos(ang) * lip_r
        z = math.sin(ang) * lip_r
        v0 = bm_lip.verts.new(Vector((0.0, y, z)))
        v1 = bm_lip.verts.new(Vector((x_sign * lip_w, y, z - 0.03)))
        l_in.append(v0)
        l_out.append(v1)

    for i in range(arc_pts - 1):
        bm_lip.faces.new((l_in[i], l_out[i], l_out[i+1], l_in[i+1]))

    bmesh.ops.recalc_face_normals(bm_lip, faces=bm_lip.faces)
    bm_lip.to_mesh(lip_mesh)
    bm_lip.free()

    lip = bpy.data.objects.new(f"{name}_Lip", lip_mesh)
    lip.location = (x_sign * (width * 0.48), 0, 0)
    lip.data.materials.append(mats['white'])
    for poly in lip.data.polygons:
        poly.use_smooth = True
    lip.parent = root

    # 3. Inward Body Fender Mount Bracket
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    mount = bpy.context.active_object
    mount.parent = root
    mount.location = (-x_sign * 0.16, 0, 0.20)
    mount.scale = (0.24, 0.26, 0.05)
    mount.data.materials.append(mats['body'])
    mount.name = f"{name}_Mount"

    # 4. Rear Red LED Taillight Strip on Rear Fender
    if is_rear:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.08)
        tl = bpy.context.active_object
        tl.parent = root
        tl.location = (0, -0.40, 0.25)
        tl.rotation_euler = (math.pi/2, 0, 0)
        tl.data.materials.append(mats['tail_red'])
        tl.name = f"{name}_TailLight"

    return root

def create_hollow_tire_mesh(name, outer_r=0.45, inner_r=0.28, width=0.30):
    """
    Creates an authentic sports tire with hollow center for deep-dish alloy rim,
    curved sidewalls, and flat tread face.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    profile = [
        (-width * 0.42, inner_r),        # Inner rim bead
        (-width * 0.50, (inner_r + outer_r) * 0.52), # Inner sidewall bulge
        (-width * 0.46, outer_r - 0.02), # Inner shoulder
        (-width * 0.32, outer_r),        # Tread inner
        (0.0, outer_r),                  # Tread center
        (width * 0.32, outer_r),         # Tread outer
        (width * 0.46, outer_r - 0.02),  # Outer shoulder
        (width * 0.50, (inner_r + outer_r) * 0.52),  # Outer sidewall bulge
        (width * 0.42, inner_r)          # Outer rim bead
    ]

    segments = 24
    rings = []
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        ring_verts = []
        for x_off, r in profile:
            v = bm.verts.new(Vector((x_off, cos_a * r, sin_a * r)))
            ring_verts.append(v)
        rings.append(ring_verts)

    p_len = len(profile)
    for s in range(segments):
        next_s = (s + 1) % segments
        for p in range(p_len - 1):
            v0 = rings[s][p]
            v1 = rings[next_s][p]
            v2 = rings[next_s][p + 1]
            v3 = rings[s][p + 1]
            bm.faces.new((v0, v1, v2, v3))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_detailed_wheel(name, mats, outer_r=0.45, width=0.30, is_left=True):
    """
    Builds 10-spoke gunmetal Christiano alloy wheel with deep-dish rim,
    hollow rubber racing tire, drilled steel brake rotor, and racing red brake caliper.
    """
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    face_dir = 1.0 if is_left else -1.0
    inner_rim_r = 0.28

    # 1. Hollow Rubber Tire
    t_mesh = create_hollow_tire_mesh(f"{name}_TireMesh", outer_r=outer_r, inner_r=inner_rim_r, width=width)
    tire = bpy.data.objects.new(f"{name}_Tire", t_mesh)
    tire.data.materials.append(mats['tire'])
    for poly in tire.data.polygons:
        poly.use_smooth = True
    tire.parent = root

    # 2. Deep-Dish Gunmetal Outer Rim Ring
    rim_outer_x = face_dir * (width * 0.42)
    bpy.ops.mesh.primitive_torus_add(major_radius=inner_rim_r + 0.015, minor_radius=0.022, location=(rim_outer_x, 0, 0))
    rim = bpy.context.active_object
    rim.rotation_euler = (0, math.pi/2, 0)
    rim.data.materials.append(mats['wheel_alloy'])
    rim.name = f"{name}_RimBezel"
    rim.parent = root
    for poly in rim.data.polygons:
        poly.use_smooth = True

    # 3. Recessed Inner Rim Barrel (Steps inwards 0.06m)
    rim_depth = 0.16
    barrel_x = face_dir * (width * 0.42 - rim_depth * 0.5)
    bpy.ops.mesh.primitive_cylinder_add(radius=inner_rim_r, depth=rim_depth, location=(barrel_x, 0, 0), end_fill_type='NOTHING')
    barrel = bpy.context.active_object
    barrel.rotation_euler = (0, math.pi/2, 0)
    barrel.data.materials.append(mats['wheel_alloy'])
    barrel.name = f"{name}_RimBarrel"
    barrel.parent = root
    for poly in barrel.data.polygons:
        poly.use_smooth = True

    # 4. 10 Sleek Gunmetal Alloy Spokes (Recessed inside the deep-dish rim)
    spoke_x = face_dir * (width * 0.42 - 0.05)
    for s_idx in range(10):
        ang = s_idx * (2.0 * math.pi / 10.0)
        sy = math.cos(ang) * (inner_rim_r * 0.52)
        sz = math.sin(ang) * (inner_rim_r * 0.52)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(spoke_x, sy, sz))
        spoke = bpy.context.active_object
        spoke.scale = (0.022, 0.038, inner_rim_r * 0.88)
        spoke.rotation_euler = (ang, 0, 0)
        spoke.data.materials.append(mats['wheel_alloy'])
        spoke.name = f"{name}_Spoke_{s_idx}"
        spoke.parent = root
        for poly in spoke.data.polygons:
            poly.use_smooth = True

    # 5. Polished Chrome Center Hub Cap
    hub_x = face_dir * (width * 0.42 - 0.035)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.04, location=(hub_x, 0, 0))
    hub = bpy.context.active_object
    hub.rotation_euler = (0, math.pi/2, 0)
    hub.data.materials.append(mats['chrome'])
    hub.name = f"{name}_Hub"
    hub.parent = root

    # 6. Steel Brake Rotor Disc (Visible behind spokes)
    rotor_x = face_dir * (width * 0.42 - 0.11)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.23, depth=0.016, location=(rotor_x, 0, 0))
    rotor = bpy.context.active_object
    rotor.rotation_euler = (0, math.pi/2, 0)
    rotor.data.materials.append(mats['rotor'])
    rotor.name = f"{name}_BrakeRotor"
    rotor.parent = root

    # 7. Racing Red Brake Caliper Clamping the Rotor
    caliper_x = face_dir * (width * 0.42 - 0.10)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(caliper_x, 0.15, 0.14))
    caliper = bpy.context.active_object
    caliper.scale = (0.05, 0.12, 0.09)
    caliper.rotation_euler = (-0.6, 0, 0)
    caliper.data.materials.append(mats['engine_red'])
    caliper.name = f"{name}_BrakeCaliper"
    caliper.parent = root
    bev = caliper.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.008
    bev.segments = 2

    return root

def build_suspension_arm(name, mats, start_pt, end_pt, is_upper=False):
    """Builds tubular suspension wishbone arm and coilover shock spring."""
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    start_v = Vector(start_pt)
    end_v = Vector(end_pt)
    mid_v = (start_v + end_v) * 0.5
    vec = end_v - start_v
    length = vec.length

    # Tubular arm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=length, location=mid_v)
    arm = bpy.context.active_object
    rot_quat = vec.to_track_quat('Z', 'Y')
    arm.rotation_euler = rot_quat.to_euler()
    arm.data.materials.append(mats['chassis'])
    arm.name = f"{name}_Arm"
    arm.parent = root

    # Coilover Shock Damper on lower arms
    if not is_upper:
        shock_mid = (start_v * 0.35 + end_v * 0.65) + Vector((0, 0, 0.12))
        shock_vec = (end_v - Vector((start_v.x, start_v.y, start_v.z + 0.22)))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=shock_vec.length * 0.85, location=shock_mid)
        damper = bpy.context.active_object
        damper.rotation_euler = shock_vec.to_track_quat('Z', 'Y').to_euler()
        damper.data.materials.append(mats['chrome'])
        damper.name = f"{name}_ShockDamper"
        damper.parent = root

    return root

def build_picture_car(col, mats, name="Championship_Octane", location=(0, 0, 0), rotation=(0, 0, 0)):
    """Builds the 1:1 Reference Blueprint Car in Blender."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    root = bpy.context.active_object
    root.name = name
    root.rotation_euler = rotation

    def attach_simple(child):
        child.parent = root
        return child

    # =========================================================================
    # 1. SCULPTED CONTINUOUS HOOD (Cobalt Blue with Dual White Stripes)
    # =========================================================================
    hood = create_sculpted_hood(f"{name}_Hood", mats['body'])
    attach_simple(hood)

    # Titanium White Chamfer Flanks along Hood Edges
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 0.45, 1.15, 0.58))
        chamf = bpy.context.active_object
        chamf.scale = (0.08, 0.70, 0.04)
        chamf.rotation_euler = (-0.22, sx * 0.32, 0)
        chamf.data.materials.append(mats['white'])
        chamf.name = f"{name}_HoodTrim_{'L' if sx > 0 else 'R'}"
        for poly in chamf.data.polygons: poly.use_smooth = True
        attach_simple(chamf)

    # =========================================================================
    # 2. FRONT PUSHBAR / BULLBAR WITH 4 PROJECTOR LIGHTS & CYAN HALOS
    # =========================================================================
    # Lower crossbar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=1.12, location=(0, 1.82, 0.25))
    bar_low = bpy.context.active_object
    bar_low.rotation_euler = (0, math.pi/2, 0)
    bar_low.data.materials.append(mats['chassis'])
    bar_low.name = f"{name}_Bullbar_Lower"
    attach_simple(bar_low)

    # Upper crossbar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.96, location=(0, 1.76, 0.44))
    bar_high = bpy.context.active_object
    bar_high.rotation_euler = (0, math.pi/2, 0)
    bar_high.data.materials.append(mats['chassis'])
    bar_high.name = f"{name}_Bullbar_Upper"
    attach_simple(bar_high)

    # Vertical push uprights
    for px in [-0.34, 0.34]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 1.80, 0.34))
        upright = bpy.context.active_object
        upright.scale = (0.05, 0.07, 0.26)
        upright.data.materials.append(mats['chassis'])
        upright.name = f"{name}_Bullbar_Upright_{px}"
        attach_simple(upright)

    # Two Outer Rally Projector Headlights with Glowing Cyan Halo Rings
    for hx in [-0.46, 0.46]:
        # Casing
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.12, location=(hx, 1.76, 0.50))
        hl_case = bpy.context.active_object
        hl_case.rotation_euler = (math.pi/2, 0, 0)
        hl_case.data.materials.append(mats['chassis'])
        hl_case.name = f"{name}_Headlight_Casing_{hx}"
        attach_simple(hl_case)

        # Chrome Lens
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.03, location=(hx, 1.82, 0.50))
        hl_lens = bpy.context.active_object
        hl_lens.rotation_euler = (math.pi/2, 0, 0)
        hl_lens.data.materials.append(mats['chrome'])
        hl_lens.name = f"{name}_Headlight_Lens_{hx}"
        attach_simple(hl_lens)

        # Glowing Cyan Halo Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.105, minor_radius=0.016, location=(hx, 1.84, 0.50))
        halo = bpy.context.active_object
        halo.rotation_euler = (math.pi/2, 0, 0)
        halo.data.materials.append(mats['neon_cyan'])
        halo.name = f"{name}_Headlight_Halo_{hx}"
        attach_simple(halo)

        # Bright White Projector Center Bulb
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.02, location=(hx, 1.84, 0.50))
        bulb = bpy.context.active_object
        bulb.rotation_euler = (math.pi/2, 0, 0)
        bulb.data.materials.append(mats['white'])
        bulb.name = f"{name}_Headlight_Bulb_{hx}"
        attach_simple(bulb)

    # Two Lower Central Fog Lights
    for fx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.05, location=(fx, 1.84, 0.25))
        fog = bpy.context.active_object
        fog.rotation_euler = (math.pi/2, 0, 0)
        fog.data.materials.append(mats['chrome'])
        fog.name = f"{name}_FogLight_{fx}"
        attach_simple(fog)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.02, location=(fx, 1.87, 0.25))
        fog_l = bpy.context.active_object
        fog_l.rotation_euler = (math.pi/2, 0, 0)
        fog_l.data.materials.append(mats['white'])
        fog_l.name = f"{name}_FogLight_Lens_{fx}"
        attach_simple(fog_l)

    # Honeycomb / Hex Front Radiator Grille
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.68, 0.38))
    grille = bpy.context.active_object
    grille.scale = (0.78, 0.05, 0.24)
    grille.data.materials.append(mats['chassis'])
    grille.name = f"{name}_FrontGrille"
    attach_simple(grille)

    # =========================================================================
    # 3. RAKED TINTED WINDSHIELD & TITANIUM WHITE A-PILLARS
    # =========================================================================
    # Windshield Glass (42° Rake)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.22, 0.94))
    windshield = bpy.context.active_object
    windshield.scale = (0.84, 0.56, 0.03)
    windshield.rotation_euler = (math.radians(-42), 0, 0)
    windshield.data.materials.append(mats['glass'])
    windshield.name = f"{name}_Windshield"
    attach_simple(windshield)

    # Titanium White Structural A-Pillars flanking windshield
    for px in [-0.43, 0.43]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.22, 0.94))
        pillar = bpy.context.active_object
        pillar.scale = (0.07, 0.60, 0.05)
        pillar.rotation_euler = (math.radians(-42), 0, 0)
        pillar.data.materials.append(mats['white'])
        pillar.name = f"{name}_APillar_{'L' if px > 0 else 'R'}"
        for poly in pillar.data.polygons: poly.use_smooth = True
        bev = pillar.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.01
        bev.segments = 2
        attach_simple(pillar)

    # Low-Profile Sports Roof (Cobalt Blue with Dual Stripes)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, 1.15))
    roof = bpy.context.active_object
    roof.scale = (0.80, 0.50, 0.04)
    roof.data.materials.append(mats['body'])
    roof.name = f"{name}_Roof"
    for poly in roof.data.polygons: poly.use_smooth = True
    bev = roof.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.015
    bev.segments = 2
    attach_simple(roof)

    # Titanium White Roof Side Rails
    for rx in [-0.41, 0.41]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, -0.22, 1.15))
        rail = bpy.context.active_object
        rail.scale = (0.045, 0.52, 0.045)
        rail.data.materials.append(mats['white'])
        rail.name = f"{name}_RoofRail_{'L' if rx > 0 else 'R'}"
        for poly in rail.data.polygons: poly.use_smooth = True
        attach_simple(rail)

    # Side Window Glass
    for wx in [-0.40, 0.40]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -0.18, 0.95))
        swin = bpy.context.active_object
        swin.scale = (0.02, 0.46, 0.30)
        swin.data.materials.append(mats['glass'])
        swin.name = f"{name}_SideWindow_{'L' if wx > 0 else 'R'}"
        attach_simple(swin)

    # Black Aerodynamic Roof Air Intake Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.18, 1.23))
    r_scoop = bpy.context.active_object
    r_scoop.scale = (0.34, 0.32, 0.08)
    r_scoop.rotation_euler = (math.radians(6), 0, 0)
    r_scoop.data.materials.append(mats['chassis'])
    r_scoop.name = f"{name}_RoofAirScoop"
    for poly in r_scoop.data.polygons: poly.use_smooth = True
    attach_simple(r_scoop)

    # Dual scoop intake nostrils (front of scoop)
    for sx in [-0.09, 0.09]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.01, 1.23))
        nostril = bpy.context.active_object
        nostril.scale = (0.09, 0.03, 0.045)
        nostril.data.materials.append(mats['chassis'])
        nostril.name = f"{name}_ScoopNostril_{sx}"
        attach_simple(nostril)

    # =========================================================================
    # 4. CHASSIS TUB & SCULPTED SIDE ROCKERS WITH NEON ACCENTS
    # =========================================================================
    # Main Lower Chassis Plate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.32))
    tub = bpy.context.active_object
    tub.scale = (0.90, 2.70, 0.22)
    tub.data.materials.append(mats['chassis'])
    tub.name = f"{name}_ChassisTub"
    for poly in tub.data.polygons: poly.use_smooth = True
    attach_simple(tub)

    # Sculpted Side Pods (Cobalt Blue flanks)
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 0.58, -0.10, 0.44))
        pod = bpy.context.active_object
        pod.scale = (0.24, 1.45, 0.32)
        pod.data.materials.append(mats['body'])
        pod.name = f"{name}_SidePod_{'L' if sx > 0 else 'R'}"
        for poly in pod.data.polygons: poly.use_smooth = True
        bev = pod.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.02
        bev.segments = 2
        attach_simple(pod)

        # Titanium White lower accent runner
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx * 0.70, -0.10, 0.30))
        runner = bpy.context.active_object
        runner.scale = (0.04, 1.40, 0.04)
        runner.data.materials.append(mats['white'])
        runner.name = f"{name}_SideRockerRunner_{'L' if sx > 0 else 'R'}"
        attach_simple(runner)

        # Subtle thin neon cyan rocker light tube (sleek underglow accent)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=1.35, location=(sx * 0.68, -0.10, 0.24))
        neon_tube = bpy.context.active_object
        neon_tube.rotation_euler = (math.pi/2, 0, 0)
        neon_tube.data.materials.append(mats['neon_cyan'])
        neon_tube.name = f"{name}_NeonTube_{'L' if sx > 0 else 'R'}"
        attach_simple(neon_tube)

    # =========================================================================
    # 5. EXPOSED REAR V8 ENGINE & TWIN ROCKET THRUSTERS
    # =========================================================================
    # Engine Block (Dark Cast Iron)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.92, 0.58))
    eng_block = bpy.context.active_object
    eng_block.scale = (0.64, 0.66, 0.38)
    eng_block.data.materials.append(mats['chassis'])
    eng_block.name = f"{name}_EngineBlock"
    for poly in eng_block.data.polygons: poly.use_smooth = True
    attach_simple(eng_block)

    # Racing Red Cylinder Valve Covers (#D32F2F)
    for ex in [-0.24, 0.24]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.92, 0.78))
        v_cov = bpy.context.active_object
        v_cov.scale = (0.16, 0.58, 0.12)
        v_cov.rotation_euler = (0, ex * 0.45, 0)
        v_cov.data.materials.append(mats['engine_red'])
        v_cov.name = f"{name}_ValveCover_{'L' if ex > 0 else 'R'}"
        for poly in v_cov.data.polygons: poly.use_smooth = True
        attach_simple(v_cov)

        # Chrome Ignition Wire Conduits
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.52, location=(ex, -0.92, 0.86))
        wire = bpy.context.active_object
        wire.rotation_euler = (math.pi/2, 0, 0)
        wire.data.materials.append(mats['chrome'])
        wire.name = f"{name}_IgnitionConduit_{ex}"
        attach_simple(wire)

    # 4 Chrome Intake Manifold Velocity Stacks (Center V of engine)
    for iy in [-1.10, -0.98, -0.86, -0.74]:
        for ix in [-0.08, 0.08]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.14, location=(ix, iy, 0.84))
            stack = bpy.context.active_object
            stack.data.materials.append(mats['chrome'])
            stack.name = f"{name}_IntakeStack_{ix}_{iy}"
            attach_simple(stack)

    # Dual Polished Chrome Rocket Thruster Nozzles with Glowing Cyan Cores
    for tx in [-0.22, 0.22]:
        # Outer Chrome Nozzle
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.28, location=(tx, -1.48, 0.52))
        nozzle = bpy.context.active_object
        nozzle.rotation_euler = (math.pi/2, 0, 0)
        nozzle.data.materials.append(mats['chrome'])
        nozzle.name = f"{name}_ThrusterNozzle_{tx}"
        for poly in nozzle.data.polygons: poly.use_smooth = True
        attach_simple(nozzle)

        # Heat Shield Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.132, minor_radius=0.018, location=(tx, -1.62, 0.52))
        t_ring = bpy.context.active_object
        t_ring.rotation_euler = (math.pi/2, 0, 0)
        t_ring.data.materials.append(mats['chassis'])
        t_ring.name = f"{name}_ThrusterRing_{tx}"
        attach_simple(t_ring)

        # Glowing Cyan Plasma Flame Exhaust Core
        bpy.ops.mesh.primitive_cylinder_add(radius=0.095, depth=0.18, location=(tx, -1.58, 0.52))
        core = bpy.context.active_object
        core.rotation_euler = (math.pi/2, 0, 0)
        core.data.materials.append(mats['neon_cyan'])
        core.name = f"{name}_PlasmaCore_{tx}"
        attach_simple(core)

    # =========================================================================
    # 6. HIGH-DOWNFORCE REAR WING (Cobalt Blue, Dual Stripes, White Winglets)
    # =========================================================================
    # Main Aerofoil Wing Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.28, 1.34))
    wing = bpy.context.active_object
    wing.scale = (1.52, 0.38, 0.045)
    wing.rotation_euler = (math.radians(-8), 0, 0)
    wing.data.materials.append(mats['body'])
    wing.name = f"{name}_RearWing"
    for poly in wing.data.polygons: poly.use_smooth = True
    bev = wing.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.012
    bev.segments = 2
    attach_simple(wing)

    # Titanium White Winglet Endplates (Canted outwards)
    for wx in [-0.76, 0.76]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -1.28, 1.36))
        winglet = bpy.context.active_object
        winglet.scale = (0.04, 0.42, 0.22)
        winglet.rotation_euler = (math.radians(-8), (0.18 if wx > 0 else -0.18), 0)
        winglet.data.materials.append(mats['white'])
        winglet.name = f"{name}_Winglet_{'L' if wx > 0 else 'R'}"
        for poly in winglet.data.polygons: poly.use_smooth = True
        bev = winglet.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.01
        bev.segments = 2
        attach_simple(winglet)

    # Dual Aerodynamic Wing Struts (Chassis to Wing)
    for sx in [-0.34, 0.34]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.72, location=(sx, -1.15, 0.98))
        strut = bpy.context.active_object
        strut.rotation_euler = (math.radians(-24), 0, 0)
        strut.data.materials.append(mats['chassis'])
        strut.name = f"{name}_WingStrut_{sx}"
        attach_simple(strut)

    # =========================================================================
    # 7. SLEEK CURVED FENDER ARCHES (Over tires)
    # =========================================================================
    f_configs = [
        ("Fender_Front_Left", False, True),
        ("Fender_Front_Right", False, False),
        ("Fender_Rear_Left", True, True),
        ("Fender_Rear_Right", True, False),
    ]
    for f_name, is_rear, is_left in f_configs:
        f_obj = create_sleek_fender_arch(f"{name}_{f_name}", mats, is_rear=is_rear, is_left=is_left)
        f_obj.parent = root

    # =========================================================================
    # 8. EXPOSED DOUBLE-WISHBONE SUSPENSION SYSTEM
    # =========================================================================
    for sx in [-1, 1]:
        # Front Upper Arm
        u_start = (sx * 0.44, 1.08, 0.46)
        u_end = (sx * 0.92, 1.08, 0.44)
        u_arm = build_suspension_arm(f"{name}_FrontUpperArm_{sx}", mats, u_start, u_end, is_upper=True)
        u_arm.parent = root

        # Front Lower Arm + Shock Damper
        l_start = (sx * 0.42, 1.08, 0.28)
        l_end = (sx * 0.92, 1.08, 0.28)
        l_arm = build_suspension_arm(f"{name}_FrontLowerArm_{sx}", mats, l_start, l_end, is_upper=False)
        l_arm.parent = root

        # Rear Upper Arm
        ru_start = (sx * 0.48, -1.05, 0.50)
        ru_end = (sx * 1.00, -1.05, 0.48)
        ru_arm = build_suspension_arm(f"{name}_RearUpperArm_{sx}", mats, ru_start, ru_end, is_upper=True)
        ru_arm.parent = root

        # Rear Lower Arm + Shock Damper
        rl_start = (sx * 0.46, -1.05, 0.30)
        rl_end = (sx * 1.00, -1.05, 0.30)
        rl_arm = build_suspension_arm(f"{name}_RearLowerArm_{sx}", mats, rl_start, rl_end, is_upper=False)
        rl_arm.parent = root

    # =========================================================================
    # 9. 4 DETAILED DEEP-DISH ALLOY WHEELS WITH RED BRAKE CALIPERS
    # =========================================================================
    wheel_data = [
        ("Wheel_Front_Left", 1.05, 1.08, 0.42, 0.42, 0.28, True),
        ("Wheel_Front_Right", -1.05, 1.08, 0.42, 0.42, 0.28, False),
        ("Wheel_Rear_Left", 1.14, -1.05, 0.46, 0.46, 0.32, True),
        ("Wheel_Rear_Right", -1.14, -1.05, 0.46, 0.46, 0.32, False),
    ]
    for w_name, wx, wy, wz, outer_r, w_width, is_left in wheel_data:
        w_obj = build_detailed_wheel(f"{name}_{w_name}", mats, outer_r=outer_r, width=w_width, is_left=is_left)
        w_obj.location = (wx, wy, wz)
        w_obj.parent = root

    # Recursively ensure the entire hierarchy is linked to car_col
    link_hierarchy(root, col)

    return root

def setup_studio_lighting():
    """Sets up vibrant stadium / studio 3-point lighting to reveal all car details."""
    # Key Light (Warm daylight stadium sun)
    key_data = bpy.data.lights.new(name="Light_Key", type='AREA')
    key_data.energy = 900.0
    key_data.size = 5.0
    key_data.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("Light_Key", key_data)
    key_obj.location = (4.5, 4.2, 5.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-42))
    bpy.context.scene.collection.objects.link(key_obj)

    # Fill Light (Cool sky fill)
    fill_data = bpy.data.lights.new(name="Light_Fill", type='AREA')
    fill_data.energy = 450.0
    fill_data.size = 6.0
    fill_data.color = (0.75, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
    fill_obj.location = (-4.8, 3.2, 3.5)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-15), math.radians(45))
    bpy.context.scene.collection.objects.link(fill_obj)

    # Rim / Backlight (Sunset orange rim light catching the spoiler, roof scoop, and wheels)
    rim_data = bpy.data.lights.new(name="Light_Rim", type='AREA')
    rim_data.energy = 800.0
    rim_data.size = 4.0
    rim_data.color = (1.0, 0.70, 0.40)
    rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
    rim_obj.location = (0.0, -5.2, 4.0)
    rim_obj.rotation_euler = (math.radians(-55), 0, math.radians(180))
    bpy.context.scene.collection.objects.link(rim_obj)

    # Ground Studio Asphalt / Turf Pitch Floor
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Stadium_Pitch_Floor"
    m_floor = get_or_create_material('Mat_StadiumFloor')
    nt = m_floor.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.08, 0.05, 1.0) # Deep turf green
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Metallic'].default_value = 0.10
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    floor.data.materials.append(m_floor)

    # Subtle White Field Sideline
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -0.6, 0.003))
    line = bpy.context.active_object
    line.scale = (28.0, 0.16, 1.0)
    m_line = get_or_create_material('Mat_PitchLine')
    nt = m_line.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.94, 0.96, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.40
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    line.data.materials.append(m_line)

    # Stadium Sun Light for high-gloss metallic car highlights
    sun_data = bpy.data.lights.new(name="Light_Sun", type='SUN')
    sun_data.energy = 4.0
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.angle = math.radians(8)
    sun_obj = bpy.data.objects.new("Light_Sun", sun_data)
    sun_obj.rotation_euler = (math.radians(52), math.radians(16), math.radians(-38))
    bpy.context.scene.collection.objects.link(sun_obj)

def setup_camera():
    """Sets up camera angled at the exact 3/4 beauty perspective matching media_1790263831226.png."""
    cam_data = bpy.data.cameras.new(name="Camera_BlueprintView")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Camera_BlueprintView", cam_data)
    cam_obj.location = (3.4, 3.6, 1.85)
    direction = Vector((0, 0.10, 0.65)) - cam_obj.location
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
    print("=== BUILDING 1:1 REFERENCE BLUEPRINT CAR IN BLENDER ===")
    reset_scene()
    car_col = make_collection("RocketLeague_Championship_Car")
    mats = setup_materials()
    car = build_picture_car(car_col, mats, name="Championship_Octane")
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
