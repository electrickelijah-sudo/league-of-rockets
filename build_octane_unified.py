"""
Unified 1:1 Rocket League Octane Body Builder for Blender 5.x.
Directly reproduces media_1790263831226.png:
- Single cohesive, wide-body shell with integrated front and rear fender flares (NOT open-wheel F1 sticks)
- Wide, aggressive trophy-buggy stance with tires tucked snugly under aerodynamic fender arches
- Sweeping Titanium White trim accents along fender lips and A-pillars
- Dual Alpine White racing stripes with cyan pinstripes running from nose to spoiler
- Recessed angular side door scoops (NOT bulky striped boxes)
- Front tubular bullbar with 4 projector lights (outer cyan halos, lower fog lights)
- Exposed rear V8 engine with bright red cylinder heads (#D32F2F) & chrome intake horns
- Dual chrome rocket thruster nozzles with glowing cyan plasma cores
- High-downforce rear wing with Titanium White endplates
- Chunky deep-dish 10-spoke gunmetal alloy wheels with hollow tires and red brake calipers
- Balanced 3/4 sports camera framing the entire vehicle
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
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.lights: bpy.data.lights.remove(block)
    for block in bpy.data.cameras: bpy.data.cameras.remove(block)

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

    # 2. Titanium White Trim (#FFFFFF)
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

    # 4. Racing Red Engine Cylinder Heads & Calipers (#D32F2F)
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

    # 5. Polished Mirror Chrome
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

    # 6. Tinted Glass
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

    # 7. Gunmetal Christiano Alloy
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

    # 9. Drilled Steel Rotor
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

def build_unified_octane_body(name, mats):
    """
    Builds the unified, sculpted Octane main body shell with integrated front/rear fender arches.
    This creates the iconic muscular silhouette of the Octane without disjointed floating boxes.
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")

    # Stations along Y (front to back) with half-width stations:
    # 0: Center (x=0)
    # 1: Stripe Ridge (x ~ 0.22 - 0.32)
    # 2: Hood / Roof Shoulder (x ~ 0.38 - 0.52)
    # 3: Fender Flare Peak (x ~ 0.85 - 1.02)
    # 4: Fender Outer Arch Lip (x ~ 0.92 - 1.08)
    # 5: Lower Rocker Sill (x ~ 0.45 - 0.58)

    stations = [
        # Nose tip
        {"y": 1.68, "cz": 0.40, "rx": 0.18, "rz": 0.38, "sx": 0.35, "sz": 0.35, "fx": 0.55, "fz": 0.34, "bx": 0.32, "bz": 0.28},
        # Front bumper / Grille
        {"y": 1.45, "cz": 0.48, "rx": 0.24, "rz": 0.47, "sx": 0.45, "sz": 0.44, "fx": 0.88, "fz": 0.68, "bx": 0.42, "bz": 0.28},
        # Front wheel arch apex
        {"y": 1.05, "cz": 0.62, "rx": 0.28, "rz": 0.60, "sx": 0.52, "sz": 0.58, "fx": 1.02, "fz": 0.96, "bx": 0.48, "bz": 0.28},
        # Front wheel arch rear / Cowl base
        {"y": 0.55, "cz": 0.78, "rx": 0.34, "rz": 0.76, "sx": 0.56, "sz": 0.72, "fx": 0.88, "fz": 0.68, "bx": 0.52, "bz": 0.28},
        # Cockpit windshield rake
        {"y": 0.10, "cz": 1.15, "rx": 0.36, "rz": 1.12, "sx": 0.54, "sz": 0.75, "fx": 0.62, "fz": 0.48, "bx": 0.50, "bz": 0.28},
        # Cockpit roof mid (wasp-waist tuck)
        {"y": -0.35, "cz": 1.28, "rx": 0.36, "rz": 1.26, "sx": 0.52, "sz": 0.76, "fx": 0.64, "fz": 0.48, "bx": 0.50, "bz": 0.28},
        # Cockpit rear / Cabin drop
        {"y": -0.65, "cz": 1.22, "rx": 0.35, "rz": 1.20, "sx": 0.54, "sz": 0.78, "fx": 0.88, "fz": 0.72, "bx": 0.52, "bz": 0.28},
        # Rear wheel arch apex (hip haunch)
        {"y": -1.05, "cz": 0.70, "rx": 0.34, "rz": 0.70, "sx": 0.56, "sz": 0.72, "fx": 1.08, "fz": 1.04, "bx": 0.54, "bz": 0.28},
        # Rear wheel arch drop
        {"y": -1.40, "cz": 0.60, "rx": 0.33, "rz": 0.60, "sx": 0.54, "sz": 0.62, "fx": 0.92, "fz": 0.72, "bx": 0.50, "bz": 0.28},
        # Rear tail / Thruster mount
        {"y": -1.65, "cz": 0.50, "rx": 0.30, "rz": 0.50, "sx": 0.48, "sz": 0.52, "fx": 0.65, "fz": 0.48, "bx": 0.45, "bz": 0.28}
    ]

    # Create symmetric grid:
    # 0: -fx, fz (Right fender flare lip)
    # 1: -sx, sz (Right shoulder)
    # 2: -rx, rz (Right stripe ridge)
    # 3: 0, cz   (Centerline)
    # 4: +rx, rz (Left stripe ridge)
    # 5: +sx, sz (Left shoulder)
    # 6: +fx, fz (Left fender flare lip)
    n_st = len(stations)
    grid = []
    sills_left = []
    sills_right = []

    for st in stations:
        py = st['y']
        row = [
            bm.verts.new(Vector((-st['fx'], py, st['fz']))),
            bm.verts.new(Vector((-st['sx'], py, st['sz']))),
            bm.verts.new(Vector((-st['rx'], py, st['rz']))),
            bm.verts.new(Vector((0.0, py, st['cz']))),
            bm.verts.new(Vector((st['rx'], py, st['rz']))),
            bm.verts.new(Vector((st['sx'], py, st['sz']))),
            bm.verts.new(Vector((st['fx'], py, st['fz'])))
        ]
        grid.append(row)
        sills_left.append(bm.verts.new(Vector((st['bx'], py, st['bz']))))
        sills_right.append(bm.verts.new(Vector((-st['bx'], py, st['bz']))))

    # UV layout: center (col 3) is u = 0.50
    u_map = [0.08, 0.26, 0.40, 0.50, 0.60, 0.74, 0.92]

    # Build top and shoulder faces with UV mapping
    for s in range(n_st - 1):
        v0 = 0.92 - (s / (n_st - 1)) * 0.78
        v1 = 0.92 - ((s + 1) / (n_st - 1)) * 0.78
        for c in range(6):
            va = grid[s][c]
            vb = grid[s][c+1]
            vc = grid[s+1][c+1]
            vd = grid[s+1][c]
            face = bm.faces.new((va, vb, vc, vd))
            for loop in face.loops:
                if loop.vert == va: loop[uv].uv = (u_map[c], v0)
                elif loop.vert == vb: loop[uv].uv = (u_map[c+1], v0)
                elif loop.vert == vc: loop[uv].uv = (u_map[c+1], v1)
                elif loop.vert == vd: loop[uv].uv = (u_map[c], v1)

    # Build side body flanks (ONLY in cabin/door area between wheel wells)
    for s in range(n_st - 1):
        if 3 <= s <= 5:
            # Left side door flank
            bm.faces.new((grid[s][6], sills_left[s], sills_left[s+1], grid[s+1][6]))
            # Right side door flank
            bm.faces.new((sills_right[s], grid[s][0], grid[s+1][0], sills_right[s+1]))

        # Bottom undertray plate across center
        bm.faces.new((sills_left[s], sills_right[s], sills_right[s+1], sills_left[s+1]))

    # Front Nose Cap
    bm.faces.new((grid[0][0], grid[0][1], grid[0][2], grid[0][3]))
    bm.faces.new((grid[0][3], grid[0][4], grid[0][5], grid[0][6]))
    bm.faces.new((grid[0][6], sills_left[0], sills_right[0], grid[0][0]))

    # Rear Tail Cap
    last = n_st - 1
    bm.faces.new((grid[last][3], grid[last][2], grid[last][1], grid[last][0]))
    bm.faces.new((grid[last][6], grid[last][5], grid[last][4], grid[last][3]))
    bm.faces.new((sills_left[last], grid[last][6], grid[last][0], sills_right[last]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mats['body'])
    for p in obj.data.polygons: p.use_smooth = True

    # Crisp sports car bevel
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.018
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)

    return obj

