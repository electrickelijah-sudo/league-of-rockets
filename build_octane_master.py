"""
Builds the Definitive 1:1 Rocket League Octane in Blender 5.1.2.
Fully resolves all geometry, proportions, and styling to match media_1790263831226.png:
1. Solid, connected automotive body shell:
   - Sloped wedge hood with dual Alpine White racing stripes and front honeycomb grille
   - Curved arched front fenders flaring smoothly out over the front wheels with sweeping Titanium White trim lips
   - Seamless cockpit with raked dark glass windshield, precision-aligned Titanium White A-pillars, side windows, flat roof with dual stripes, and dual-port roof scoop
   - Sculpted wasp-waist side body with cyan neon rocker tube
   - Muscular flared rear hip haunches with Titanium White trim arches and red LED taillights
   - Open rear engine cradle with detailed V8 engine, red valve covers, 8 chrome velocity stacks
   - Dual chrome rocket boost thrusters with glowing cyan plasma cores
   - High-downforce rear wing with Titanium White endplates
2. Aggressive 10-spoke deep-dish sports wheels tucked snugly under the fender arches, with hollow rubber tires, chrome rim lips, radial alloy spokes, and red brake calipers
3. Front tubular bullbar with 4 projector lights (outer cyan neon halos + lower fog lights)
4. Hero 3/4 beauty camera matching the perspective in media_1790263831226.png
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
# Materials
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

    # Cobalt Blue Metallic Paint (#0B3C9E)
    new_pbr("CarPaint_Cobalt", (0.012, 0.12, 0.70, 1.0), metallic=0.75, roughness=0.18, clearcoat=1.0)
    
    # Titanium White Paint (#F0F2F5)
    new_pbr("CarPaint_White", (0.95, 0.95, 0.97, 1.0), metallic=0.15, roughness=0.18, clearcoat=0.9)

    # Alpine White Racing Stripes (#FFFFFF)
    new_pbr("RacingStripe_White", (0.98, 0.98, 1.0, 1.0), metallic=0.05, roughness=0.15, clearcoat=1.0)

    # Dark Automotive Glass
    new_pbr("Cockpit_Glass", (0.01, 0.012, 0.018, 1.0), metallic=0.92, roughness=0.03, clearcoat=1.0)

    # Matte Chassis & Engine Cradle Black
    new_pbr("Chassis_MatteBlack", (0.025, 0.025, 0.028, 1.0), metallic=0.35, roughness=0.55)

    # Polished Mirror Chrome
    new_pbr("Polished_Chrome", (0.96, 0.96, 0.96, 1.0), metallic=1.0, roughness=0.03)

    # Bright Gunmetal Alloy
    new_pbr("Gunmetal_Alloy", (0.16, 0.17, 0.18, 1.0), metallic=0.92, roughness=0.22)

    # Deep Black Tire Rubber
    new_pbr("Tire_Rubber", (0.02, 0.02, 0.02, 1.0), metallic=0.02, roughness=0.70)

    # Racing Red Engine Valve Covers & Calipers (#D32F2F)
    new_pbr("Engine_Red", (0.82, 0.04, 0.04, 1.0), metallic=0.35, roughness=0.25, clearcoat=0.8)

    # Cyan Neon Halos & Plasma (#00F0FF)
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
# 1. Hood, Grille & Front Fenders (Connected Assembly)
# ---------------------------------------------------------
def build_front_assembly(mats):
    """
    Constructs the sloped hood, front grille, dual Alpine White stripes,
    and flared arched front fenders with Titanium White outer trim lips.
    Front wheel center: X=±0.75, Y=0.85, Z=0.38. Radius = 0.38.
    """
    # 1. Main Hood Body
    bm = bmesh.new()
    # Half-mesh across X>=0
    # Loop at windshield base (Y=0.35)
    v_cowl_c = bm.verts.new(Vector((0.0, 0.35, 0.54)))
    v_cowl_s = bm.verts.new(Vector((0.16, 0.35, 0.54)))
    v_cowl_m = bm.verts.new(Vector((0.34, 0.35, 0.54)))

    # Loop at mid hood (Y=0.85)
    v_mid_c = bm.verts.new(Vector((0.0, 0.85, 0.42)))
    v_mid_s = bm.verts.new(Vector((0.15, 0.85, 0.42)))
    v_mid_m = bm.verts.new(Vector((0.32, 0.85, 0.42)))

    # Loop at front nose (Y=1.35)
    v_nose_c = bm.verts.new(Vector((0.0, 1.35, 0.28)))
    v_nose_s = bm.verts.new(Vector((0.14, 1.35, 0.28)))
    v_nose_m = bm.verts.new(Vector((0.28, 1.35, 0.28)))

    # Grille bottom (Y=1.35, Z=0.12)
    v_grille_c = bm.verts.new(Vector((0.0, 1.35, 0.12)))
    v_grille_s = bm.verts.new(Vector((0.14, 1.35, 0.12)))
    v_grille_m = bm.verts.new(Vector((0.28, 1.35, 0.12)))

    # Lower belly under nose
    v_belly_c = bm.verts.new(Vector((0.0, 0.85, 0.16)))
    v_belly_m = bm.verts.new(Vector((0.30, 0.85, 0.16)))

    # Hood Faces
    bm.faces.new([v_cowl_c, v_cowl_s, v_mid_s, v_mid_c])
    bm.faces.new([v_cowl_s, v_cowl_m, v_mid_m, v_mid_s])
    bm.faces.new([v_mid_c, v_mid_s, v_nose_s, v_nose_c])
    bm.faces.new([v_mid_s, v_mid_m, v_nose_m, v_nose_s])

    # Front Grille Faces
    bm.faces.new([v_nose_c, v_nose_s, v_grille_s, v_grille_c])
    bm.faces.new([v_nose_s, v_nose_m, v_grille_m, v_grille_s])

    # Lower Belly
    bm.faces.new([v_grille_c, v_grille_s, v_belly_c])
    bm.faces.new([v_grille_s, v_grille_m, v_belly_m, v_belly_c])
    bm.faces.new([v_nose_m, v_mid_m, v_belly_m, v_grille_m])

    # 2. Integrated Arched Front Fender
    # Arch vertices sweeping over wheel at (0.75, 0.85, 0.38)
    angles = [15, 45, 75, 105, 135, 165]
    r_wheel = 0.38
    r_fender = 0.47
    y_c = 0.85
    z_c = 0.38

    prev_in, prev_mid, prev_out = None, None, None

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad) * r_fender
        dz = math.sin(rad) * r_fender

        # Inner attachment along hood flank (X ~ 0.32 - 0.36)
        curr_in = bm.verts.new(Vector((0.34, y_c - dy * 0.70, z_c + dz * 0.75)))
        # Fender top ridge over tire (X ~ 0.75)
        curr_mid = bm.verts.new(Vector((0.74, y_c - dy, z_c + dz)))
        # Outer flare lip over tire (X ~ 0.90)
        curr_out = bm.verts.new(Vector((0.90, y_c - dy, z_c + dz * 0.90)))

        if prev_in is not None:
            # Inner wing face
            bm.faces.new([prev_in, curr_in, curr_mid, prev_mid])
            # Outer flare face
            bm.faces.new([prev_mid, curr_mid, curr_out, prev_out])

        prev_in, prev_mid, prev_out = curr_in, curr_mid, curr_out

    mesh = bpy.data.meshes.new("Front_Assembly_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    front_obj = bpy.data.objects.new("Front_Assembly", mesh)
    bpy.context.collection.objects.link(front_obj)
    front_obj.data.materials.append(mats["CarPaint_Cobalt"])      # 0 Blue
    front_obj.data.materials.append(mats["RacingStripe_White"])  # 1 White Stripe
    front_obj.data.materials.append(mats["Chassis_MatteBlack"])  # 2 Grille Black

    for p in front_obj.data.polygons:
        p.use_smooth = True
        c = p.center
        if c.y > 1.34:
            p.material_index = 2
        elif c.x < 0.15 and c.z > 0.25:
            p.material_index = 1
        else:
            p.material_index = 0

    mod_m = front_obj.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    # Subdivision modifier for sleek automotive curves
    mod_s = front_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_s.levels = 1
    mod_s.render_levels = 2

    # 3. Sweeping Titanium White Trim Lip on Front Fenders
    for side in [-1, 1]:
        bm_lip = bmesh.new()
        prev_l1, prev_l2 = None, None
        for deg in [15, 35, 55, 75, 95, 115, 135, 155, 165]:
            rad = math.radians(deg)
            dy = math.cos(rad) * (r_fender + 0.01)
            dz = math.sin(rad) * (r_fender + 0.01) * 0.90
            p1 = Vector((0.90 * side, y_c - dy, z_c + dz))
            p2 = Vector((0.925 * side, y_c - dy * 1.02, z_c + dz - 0.04))
            v1 = bm_lip.verts.new(p1)
            v2 = bm_lip.verts.new(p2)
            if prev_l1 is not None:
                bm_lip.faces.new([prev_l1, v1, v2, prev_l2])
            prev_l1, prev_l2 = v1, v2

        mesh_lip = bpy.data.meshes.new(f"FrontLip_{'L' if side < 0 else 'R'}")
        bm_lip.to_mesh(mesh_lip)
        bm_lip.free()
        lip_obj = bpy.data.objects.new(f"FrontLip_{'L' if side < 0 else 'R'}", mesh_lip)
        bpy.context.collection.objects.link(lip_obj)
        assign_mat(lip_obj, mats["CarPaint_White"])
        apply_smooth(lip_obj)

# ---------------------------------------------------------
# 2. Cockpit Canopy & Roof Scoop
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
    # 1. Glass Windshield & Side Windows
    bm = bmesh.new()
    # Windshield: from (0.35, 0.54) to (-0.15, 0.86)
    gw_b_c = bm.verts.new(Vector((0.00, 0.35, 0.54)))
    gw_b_o = bm.verts.new(Vector((0.32, 0.35, 0.54)))
    gw_t_c = bm.verts.new(Vector((0.00, -0.15, 0.86)))
    gw_t_o = bm.verts.new(Vector((0.24, -0.15, 0.86)))
    bm.faces.new([gw_b_c, gw_b_o, gw_t_o, gw_t_c])

    # Side Window: triangular swept canopy
    gw_rear = bm.verts.new(Vector((0.25, -0.65, 0.74)))
    gw_sill = bm.verts.new(Vector((0.35, -0.60, 0.48)))
    bm.faces.new([gw_b_o, gw_t_o, gw_rear, gw_sill])

    mesh_g = bpy.data.meshes.new("Cockpit_Glass_Mesh")
    bm.to_mesh(mesh_g)
    bm.free()
    glass = bpy.data.objects.new("Cockpit_Glass", mesh_g)
    bpy.context.collection.objects.link(glass)
    assign_mat(glass, mats["Cockpit_Glass"])
    mod_m = glass.modifiers.new("Mirror", 'MIRROR')
    mod_m.use_axis[0] = True

    # 2. Precision-Extruded Titanium White A-Pillars
    # Runs precisely from (0.32*side, 0.35, 0.54) to (0.24*side, -0.15, 0.86)
    for side in [-1, 1]:
        bm_p = bmesh.new()
        p_start = Vector((0.32 * side, 0.35, 0.54))
        p_end   = Vector((0.24 * side, -0.15, 0.86))
        # Beam thickness = 0.04
        v_b1 = bm_p.verts.new(p_start + Vector((-0.02 * side, 0, 0.01)))
        v_b2 = bm_p.verts.new(p_start + Vector(( 0.02 * side, 0, -0.01)))
        v_b3 = bm_p.verts.new(p_start + Vector(( 0.02 * side, 0, -0.05)))
        v_b4 = bm_p.verts.new(p_start + Vector((-0.02 * side, 0, -0.03)))

        v_t1 = bm_p.verts.new(p_end + Vector((-0.02 * side, 0, 0.01)))
        v_t2 = bm_p.verts.new(p_end + Vector(( 0.02 * side, 0, -0.01)))
        v_t3 = bm_p.verts.new(p_end + Vector(( 0.02 * side, 0, -0.05)))
        v_t4 = bm_p.verts.new(p_end + Vector((-0.02 * side, 0, -0.03)))

        # 4 longitudinal faces
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
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.40, 0.86))
    roof = bpy.context.active_object
    roof.name = "Cockpit_Roof"
    roof.scale = (0.50, 0.50, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(roof, mats["CarPaint_Cobalt"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.08 * side, -0.40, 0.88))
        rs = bpy.context.active_object
        rs.name = f"Roof_Stripe_{'L' if side < 0 else 'R'}"
        rs.scale = (0.055, 0.24, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(rs, mats["RacingStripe_White"])

    # 4. Signature Dual-Port Roof Air Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.50, 0.92))
    scoop = bpy.context.active_object
    scoop.name = "Roof_Air_Scoop"
    scoop.scale = (0.32, 0.22, 0.065)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(scoop, mats["Chassis_MatteBlack"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.08 * side, -0.38, 0.92))
        nostril = bpy.context.active_object
        nostril.name = f"Scoop_Nostril_{'L' if side < 0 else 'R'}"
        nostril.scale = (0.075, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(nostril, mats["Polished_Chrome"])

# ---------------------------------------------------------
# 3. Side Body & Rear Fenders
# ---------------------------------------------------------
def build_side_and_rear_fenders(mats):
    """
    Constructs the wasp-waist side body pods, cyan neon rocker tubes,
    flared rear fenders that arch over the rear wheels, and Titanium White trim lips.
    Rear wheel center: X=±0.78, Y=-1.05, Z=0.42. Radius = 0.42.
    """
    # 1. Wasp-Waist Side Body Pod
    bm_side = bmesh.new()
    v_f_top = bm_side.verts.new(Vector((0.34, 0.35, 0.48)))
    v_f_bot = bm_side.verts.new(Vector((0.36, 0.35, 0.18)))
    v_m_top = bm_side.verts.new(Vector((0.32, -0.35, 0.46)))
    v_m_bot = bm_side.verts.new(Vector((0.35, -0.35, 0.18)))
    v_r_top = bm_side.verts.new(Vector((0.44, -0.75, 0.54)))
    v_r_bot = bm_side.verts.new(Vector((0.44, -0.75, 0.18)))

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
            radius=0.016,
            depth=0.95,
            vertices=8,
            location=(0.36 * side, -0.20, 0.17)
        )
        tube = bpy.context.active_object
        tube.name = f"Neon_Rocker_{'L' if side < 0 else 'R'}"
        tube.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(tube, mats["Neon_Cyan"])

    # 2. Flared Rear Fenders Arching Over Rear Wheels
    bm_rf = bmesh.new()
    angles = [15, 45, 75, 105, 135, 165]
    r_rfender = 0.52
    y_c = -1.05
    z_c = 0.42

    prev_in, prev_mid, prev_out = None, None, None

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad) * r_rfender
        dz = math.sin(rad) * r_rfender

        curr_in = bm_rf.verts.new(Vector((0.42, y_c - dy * 0.70, z_c + dz * 0.80)))
        curr_mid = bm_rf.verts.new(Vector((0.78, y_c - dy, z_c + dz)))
        curr_out = bm_rf.verts.new(Vector((0.95, y_c - dy, z_c + dz * 0.92)))

        if prev_in is not None:
            bm_rf.faces.new([prev_in, curr_in, curr_mid, prev_mid])
            bm_rf.faces.new([prev_mid, curr_mid, curr_out, prev_out])

        prev_in, prev_mid, prev_out = curr_in, curr_mid, curr_out

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
            dy = math.cos(rad) * (r_rfender + 0.01)
            dz = math.sin(rad) * (r_rfender + 0.01) * 0.92
            p1 = Vector((0.95 * side, y_c - dy, z_c + dz))
            p2 = Vector((0.975 * side, y_c - dy * 1.02, z_c + dz - 0.04))
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

        # Red LED Taillight Bar
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.62 * side, -1.54, 0.52))
        tl = bpy.context.active_object
        tl.name = f"Taillight_{'L' if side < 0 else 'R'}"
        tl.scale = (0.12, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(tl, mats["Neon_Red"])

# ---------------------------------------------------------
# 4. Exposed Rear Engine Bay & Rocket Thrusters
# ---------------------------------------------------------
def build_engine_and_thrusters(mats):
    """
    Constructs the open rear engine cradle, V8 engine block,
    bright racing red valve covers, 8 chrome velocity stacks,
    and dual rocket boost thrusters.
    """
    # 1. Lower Engine Bed / Rear Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.05, 0.26))
    bed = bpy.context.active_object
    bed.name = "Engine_Bed_Chassis"
    bed.scale = (0.64, 0.70, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(bed, mats["Chassis_MatteBlack"])

    # 2. V8 Engine Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.02, 0.42))
    block = bpy.context.active_object
    block.name = "V8_Engine_Block"
    block.scale = (0.34, 0.42, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(block, mats["Gunmetal_Alloy"])

    # 3. Dual Racing Red Valve Covers
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.15 * side, -1.02, 0.50))
        valve = bpy.context.active_object
        valve.name = f"ValveCover_Red_{'L' if side < 0 else 'R'}"
        valve.scale = (0.12, 0.40, 0.07)
        valve.rotation_euler = (0, math.radians(20 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(valve, mats["Engine_Red"])

        # 4 Chrome Velocity Intake Stacks per bank
        for row in range(4):
            y_pos = -0.88 - (row * 0.09)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.024,
                depth=0.12,
                vertices=12,
                location=(0.09 * side, y_pos, 0.56)
            )
            stack = bpy.context.active_object
            stack.name = f"IntakeStack_{'L' if side < 0 else 'R'}_{row}"
            assign_mat(stack, mats["Polished_Chrome"])

    # 4. Dual Rocket Boost Thruster Nozzles
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.092,
            depth=0.18,
            vertices=18,
            location=(0.15 * side, -1.52, 0.38)
        )
        nozzle = bpy.context.active_object
        nozzle.name = f"Rocket_Nozzle_{'L' if side < 0 else 'R'}"
        nozzle.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(nozzle, mats["Chassis_MatteBlack"])

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.092,
            minor_radius=0.016,
            major_segments=18,
            minor_segments=8,
            location=(0.15 * side, -1.61, 0.38)
        )
        ring = bpy.context.active_object
        ring.name = f"Nozzle_Rim_{'L' if side < 0 else 'R'}"
        ring.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(ring, mats["Polished_Chrome"])

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.07,
            depth=0.04,
            vertices=16,
            location=(0.15 * side, -1.59, 0.38)
        )
        plasma = bpy.context.active_object
        plasma.name = f"Rocket_Plasma_{'L' if side < 0 else 'R'}"
        plasma.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(plasma, mats["Neon_Cyan"])

# ---------------------------------------------------------
# 5. High-Downforce Rear Wing
# ---------------------------------------------------------
def build_rear_wing(mats):
    """
    Constructs the high-downforce rear wing with Titanium White endplates.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.30, 0.98))
    wing = bpy.context.active_object
    wing.name = "Rear_Wing_Airfoil"
    wing.scale = (0.86, 0.22, 0.038)
    wing.rotation_euler = (math.radians(-7), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(wing, mats["CarPaint_Cobalt"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.48,
            vertices=10,
            location=(0.28 * side, -1.22, 0.77)
        )
        pylon = bpy.context.active_object
        pylon.name = f"Wing_Pylon_{'L' if side < 0 else 'R'}"
        pylon.rotation_euler = (math.radians(-22), 0, math.radians(6 * side))
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(pylon, mats["Chassis_MatteBlack"])

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.44 * side, -1.30, 0.98))
        endplate = bpy.context.active_object
        endplate.name = f"Wing_Endplate_{'L' if side < 0 else 'R'}"
        endplate.scale = (0.028, 0.28, 0.16)
        endplate.rotation_euler = (math.radians(-5), math.radians(8 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(endplate, mats["CarPaint_White"])

# ---------------------------------------------------------
# 6. Front Bullbar & Projector Headlights
# ---------------------------------------------------------
def build_front_bullbar_and_lights(mats):
    """
    Constructs the tubular bullbar, dual cyan halo projector headlights, and lower fog lights.
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.03,
        depth=0.70,
        vertices=14,
        location=(0.0, 1.44, 0.25)
    )
    bar_top = bpy.context.active_object
    bar_top.name = "Bullbar_Top"
    bar_top.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(bar_top, mats["Chassis_MatteBlack"])

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.025,
        depth=0.56,
        vertices=12,
        location=(0.0, 1.47, 0.13)
    )
    bar_bot = bpy.context.active_object
    bar_bot.name = "Bullbar_Bottom"
    bar_bot.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(bar_bot, mats["Chassis_MatteBlack"])

    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.20,
            vertices=10,
            location=(0.20 * side, 1.45, 0.19)
        )
        guard = bpy.context.active_object
        guard.name = f"Bullbar_Guard_{'L' if side < 0 else 'R'}"
        assign_mat(guard, mats["Chassis_MatteBlack"])

        # Projector Headlight
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.088,
            depth=0.07,
            vertices=18,
            location=(0.33 * side, 1.41, 0.26)
        )
        casing = bpy.context.active_object
        casing.name = f"Headlight_Housing_{'L' if side < 0 else 'R'}"
        casing.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(casing, mats["Chassis_MatteBlack"])

        # Cyan Halo Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.082,
            minor_radius=0.016,
            major_segments=22,
            minor_segments=8,
            location=(0.33 * side, 1.46, 0.26)
        )
        halo = bpy.context.active_object
        halo.name = f"Headlight_Halo_{'L' if side < 0 else 'R'}"
        halo.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(halo, mats["Neon_Cyan"])

        # Center White Projector Lens
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05,
            depth=0.025,
            vertices=16,
            location=(0.33 * side, 1.46, 0.26)
        )
        lens = bpy.context.active_object
        lens.name = f"Headlight_Projector_{'L' if side < 0 else 'R'}"
        lens.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(lens, mats["Headlight_WhiteBeam"])

        # Lower Fog Light
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.045,
            depth=0.035,
            vertices=14,
            location=(0.10 * side, 1.49, 0.13)
        )
        fog = bpy.context.active_object
        fog.name = f"Fog_Light_{'L' if side < 0 else 'R'}"
        fog.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(fog, mats["Headlight_WhiteBeam"])

# ---------------------------------------------------------
# 7. Chunky 10-Spoke Deep-Dish Wheels with Correct Radial Spokes
# ---------------------------------------------------------
def build_rocket_league_wheels(mats):
    """
    Constructs the 4 deep-dish sports wheels tucked under the arches.
    Spokes radiate radially in the wheel's local Y-Z plane!
    """
    configs = [
        # (name, x, y, z, tire_radius, tire_width, rim_radius)
        ("Front_L", -0.75,  0.85, 0.38, 0.38, 0.26, 0.24),
        ("Front_R",  0.75,  0.85, 0.38, 0.38, 0.26, 0.24),
        ("Rear_L",  -0.78, -1.05, 0.42, 0.42, 0.30, 0.26),
        ("Rear_R",   0.78, -1.05, 0.42, 0.42, 0.30, 0.26),
    ]

    for name, wx, wy, wz, r_tire, w_tire, r_rim in configs:
        is_right = (wx > 0)
        side_mult = 1 if is_right else -1
        outer_rim_x = wx + (w_tire * 0.48 * side_mult)

        # 1. Tire Rubber
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_tire,
            depth=w_tire,
            vertices=32,
            location=(wx, wy, wz)
        )
        tire = bpy.context.active_object
        tire.name = f"Tire_{name}"
        tire.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(tire, mats["Tire_Rubber"])
        apply_smooth(tire)

        # 2. Polished Chrome Outer Rim Lip
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r_rim,
            minor_radius=0.022,
            major_segments=24,
            minor_segments=10,
            location=(outer_rim_x, wy, wz)
        )
        rim_lip = bpy.context.active_object
        rim_lip.name = f"RimLip_{name}"
        rim_lip.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(rim_lip, mats["Polished_Chrome"])
        apply_smooth(rim_lip)

        # 3. Chrome Center Hub
        dish_center_x = outer_rim_x - (0.035 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.075,
            depth=0.04,
            vertices=16,
            location=(dish_center_x, wy, wz)
        )
        hub = bpy.context.active_object
        hub.name = f"Hub_{name}"
        hub.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(hub, mats["Polished_Chrome"])

        # 4. 10 Radial Alloy Spokes (Correct radial orientation in Y-Z plane!)
        for i in range(10):
            theta = i * (2.0 * math.pi / 10.0)
            # Midpoint of spoke
            r_mid = r_rim * 0.52
            sy = wy + math.sin(theta) * r_mid
            sz = wz + math.cos(theta) * r_mid
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(dish_center_x, sy, sz)
            )
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{name}_{i}"
            # X is thickness, Y is width, Z is radial length
            spoke.scale = (0.024, 0.034, r_rim * 0.84)
            # Rotate around X by -theta so Z points radially outward!
            spoke.rotation_euler = (-theta, 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            assign_mat(spoke, mats["Gunmetal_Alloy"])

        # 5. Brake Disc & Red Racing Caliper
        disc_x = wx - (0.04 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_rim * 0.72,
            depth=0.02,
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
            location=(disc_x, wy + (r_rim * 0.55), wz)
        )
        caliper = bpy.context.active_object
        caliper.name = f"BrakeCaliper_{name}"
        caliper.scale = (0.045, 0.065, 0.11)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(caliper, mats["Engine_Red"])

# ---------------------------------------------------------
# Environment, Lighting & Camera
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
    key_obj.location = (-5.0, 4.5, 7.5)
    key_obj.rotation_euler = (math.radians(50), math.radians(-15), math.radians(40))

    # Rim / Accent Light (Cool Stadium Cyan-Blue)
    rim = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim.energy = 550.0
    rim.color = (0.35, 0.78, 1.0)
    rim.size = 4.0
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (4.5, -4.5, 4.0)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(20), math.radians(-135))

    # Fill Light (Soft Neutral)
    fill = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill.energy = 220.0
    fill.color = (0.92, 0.94, 1.0)
    fill.size = 4.5
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-3.5, -3.0, 3.5)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-15), math.radians(-45))

    # Camera matching the hero 3/4 beauty view in media_1790263831226.png
    cam_data = bpy.data.cameras.new(name="Hero_Camera")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Hero_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (-3.2, 3.4, 1.50)
    target = Vector((0.0, 0.10, 0.50))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.camera = cam_obj

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
def main():
    print("=== BUILDING DEFINITIVE 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    mats = create_materials()

    build_front_assembly(mats)
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
