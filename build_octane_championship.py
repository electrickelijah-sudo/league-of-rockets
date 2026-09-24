"""
Championship 1:1 Rocket League Octane Builder for Blender 5.1.2.
Matches media_1790263831226.png with authentic dune buggy proportions:
- Wide, compact, muscular stance (short wheelbase, wide track)
- Hollow rubber tires with recessed deep-dish 10-spoke gunmetal alloy wheels, chrome lips, and red brake calipers
- Fender arches hug the top of the tires with sleek ~0.04m clearance, bordered by sweeping Titanium White trim lips
- Broad wedge hood with dual Alpine White racing stripes running from front grille to windshield
- Raked dark-glass windshield framed by Titanium White A-pillars
- Flat blue roof with dual stripes and dual-port matte black roof scoop
- Sculpted wasp-waist side body with cyan neon rocker tube
- Open rear engine bay with exposed V8 engine (bright red valve covers, 8 chrome velocity stacks)
- Dual chrome rocket boost thrusters with glowing cyan plasma cores
- High-downforce rear wing with Titanium White endplates
- Front tubular steel bullbar with dual cyan halo projector headlights and lower foglights
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)

# ---------------------------------------------------------
# Materials Setup
# ---------------------------------------------------------
def create_materials():
    mats = {}

    def new_pbr(name, base_color, metallic=0.0, roughness=0.3, clearcoat=0.0, emission_color=None, emission_strength=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = clearcoat
        elif "Clearcoat" in bsdf.inputs:
            bsdf.inputs["Clearcoat"].default_value = clearcoat
        if emission_color and emission_strength > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_color
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
        mats[name] = mat
        return mat

    # Cobalt Blue Gloss Paint
    new_pbr("CarPaint_Cobalt", (0.012, 0.12, 0.70, 1.0), metallic=0.75, roughness=0.18, clearcoat=1.0)
    
    # Titanium White Trim Paint
    new_pbr("CarPaint_White", (0.95, 0.95, 0.97, 1.0), metallic=0.15, roughness=0.18, clearcoat=0.9)

    # Alpine White Racing Stripes
    new_pbr("RacingStripe_White", (0.98, 0.98, 1.0, 1.0), metallic=0.05, roughness=0.15, clearcoat=1.0)

    # Dark Tinted Automotive Glass
    new_pbr("Cockpit_Glass", (0.01, 0.012, 0.018, 1.0), metallic=0.92, roughness=0.03, clearcoat=1.0)

    # Matte Black Chassis & Engine Cradle
    new_pbr("Chassis_MatteBlack", (0.025, 0.025, 0.028, 1.0), metallic=0.35, roughness=0.55)

    # Polished Mirror Chrome
    new_pbr("Polished_Chrome", (0.96, 0.96, 0.96, 1.0), metallic=1.0, roughness=0.03)

    # Gunmetal Alloy
    new_pbr("Gunmetal_Alloy", (0.16, 0.17, 0.18, 1.0), metallic=0.92, roughness=0.22)

    # Tire Rubber
    new_pbr("Tire_Rubber", (0.02, 0.02, 0.02, 1.0), metallic=0.02, roughness=0.70)

    # Racing Red Engine Valve Covers & Calipers (#D32F2F)
    new_pbr("Engine_Red", (0.82, 0.04, 0.04, 1.0), metallic=0.35, roughness=0.25, clearcoat=0.8)

    # Cyan Neon Halos & Rocket Plasma (#00F0FF)
    new_pbr("Neon_Cyan", (0.0, 0.88, 1.0, 1.0), emission_color=(0.0, 0.88, 1.0, 1.0), emission_strength=16.0)

    # Projector Light White Core
    new_pbr("Headlight_WhiteBeam", (0.96, 0.98, 1.0, 1.0), emission_color=(0.96, 0.98, 1.0, 1.0), emission_strength=22.0)

    # LED Neon Red Taillights
    new_pbr("Neon_Red", (1.0, 0.02, 0.02, 1.0), emission_color=(1.0, 0.02, 0.02, 1.0), emission_strength=10.0)

    return mats

def assign_mat(obj, mat):
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

def apply_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

# ---------------------------------------------------------
# 1. Broad Wedge Hood & Honeycomb Radiator Grille
# ---------------------------------------------------------
def build_hood(mats):
    """
    Constructs the broad wedge hood with DUAL Alpine White racing stripes,
    blue center spine, full-width nose connecting to headlights, and honeycomb grille.
    Windshield base at Y=0.25, front bumper at Y=1.15.
    """
    bm = bmesh.new()

    # Y=0.25 (Windshield base, width X=0.34)
    v_cowl_c  = bm.verts.new(Vector((0.00, 0.25, 0.52))) # center
    v_cowl_s1 = bm.verts.new(Vector((0.04, 0.25, 0.52))) # stripe inner
    v_cowl_s2 = bm.verts.new(Vector((0.16, 0.25, 0.52))) # stripe outer
    v_cowl_o  = bm.verts.new(Vector((0.34, 0.25, 0.52))) # outer shoulder

    # Y=0.70 (Mid hood, width X=0.34)
    v_mid_c  = bm.verts.new(Vector((0.00, 0.70, 0.40)))
    v_mid_s1 = bm.verts.new(Vector((0.04, 0.70, 0.40)))
    v_mid_s2 = bm.verts.new(Vector((0.15, 0.70, 0.40)))
    v_mid_o  = bm.verts.new(Vector((0.34, 0.70, 0.40)))

    # Y=1.15 (Nose top, width X=0.34 connecting directly to headlights)
    v_nose_c  = bm.verts.new(Vector((0.00, 1.15, 0.28)))
    v_nose_s1 = bm.verts.new(Vector((0.04, 1.15, 0.28)))
    v_nose_s2 = bm.verts.new(Vector((0.15, 1.15, 0.28)))
    v_nose_o  = bm.verts.new(Vector((0.34, 1.15, 0.28)))

    # Y=1.15 (Grille bottom, Z=0.12)
    v_grille_c  = bm.verts.new(Vector((0.00, 1.15, 0.12)))
    v_grille_s1 = bm.verts.new(Vector((0.04, 1.15, 0.12)))
    v_grille_s2 = bm.verts.new(Vector((0.15, 1.15, 0.12)))
    v_grille_o  = bm.verts.new(Vector((0.34, 1.15, 0.12)))

    # Lower belly
    v_belly_c = bm.verts.new(Vector((0.00, 0.70, 0.14)))
    v_belly_o = bm.verts.new(Vector((0.32, 0.70, 0.14)))

    # Hood quads:
    # Column 1: Blue center spine (0.0 to 0.04)
    bm.faces.new([v_cowl_c, v_cowl_s1, v_mid_s1, v_mid_c])
    bm.faces.new([v_mid_c, v_mid_s1, v_nose_s1, v_nose_c])
    # Column 2: Alpine White Racing Stripe (0.04 to 0.15)
    bm.faces.new([v_cowl_s1, v_cowl_s2, v_mid_s2, v_mid_s1])
    bm.faces.new([v_mid_s1, v_mid_s2, v_nose_s2, v_nose_s1])
    # Column 3: Blue Outer Cowl Shoulder (0.15 to 0.34)
    bm.faces.new([v_cowl_s2, v_cowl_o, v_mid_o, v_mid_s2])
    bm.faces.new([v_mid_s2, v_mid_o, v_nose_o, v_nose_s2])

    # Front Grille
    bm.faces.new([v_nose_c, v_nose_s1, v_grille_s1, v_grille_c])
    bm.faces.new([v_nose_s1, v_nose_s2, v_grille_s2, v_grille_s1])
    bm.faces.new([v_nose_s2, v_nose_o, v_grille_o, v_grille_s2])

    # Lower Belly
    bm.faces.new([v_grille_c, v_grille_s1, v_belly_c])
    bm.faces.new([v_grille_s1, v_grille_s2, v_belly_c])
    bm.faces.new([v_grille_s2, v_grille_o, v_belly_o, v_belly_c])
    bm.faces.new([v_nose_o, v_mid_o, v_belly_o, v_grille_o])

    mesh = bpy.data.meshes.new("Hood_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    hood = bpy.data.objects.new("Octane_Hood", mesh)
    bpy.context.collection.objects.link(hood)
    hood.data.materials.append(mats["CarPaint_Cobalt"])      # 0
    hood.data.materials.append(mats["RacingStripe_White"])  # 1
    hood.data.materials.append(mats["Chassis_MatteBlack"])  # 2

    for p in hood.data.polygons:
        p.use_smooth = True
        c = p.center
        if c.y > 1.14: # Grille
            p.material_index = 2
        elif 0.038 < c.x < 0.155 and c.z > 0.25: # Dual Alpine White racing stripe
            p.material_index = 1
        else:
            p.material_index = 0

    mod_m = hood.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    return hood

# ---------------------------------------------------------
# 2. Sleek Front Fender Arches Hugging Tires with Inner Well Walls
# ---------------------------------------------------------
def build_front_fenders(mats):
    """
    Constructs the front fender arches that curve closely over the front wheels
    with solid inner wheel-well splash walls.
    Front wheel center: X=±0.68, Y=0.75, Z=0.35. Radius = 0.35.
    Fender radius = 0.40.
    """
    bm = bmesh.new()
    angles = [20, 50, 80, 110, 140, 165]
    r_arch = 0.40
    y_c = 0.75
    z_c = 0.35
    x_in = 0.34
    x_peak = 0.68
    x_out = 0.82

    prev_in, prev_mid, prev_out, prev_bot = None, None, None, None

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad) * r_arch
        dz = math.sin(rad) * r_arch

        # Inner edge attached along hood
        v_in = bm.verts.new(Vector((x_in, y_c - dy * 0.75, z_c + dz * 0.75)))
        # Inner wheel well lower wall down to chassis (Z=0.15)
        v_bot = bm.verts.new(Vector((x_in, y_c - dy * 0.75, 0.15)))
        # Peak of arch over tire
        v_mid = bm.verts.new(Vector((x_peak, y_c - dy, z_c + dz)))
        # Outer flare lip over outer tire face
        v_out = bm.verts.new(Vector((x_out, y_c - dy, z_c + dz * 0.92)))

        if prev_in is not None:
            # Fender top surfaces
            bm.faces.new([prev_in, v_in, v_mid, prev_mid])
            bm.faces.new([prev_mid, v_mid, v_out, prev_out])
            # Inner wheel well vertical splash wall
            bm.faces.new([prev_bot, v_bot, v_in, prev_in])

        prev_in, prev_mid, prev_out, prev_bot = v_in, v_mid, v_out, v_bot

    mesh = bpy.data.meshes.new("Front_Fender_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    fender = bpy.data.objects.new("Front_Fenders", mesh)
    bpy.context.collection.objects.link(fender)
    assign_mat(fender, mats["CarPaint_Cobalt"])
    apply_smooth(fender)

    mod_m = fender.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    mod_s = fender.modifiers.new("Subsurf", 'SUBSURF')
    mod_s.levels = 1
    mod_s.render_levels = 2

    # Titanium White Trim Lip along outer rim
    for side in [-1, 1]:
        bm_lip = bmesh.new()
        prev_v1, prev_v2 = None, None
        for deg in [20, 40, 60, 80, 100, 120, 140, 165]:
            rad = math.radians(deg)
            dy = math.cos(rad) * (r_arch + 0.008)
            dz = math.sin(rad) * (r_arch + 0.008) * 0.92
            p1 = Vector((x_out * side, y_c - dy, z_c + dz))
            p2 = Vector(((x_out + 0.025) * side, y_c - dy * 1.02, z_c + dz - 0.035))
            v1 = bm_lip.verts.new(p1)
            v2 = bm_lip.verts.new(p2)
            if prev_v1 is not None:
                bm_lip.faces.new([prev_v1, v1, v2, prev_v2])
            prev_v1, prev_v2 = v1, v2

        mesh_lip = bpy.data.meshes.new(f"FrontLip_{'L' if side < 0 else 'R'}")
        bm_lip.to_mesh(mesh_lip)
        bm_lip.free()
        lip_obj = bpy.data.objects.new(f"FrontLip_{'L' if side < 0 else 'R'}", mesh_lip)
        bpy.context.collection.objects.link(lip_obj)
        assign_mat(lip_obj, mats["CarPaint_White"])
        apply_smooth(lip_obj)

# ---------------------------------------------------------
# 3. Cockpit Canopy, A-Pillars & Roof Scoop
# ---------------------------------------------------------
def build_cockpit(mats):
    """
    Constructs the cockpit:
    - Raked dark glass windshield
    - Swept Titanium White A-pillars framing the windshield
    - Flat roof with dual Alpine White stripes
    - Side triangular canopy windows
    - Dual-port roof air scoop
    """
    # 1. Dark Glass Windshield & Side Windows
    bm = bmesh.new()
    gw_b_c = bm.verts.new(Vector((0.00, 0.25, 0.52)))
    gw_b_o = bm.verts.new(Vector((0.30, 0.25, 0.52)))
    gw_t_c = bm.verts.new(Vector((0.00, -0.15, 0.82)))
    gw_t_o = bm.verts.new(Vector((0.23, -0.15, 0.82)))
    bm.faces.new([gw_b_c, gw_b_o, gw_t_o, gw_t_c])

    # Side Window
    gw_rear = bm.verts.new(Vector((0.25, -0.55, 0.72)))
    gw_sill = bm.verts.new(Vector((0.34, -0.50, 0.46)))
    bm.faces.new([gw_b_o, gw_t_o, gw_rear, gw_sill])

    mesh_g = bpy.data.meshes.new("Cockpit_Glass_Mesh")
    bm.to_mesh(mesh_g)
    bm.free()
    glass = bpy.data.objects.new("Cockpit_Glass", mesh_g)
    bpy.context.collection.objects.link(glass)
    assign_mat(glass, mats["Cockpit_Glass"])
    mod_m = glass.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True

    # 2. Precision Titanium White A-Pillars
    for side in [-1, 1]:
        bm_p = bmesh.new()
        p_start = Vector((0.30 * side, 0.25, 0.52))
        p_end   = Vector((0.23 * side, -0.15, 0.82))
        v_b1 = bm_p.verts.new(p_start + Vector((-0.02 * side, 0, 0.01)))
        v_b2 = bm_p.verts.new(p_start + Vector(( 0.02 * side, 0, -0.01)))
        v_b3 = bm_p.verts.new(p_start + Vector(( 0.02 * side, 0, -0.05)))
        v_b4 = bm_p.verts.new(p_start + Vector((-0.02 * side, 0, -0.03)))

        v_t1 = bm_p.verts.new(p_end + Vector((-0.02 * side, 0, 0.01)))
        v_t2 = bm_p.verts.new(p_end + Vector(( 0.02 * side, 0, -0.01)))
        v_t3 = bm_p.verts.new(p_end + Vector(( 0.02 * side, 0, -0.05)))
        v_t4 = bm_p.verts.new(p_end + Vector((-0.02 * side, 0, -0.03)))

        bm_p.faces.new([v_b1, v_t1, v_t2, v_b2])
        bm_p.faces.new([v_b2, v_t2, v_t3, v_b3])
        bm_p.faces.new([v_b3, v_t3, v_t4, v_b4])
        bm_p.faces.new([v_b4, v_t4, v_t1, v_b1])

        mesh_p = bpy.data.meshes.new(f"APillar_{'L' if side < 0 else 'R'}")
        bm_p.to_mesh(mesh_p)
        bm_p.free()
        pillar = bpy.data.objects.new(f"APillar_{'L' if side < 0 else 'R'}", mesh_p)
        bpy.context.collection.objects.link(pillar)
        assign_mat(pillar, mats["CarPaint_White"])
        apply_smooth(pillar)

    # 3. Flat Blue Roof Deck with Dual White Stripes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.35, 0.82))
    roof = bpy.context.active_object
    roof.name = "Cockpit_Roof"
    roof.scale = (0.48, 0.44, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(roof, mats["CarPaint_Cobalt"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.08 * side, -0.35, 0.84))
        rs = bpy.context.active_object
        rs.name = f"Roof_Stripe_{'L' if side < 0 else 'R'}"
        rs.scale = (0.055, 0.21, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(rs, mats["RacingStripe_White"])

    # 4. Signature Dual-Port Roof Air Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.42, 0.88))
    scoop = bpy.context.active_object
    scoop.name = "Roof_Air_Scoop"
    scoop.scale = (0.30, 0.20, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(scoop, mats["Chassis_MatteBlack"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.075 * side, -0.31, 0.88))
        nostril = bpy.context.active_object
        nostril.name = f"Scoop_Nostril_{'L' if side < 0 else 'R'}"
        nostril.scale = (0.065, 0.03, 0.03)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(nostril, mats["Polished_Chrome"])

# ---------------------------------------------------------
# 4. Side Body & Rear Fenders
# ---------------------------------------------------------
def build_side_and_rear_fenders(mats):
    """
    Constructs the wasp-waist side body, cyan neon rocker tubes,
    flared rear fenders that arch over the rear wheels, and Titanium White trim lips.
    Rear wheel center: X=±0.70, Y=-0.75, Z=0.38. Radius = 0.38.
    """
    # 1. Wasp-Waist Side Body Pod
    bm_side = bmesh.new()
    v_f_top = bm_side.verts.new(Vector((0.32, 0.25, 0.48)))
    v_f_bot = bm_side.verts.new(Vector((0.34, 0.25, 0.16)))
    v_m_top = bm_side.verts.new(Vector((0.28, -0.30, 0.46)))
    v_m_bot = bm_side.verts.new(Vector((0.32, -0.30, 0.16)))
    v_r_top = bm_side.verts.new(Vector((0.40, -0.55, 0.52)))
    v_r_bot = bm_side.verts.new(Vector((0.40, -0.55, 0.16)))

    bm_side.faces.new([v_f_top, v_m_top, v_m_bot, v_f_bot])
    bm_side.faces.new([v_m_top, v_r_top, v_r_bot, v_m_bot])

    mesh_s = bpy.data.meshes.new("Side_Body_Mesh")
    bm_side.to_mesh(mesh_s)
    bm_side.free()

    side_body = bpy.data.objects.new("Side_Body_Pods", mesh_s)
    bpy.context.collection.objects.link(side_body)
    assign_mat(side_body, mats["CarPaint_Cobalt"])
    apply_smooth(side_body)
    mod_m = side_body.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True

    # Cyan Neon Rocker Tube
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.015,
            depth=0.75,
            vertices=8,
            location=(0.34 * side, -0.15, 0.15)
        )
        tube = bpy.context.active_object
        tube.name = f"Neon_Rocker_{'L' if side < 0 else 'R'}"
        tube.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(tube, mats["Neon_Cyan"])

    # 2. Flared Rear Fenders Arching Over Rear Wheels (Tight clearance)
    bm_rf = bmesh.new()
    angles = [15, 45, 75, 105, 135, 165]
    r_rarch = 0.43
    y_c = -0.75
    z_c = 0.38
    x_in = 0.38
    x_peak = 0.70
    x_out = 0.86

    prev_in, prev_mid, prev_out, prev_bot = None, None, None, None

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad) * r_rarch
        dz = math.sin(rad) * r_rarch

        curr_in = bm_rf.verts.new(Vector((x_in, y_c - dy * 0.75, z_c + dz * 0.80)))
        curr_bot = bm_rf.verts.new(Vector((x_in, y_c - dy * 0.75, 0.15)))
        curr_mid = bm_rf.verts.new(Vector((x_peak, y_c - dy, z_c + dz)))
        curr_out = bm_rf.verts.new(Vector((x_out, y_c - dy, z_c + dz * 0.92)))

        if prev_in is not None:
            bm_rf.faces.new([prev_in, curr_in, curr_mid, prev_mid])
            bm_rf.faces.new([prev_mid, curr_mid, curr_out, prev_out])
            bm_rf.faces.new([prev_bot, curr_bot, curr_in, prev_in])

        prev_in, prev_mid, prev_out, prev_bot = curr_in, curr_mid, curr_out, curr_bot

    mesh_rf = bpy.data.meshes.new("Rear_Fender_Mesh")
    bm_rf.to_mesh(mesh_rf)
    bm_rf.free()

    rear_fender = bpy.data.objects.new("Rear_Fenders", mesh_rf)
    bpy.context.collection.objects.link(rear_fender)
    assign_mat(rear_fender, mats["CarPaint_Cobalt"])
    apply_smooth(rear_fender)

    mod_m = rear_fender.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True
    mod_s = rear_fender.modifiers.new("Subsurf", 'SUBSURF')
    mod_s.levels = 1
    mod_s.render_levels = 2

    # Sweeping Titanium White Trim Lip on Rear Fenders
    for side in [-1, 1]:
        bm_rlip = bmesh.new()
        prev_l1, prev_l2 = None, None
        for deg in [15, 35, 55, 75, 95, 115, 135, 155, 165]:
            rad = math.radians(deg)
            dy = math.cos(rad) * (r_rarch + 0.008)
            dz = math.sin(rad) * (r_rarch + 0.008) * 0.92
            p1 = Vector((x_out * side, y_c - dy, z_c + dz))
            p2 = Vector(((x_out + 0.025) * side, y_c - dy * 1.02, z_c + dz - 0.035))
            v1 = bm_rlip.verts.new(p1)
            v2 = bm_rlip.verts.new(p2)
            if prev_l1 is not None:
                bm_rlip.faces.new([prev_l1, v1, v2, prev_l2])
            prev_l1, prev_l2 = v1, v2

        mesh_rlip = bpy.data.meshes.new(f"RearLip_{'L' if side < 0 else 'R'}")
        bm_rlip.to_mesh(mesh_rlip)
        bm_rlip.free()
        rlip_obj = bpy.data.objects.new(f"RearLip_{'L' if side < 0 else 'R'}", mesh_rlip)
        bpy.context.collection.objects.link(rlip_obj)
        assign_mat(rlip_obj, mats["CarPaint_White"])
        apply_smooth(rlip_obj)

        # Red LED Taillight
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.58 * side, -1.18, 0.48))
        tl = bpy.context.active_object
        tl.name = f"Taillight_{'L' if side < 0 else 'R'}"
        tl.scale = (0.12, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(tl, mats["Neon_Red"])

# ---------------------------------------------------------
# 5. Exposed Rear Engine Bay & Rocket Thrusters
# ---------------------------------------------------------
def build_engine_and_thrusters(mats):
    """
    Constructs the open rear engine cradle, V8 engine block,
    bright racing red valve covers, 8 chrome velocity stacks,
    and dual rocket boost thrusters.
    """
    # 1. Lower Engine Bed / Rear Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.85, 0.24))
    bed = bpy.context.active_object
    bed.name = "Engine_Bed_Chassis"
    bed.scale = (0.60, 0.65, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(bed, mats["Chassis_MatteBlack"])

    # 2. V8 Engine Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.80, 0.38))
    block = bpy.context.active_object
    block.name = "V8_Engine_Block"
    block.scale = (0.32, 0.38, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(block, mats["Gunmetal_Alloy"])

    # 3. Dual Racing Red Valve Covers
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.14 * side, -0.80, 0.46))
        valve = bpy.context.active_object
        valve.name = f"ValveCover_Red_{'L' if side < 0 else 'R'}"
        valve.scale = (0.11, 0.36, 0.065)
        valve.rotation_euler = (0, math.radians(20 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(valve, mats["Engine_Red"])

        # 4 Chrome Velocity Intake Stacks per bank
        for row in range(4):
            y_pos = -0.68 - (row * 0.08)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.022,
                depth=0.10,
                vertices=12,
                location=(0.09 * side, y_pos, 0.52)
            )
            stack = bpy.context.active_object
            stack.name = f"IntakeStack_{'L' if side < 0 else 'R'}_{row}"
            assign_mat(stack, mats["Polished_Chrome"])

    # 4. Dual Rocket Boost Thruster Nozzles
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.088,
            depth=0.16,
            vertices=18,
            location=(0.14 * side, -1.22, 0.36)
        )
        nozzle = bpy.context.active_object
        nozzle.name = f"Rocket_Nozzle_{'L' if side < 0 else 'R'}"
        nozzle.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(nozzle, mats["Chassis_MatteBlack"])

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.088,
            minor_radius=0.015,
            major_segments=18,
            minor_segments=8,
            location=(0.14 * side, -1.30, 0.36)
        )
        ring = bpy.context.active_object
        ring.name = f"Nozzle_Rim_{'L' if side < 0 else 'R'}"
        ring.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(ring, mats["Polished_Chrome"])

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.068,
            depth=0.04,
            vertices=16,
            location=(0.14 * side, -1.28, 0.36)
        )
        plasma = bpy.context.active_object
        plasma.name = f"Rocket_Plasma_{'L' if side < 0 else 'R'}"
        plasma.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(plasma, mats["Neon_Cyan"])

# ---------------------------------------------------------
# 6. High-Downforce Rear Wing
# ---------------------------------------------------------
def build_rear_wing(mats):
    """
    Constructs the high-downforce rear wing with Titanium White endplates.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.05, 0.94))
    wing = bpy.context.active_object
    wing.name = "Rear_Wing_Airfoil"
    wing.scale = (0.84, 0.22, 0.036)
    wing.rotation_euler = (math.radians(-7), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(wing, mats["CarPaint_Cobalt"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022,
            depth=0.46,
            vertices=10,
            location=(0.26 * side, -0.98, 0.74)
        )
        pylon = bpy.context.active_object
        pylon.name = f"Wing_Pylon_{'L' if side < 0 else 'R'}"
        pylon.rotation_euler = (math.radians(-22), 0, math.radians(6 * side))
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(pylon, mats["Chassis_MatteBlack"])

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.43 * side, -1.05, 0.94))
        endplate = bpy.context.active_object
        endplate.name = f"Wing_Endplate_{'L' if side < 0 else 'R'}"
        endplate.scale = (0.026, 0.26, 0.16)
        endplate.rotation_euler = (math.radians(-5), math.radians(8 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(endplate, mats["CarPaint_White"])

# ---------------------------------------------------------
# 7. Front Bullbar & Projector Headlights
# ---------------------------------------------------------
def build_front_bullbar_and_lights(mats):
    """
    Constructs the tubular bullbar, dual cyan halo projector headlights, and lower fog lights.
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.028,
        depth=0.72,
        vertices=14,
        location=(0.0, 1.22, 0.26)
    )
    bar_top = bpy.context.active_object
    bar_top.name = "Bullbar_Top"
    bar_top.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(bar_top, mats["Chassis_MatteBlack"])

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.024,
        depth=0.58,
        vertices=12,
        location=(0.0, 1.25, 0.14)
    )
    bar_bot = bpy.context.active_object
    bar_bot.name = "Bullbar_Bottom"
    bar_bot.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(bar_bot, mats["Chassis_MatteBlack"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022,
            depth=0.18,
            vertices=10,
            location=(0.18 * side, 1.23, 0.20)
        )
        guard = bpy.context.active_object
        guard.name = f"Bullbar_Guard_{'L' if side < 0 else 'R'}"
        assign_mat(guard, mats["Chassis_MatteBlack"])

        # Projector Headlight
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.084,
            depth=0.07,
            vertices=18,
            location=(0.32 * side, 1.20, 0.27)
        )
        casing = bpy.context.active_object
        casing.name = f"Headlight_Housing_{'L' if side < 0 else 'R'}"
        casing.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(casing, mats["Chassis_MatteBlack"])

        # Cyan Halo Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.078,
            minor_radius=0.015,
            major_segments=22,
            minor_segments=8,
            location=(0.32 * side, 1.24, 0.27)
        )
        halo = bpy.context.active_object
        halo.name = f"Headlight_Halo_{'L' if side < 0 else 'R'}"
        halo.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(halo, mats["Neon_Cyan"])

        # Center White Projector Lens
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.048,
            depth=0.025,
            vertices=16,
            location=(0.32 * side, 1.24, 0.27)
        )
        lens = bpy.context.active_object
        lens.name = f"Headlight_Projector_{'L' if side < 0 else 'R'}"
        lens.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(lens, mats["Headlight_WhiteBeam"])

        # Lower Fog Light
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.042,
            depth=0.035,
            vertices=14,
            location=(0.10 * side, 1.27, 0.14)
        )
        fog = bpy.context.active_object
        fog.name = f"Fog_Light_{'L' if side < 0 else 'R'}"
        fog.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(fog, mats["Headlight_WhiteBeam"])

# ---------------------------------------------------------
# 8. Hollow-Tire 10-Spoke Deep-Dish Sports Wheels
# ---------------------------------------------------------
def build_rocket_league_wheels(mats):
    """
    Constructs 4 authentic Rocket League wheels:
    - Hollow open rubber tire (NOT solid flat disc) with curved sidewall torus
    - Recessed polished chrome outer rim lip
    - Bright gunmetal alloy 10 radial spokes
    - Polished chrome hub
    - Brake rotor disc & bright red racing caliper
    """
    configs = [
        # (name, x, y, z, tire_radius, tire_width, rim_radius)
        ("Front_L", -0.68,  0.75, 0.35, 0.35, 0.24, 0.22),
        ("Front_R",  0.68,  0.75, 0.35, 0.35, 0.24, 0.22),
        ("Rear_L",  -0.70, -0.75, 0.38, 0.38, 0.28, 0.24),
        ("Rear_R",   0.70, -0.75, 0.38, 0.38, 0.28, 0.24),
    ]

    for name, wx, wy, wz, r_tire, w_tire, r_rim in configs:
        is_right = (wx > 0)
        side_mult = 1 if is_right else -1
        outer_rim_x = wx + (w_tire * 0.46 * side_mult)

        # 1. Hollow Rubber Tire (Open cylinder with no end caps, plus sidewall torus!)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_tire,
            depth=w_tire,
            end_fill_type='NOTHING',
            vertices=32,
            location=(wx, wy, wz)
        )
        t_tread = bpy.context.active_object
        t_tread.name = f"Tread_{name}"
        t_tread.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(t_tread, mats["Tire_Rubber"])
        apply_smooth(t_tread)

        # Outer rounded sidewall
        bpy.ops.mesh.primitive_torus_add(
            major_radius=(r_tire + r_rim) * 0.5,
            minor_radius=(r_tire - r_rim) * 0.5,
            major_segments=28,
            minor_segments=10,
            location=(outer_rim_x, wy, wz)
        )
        sidewall = bpy.context.active_object
        sidewall.name = f"Sidewall_{name}"
        sidewall.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(sidewall, mats["Tire_Rubber"])
        apply_smooth(sidewall)

        # 2. Polished Chrome Outer Rim Lip
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r_rim,
            minor_radius=0.020,
            major_segments=24,
            minor_segments=8,
            location=(outer_rim_x, wy, wz)
        )
        rim_lip = bpy.context.active_object
        rim_lip.name = f"RimLip_{name}"
        rim_lip.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(rim_lip, mats["Polished_Chrome"])
        apply_smooth(rim_lip)

        # 3. Recessed Rim Barrel
        barrel_x = outer_rim_x - (0.04 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_rim * 0.98,
            depth=0.08,
            end_fill_type='NOTHING',
            vertices=24,
            location=(barrel_x, wy, wz)
        )
        barrel = bpy.context.active_object
        barrel.name = f"Barrel_{name}"
        barrel.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(barrel, mats["Gunmetal_Alloy"])

        # 4. Chrome Center Hub
        dish_center_x = outer_rim_x - (0.03 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.070,
            depth=0.035,
            vertices=16,
            location=(dish_center_x, wy, wz)
        )
        hub = bpy.context.active_object
        hub.name = f"Hub_{name}"
        hub.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(hub, mats["Polished_Chrome"])

        # 5. 10 Radial Alloy Spokes (Bright Gunmetal)
        for i in range(10):
            theta = i * (2.0 * math.pi / 10.0)
            r_mid = r_rim * 0.52
            sy = wy + math.sin(theta) * r_mid
            sz = wz + math.cos(theta) * r_mid
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(dish_center_x, sy, sz)
            )
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{name}_{i}"
            spoke.scale = (0.022, 0.032, r_rim * 0.82)
            spoke.rotation_euler = (-theta, 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            assign_mat(spoke, mats["Gunmetal_Alloy"])

        # 6. Steel Brake Rotor & Bright Red Racing Caliper
        disc_x = wx - (0.03 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_rim * 0.72,
            depth=0.018,
            vertices=20,
            location=(disc_x, wy, wz)
        )
        disc = bpy.context.active_object
        disc.name = f"BrakeDisc_{name}"
        disc.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(disc, mats["Gunmetal_Alloy"])

        # Red Caliper
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(disc_x, wy + (r_rim * 0.52), wz)
        )
        caliper = bpy.context.active_object
        caliper.name = f"BrakeCaliper_{name}"
        caliper.scale = (0.042, 0.062, 0.10)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(caliper, mats["Engine_Red"])

# ---------------------------------------------------------
# Environment, Studio Lighting & Camera
# ---------------------------------------------------------
def setup_environment_and_camera():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = False

    # Stadium Turf Floor
    bpy.ops.mesh.primitive_plane_add(size=35.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Stadium_Turf"
    floor_mat = bpy.data.materials.new(name="Stadium_Turf_PBR")
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.08, 0.14, 0.09, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    assign_mat(floor, floor_mat)

    # Floor White Pitch Line
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0.002))
    line = bpy.context.active_object
    line.name = "Stadium_Pitch_Line"
    line.scale = (0.09, 18.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    line_mat = bpy.data.materials.new(name="Line_White")
    line_mat.use_nodes = True
    lbsdf = line_mat.node_tree.nodes.get("Principled BSDF")
    lbsdf.inputs["Base Color"].default_value = (0.92, 0.94, 0.96, 1.0)
    lbsdf.inputs["Roughness"].default_value = 0.4
    assign_mat(line, line_mat)

    # Dark Stadium World Environment
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.04, 0.07, 0.11, 1.0)
        bg_node.inputs["Strength"].default_value = 0.6

    # 3-Point Studio Lights
    # Key Light (Warm Floodlight)
    key = bpy.data.lights.new(name="Key_Light", type='SUN')
    key.energy = 4.2
    key.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("Key_Light", key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (-4.5, 4.0, 7.0)
    key_obj.rotation_euler = (math.radians(50), math.radians(-15), math.radians(40))

    # Rim / Accent Light (Cool Stadium Cyan-Blue)
    rim = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim.energy = 550.0
    rim.color = (0.35, 0.78, 1.0)
    rim.size = 4.0
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (4.0, -4.0, 3.8)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(20), math.radians(-135))

    # Fill Light (Soft Neutral)
    fill = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill.energy = 220.0
    fill.color = (0.92, 0.94, 1.0)
    fill.size = 4.5
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-3.2, -2.8, 3.2)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-15), math.radians(-45))

    # Camera matching the hero 3/4 beauty view in media_1790263831226.png
    cam_data = bpy.data.cameras.new(name="Hero_Camera")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Hero_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (-2.8, 2.8, 1.35)
    target = Vector((0.0, 0.05, 0.45))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.camera = cam_obj

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
def main():
    print("=== BUILDING CHAMPIONSHIP 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    mats = create_materials()

    build_hood(mats)
    build_front_fenders(mats)
    build_cockpit(mats)
    build_side_and_rear_fenders(mats)
    build_engine_and_thrusters(mats)
    build_rear_wing(mats)
    build_front_bullbar_and_lights(mats)
    build_rocket_league_wheels(mats)
    setup_environment_and_camera()

    blend_file = "/Users/elijahjohnson/67/nothing/nah/leuge of rockets/rocket_league_car.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"Saved master car scene to {blend_file}")

    render_file = "/Users/elijahjohnson/67/nothing/nah/leuge of rockets/blueprint_car_render.png"
    bpy.context.scene.render.filepath = render_file
    print(f"Rendering hero beauty shot to {render_file}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render complete: {render_file}")

if __name__ == "__main__":
    main()