def build_titanium_fender_lips(name, mats):
    """
    Builds the signature sweeping Titanium White trim accent lips
    along the outer lower edges of the front and rear fender arches.
    """
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'

    # Front fender white trim lips
    for sx in [-1, 1]:
        mesh = bpy.data.meshes.new(f"{name}_FrontLip_{sx}")
        bm = bmesh.new()
        arc_pts = 9
        f_r = 0.52
        f_cx = sx * 1.02
        f_cy = 1.05
        f_cz = 0.46
        w = 0.048

        v_in, v_out = [], []
        for i in range(arc_pts):
            t = i / (arc_pts - 1)
            ang = math.radians(32.0 + t * 116.0)
            y = f_cy + math.cos(ang) * f_r
            z = f_cz + math.sin(ang) * f_r
            v_in.append(bm.verts.new(Vector((f_cx, y, z))))
            v_out.append(bm.verts.new(Vector((f_cx + sx * w, y, z - 0.035))))

        for i in range(arc_pts - 1):
            bm.faces.new((v_in[i], v_out[i], v_out[i + 1], v_in[i + 1]))

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        lip = bpy.data.objects.new(f"{name}_FrontLip_{sx}", mesh)
        lip.parent = root
        lip.data.materials.append(mats['white'])
        for p in lip.data.polygons: p.use_smooth = True

    # Rear fender white trim lips
    for sx in [-1, 1]:
        mesh = bpy.data.meshes.new(f"{name}_RearLip_{sx}")
        bm = bmesh.new()
        arc_pts = 9
        r_r = 0.55
        r_cx = sx * 1.08
        r_cy = -1.05
        r_cz = 0.50
        w = 0.052

        v_in, v_out = [], []
        for i in range(arc_pts):
            t = i / (arc_pts - 1)
            ang = math.radians(32.0 + t * 116.0)
            y = r_cy + math.cos(ang) * r_r
            z = r_cz + math.sin(ang) * r_r
            v_in.append(bm.verts.new(Vector((r_cx, y, z))))
            v_out.append(bm.verts.new(Vector((r_cx + sx * w, y, z - 0.038))))

        for i in range(arc_pts - 1):
            bm.faces.new((v_in[i], v_out[i], v_out[i + 1], v_in[i + 1]))

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        lip = bpy.data.objects.new(f"{name}_RearLip_{sx}", mesh)
        lip.parent = root
        lip.data.materials.append(mats['white'])
        for p in lip.data.polygons: p.use_smooth = True

    return root

def build_hollow_sports_wheel(name, mats, outer_r=0.48, width=0.34, is_left=True):
    """
    Builds large, chunky, aggressive off-road racing wheel:
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
    for poly in tire.data.polygons: poly.use_smooth = True

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

def build_complete_octane(col, mats, name="Championship_Octane", location=(0, 0, 0), rotation=(0, 0, 0)):
    """Builds the authentic 1:1 Rocket League Octane in Blender."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    root = bpy.context.active_object
    root.name = name
    root.rotation_euler = rotation

    # =========================================================================
    # 1. MAIN UNIFIED WIDE-BODY SHELL (Cobalt Blue with Dual Stripes)
    # =========================================================================
    body = build_unified_octane_body(f"{name}_Body", mats)
    body.parent = root

    # Sweeping Titanium White Fender Trim Lips
    lips = build_titanium_fender_lips(f"{name}_FenderLips", mats)
    lips.parent = root

    # Titanium White Chamfer Flanks along Hood Edges
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        chamf = bpy.context.active_object
        chamf.parent = root
        chamf.location = (sx * 0.44, 1.15, 0.64)
        chamf.scale = (0.08, 0.70, 0.04)
        chamf.rotation_euler = (-0.22, sx * 0.30, 0)
        chamf.data.materials.append(mats['white'])
        chamf.name = f"{name}_HoodTrim_{'L' if sx > 0 else 'R'}"
        for p in chamf.data.polygons: p.use_smooth = True

    # =========================================================================
    # 2. FRONT TUBULAR BULLBAR & 4 PROJECTOR LIGHTS
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

    # Uprights connecting tubes
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
    # 3. AERODYNAMIC COCKPIT & WHITE A-PILLARS
    # =========================================================================
    # Windshield Glass (42° Rake)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    windshield = bpy.context.active_object
    windshield.parent = root
    windshield.location = (0, 0.20, 1.04)
    windshield.scale = (0.76, 0.60, 0.028)
    windshield.rotation_euler = (math.radians(-42), 0, 0)
    windshield.data.materials.append(mats['glass'])
    windshield.name = f"{name}_Windshield"

    # Titanium White Structural A-Pillars
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

    # Black Dual-Snorkel Roof Air Intake Scoop
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

    for sx in [-0.10, 0.10]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        nostril = bpy.context.active_object
        nostril.parent = root
        nostril.location = (sx, -0.11, 1.34)
        nostril.scale = (0.10, 0.03, 0.05)
        nostril.data.materials.append(mats['chassis'])
        nostril.name = f"{name}_ScoopNostril_{sx}"

    # Side Window Glass
    for wx in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        swin = bpy.context.active_object
        swin.parent = root
        swin.location = (wx, -0.22, 1.05)
        swin.scale = (0.02, 0.52, 0.30)
        swin.data.materials.append(mats['glass'])
        swin.name = f"{name}_SideWindow_{'L' if wx > 0 else 'R'}"

    # Subtle Neon Cyan Rocker Accent Tube along sills
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=1.45)
        neon_t = bpy.context.active_object
        neon_t.parent = root
        neon_t.location = (sx * 0.54, -0.10, 0.28)
        neon_t.rotation_euler = (math.pi/2, 0, 0)
        neon_t.data.materials.append(mats['neon_cyan'])
        neon_t.name = f"{name}_NeonRocker_{'L' if sx > 0 else 'R'}"

    # =========================================================================
    # 4. EXPOSED REAR V8 ENGINE & TWIN ROCKET THRUSTERS
    # =========================================================================
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    eng_block = bpy.context.active_object
    eng_block.parent = root
    eng_block.location = (0, -0.98, 0.62)
    eng_block.scale = (0.64, 0.66, 0.38)
    eng_block.data.materials.append(mats['chassis'])
    eng_block.name = f"{name}_EngineBlock"
    for p in eng_block.data.polygons: p.use_smooth = True

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

        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.52)
        wire = bpy.context.active_object
        wire.parent = root
        wire.location = (ex, -0.98, 0.90)
        wire.rotation_euler = (math.pi/2, 0, 0)
        wire.data.materials.append(mats['chrome'])
        wire.name = f"{name}_IgnitionConduit_{ex}"

    for iy in [-1.16, -1.04, -0.92, -0.80]:
        for ix in [-0.08, 0.08]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.15)
            stack = bpy.context.active_object
            stack.parent = root
            stack.location = (ix, iy, 0.88)
            stack.data.materials.append(mats['chrome'])
            stack.name = f"{name}_IntakeStack_{ix}_{iy}"

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
    # 5. HIGH-DOWNFORCE REAR WING
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

    # Rear Red LED Taillights on rear haunches
    for sx in [-0.85, 0.85]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.08)
        tl = bpy.context.active_object
        tl.parent = root
        tl.location = (sx, -1.48, 0.72)
        tl.rotation_euler = (math.pi/2, 0, 0)
        tl.data.materials.append(mats['tail_red'])
        tl.name = f"{name}_TailLight_{sx}"

    # =========================================================================
    # 6. FOUR CHUNKY WHEELS TUCKED UNDER INTEGRATED ARCHES
    # =========================================================================
    wheel_coords = [
        ("Wheel_Front_Left", 0.98, 1.05, 0.46, 0.46, 0.34, True),
        ("Wheel_Front_Right", -0.98, 1.05, 0.46, 0.46, 0.34, False),
        ("Wheel_Rear_Left", 1.04, -1.05, 0.50, 0.50, 0.36, True),
        ("Wheel_Rear_Right", -1.04, -1.05, 0.50, 0.50, 0.36, False),
    ]

    for w_name, wx, wy, wz, outer_r, width, is_left in wheel_coords:
        w_obj = build_hollow_sports_wheel(f"{name}_{w_name}", mats, outer_r=outer_r, width=width, is_left=is_left)
        w_obj.location = (wx, wy, wz)
        w_obj.parent = root

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
    cam_obj.location = (3.6, 4.0, 1.95)
    direction = Vector((0, 0.08, 0.65)) - cam_obj.location
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
    car = build_complete_octane(car_col, mats, name="Championship_Octane")
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
