"""
Builds the Perfect Rocket League Octane in Blender 5.1.2.
Exact 1:1 match to media_1790263831226.png:
- Wide aggressive stance with wheels tucked underneath high-clearance arched fenders
- Sweeping Titanium White trim lips framing both front and rear wheel arches
- Raked angular cockpit canopy with flat dark glass windshield, Titanium White A-pillars, side windows, dual-port roof scoop
- Sloped wedge hood with dual Alpine White racing stripes running from nose to windshield
- Sculpted wasp-waist side pods with cyan neon rocker tube
- Open rear engine cradle with exposed V8 engine (bright red valve covers, 8 chrome velocity stacks)
- Dual chrome rocket boost thrusters with glowing cyan plasma cores
- High-downforce rear wing with Titanium White endplates
- 10-spoke deep-dish gunmetal alloy wheels with chrome rim lips and red brake calipers
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

    # Rocket League Cobalt Blue Gloss Paint
    new_pbr("CarPaint_Cobalt", (0.012, 0.11, 0.68, 1.0), metallic=0.75, roughness=0.20, clearcoat=1.0)
    
    # Titanium White Body Trim & Endplates
    new_pbr("CarPaint_White", (0.95, 0.95, 0.97, 1.0), metallic=0.15, roughness=0.20, clearcoat=0.9)

    # Alpine White Racing Stripes
    new_pbr("RacingStripe_White", (0.98, 0.98, 0.99, 1.0), metallic=0.05, roughness=0.15, clearcoat=1.0)

    # Dark Automotive Glass
    new_pbr("Cockpit_Glass", (0.012, 0.015, 0.02, 1.0), metallic=0.92, roughness=0.04, clearcoat=1.0)

    # Chassis & Matte Trim
    new_pbr("Chassis_MatteBlack", (0.025, 0.025, 0.028, 1.0), metallic=0.25, roughness=0.55)

    # Polished Chrome
    new_pbr("Polished_Chrome", (0.95, 0.95, 0.95, 1.0), metallic=1.0, roughness=0.03)

    # Gunmetal Alloy
    new_pbr("Gunmetal_Alloy", (0.12, 0.125, 0.13, 1.0), metallic=0.90, roughness=0.25)

    # Tire Rubber
    new_pbr("Tire_Rubber", (0.02, 0.02, 0.02, 1.0), metallic=0.02, roughness=0.65)

    # Engine Red Valve Covers & Calipers
    new_pbr("Engine_Red", (0.82, 0.03, 0.03, 1.0), metallic=0.35, roughness=0.25, clearcoat=0.8)

    # Headlight Halo Cyan Neon
    new_pbr("Neon_Cyan", (0.0, 0.88, 1.0, 1.0), emission_color=(0.0, 0.88, 1.0, 1.0), emission_strength=15.0)

    # Headlight Inner Bright White Projector
    new_pbr("Headlight_WhiteBeam", (0.95, 0.98, 1.0, 1.0), emission_color=(0.95, 0.98, 1.0, 1.0), emission_strength=20.0)

    # Rocket Boost Core Cyan Plasma
    new_pbr("Rocket_Plasma", (0.0, 0.92, 1.0, 1.0), emission_color=(0.0, 0.92, 1.0, 1.0), emission_strength=25.0)

    # Brake Light Neon Red
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
# 1. Sculpted Hood & Nose with Dual Alpine White Stripes
# ---------------------------------------------------------
def build_hood_and_nose(mats):
    """
    Constructs the wide sloped hood with dual Alpine White racing stripes and front honeycomb grille.
    """
    bm = bmesh.new()
    # Hood vertices (half-mesh, will mirror or build symmetric)
    # Windshield base at Y=0.35, Z=0.54, nose at Y=1.35, Z=0.28
    v_cowl_c = bm.verts.new(Vector((0.0, 0.35, 0.54)))
    v_cowl_s = bm.verts.new(Vector((0.15, 0.35, 0.54)))
    v_cowl_o = bm.verts.new(Vector((0.34, 0.35, 0.54)))

    v_mid_c = bm.verts.new(Vector((0.0, 0.85, 0.42)))
    v_mid_s = bm.verts.new(Vector((0.14, 0.85, 0.42)))
    v_mid_o = bm.verts.new(Vector((0.30, 0.85, 0.42)))

    v_nose_c = bm.verts.new(Vector((0.0, 1.35, 0.28)))
    v_nose_s = bm.verts.new(Vector((0.12, 1.35, 0.28)))
    v_nose_o = bm.verts.new(Vector((0.26, 1.35, 0.28)))

    # Lower nose / grille vertices
    v_grille_c = bm.verts.new(Vector((0.0, 1.35, 0.12)))
    v_grille_s = bm.verts.new(Vector((0.12, 1.35, 0.12)))
    v_grille_o = bm.verts.new(Vector((0.26, 1.35, 0.12)))

    # Hood faces
    f_stripe_rear = bm.faces.new([v_cowl_c, v_cowl_s, v_mid_s, v_mid_c])
    f_outer_rear  = bm.faces.new([v_cowl_s, v_cowl_o, v_mid_o, v_mid_s])
    f_stripe_fwd  = bm.faces.new([v_mid_c, v_mid_s, v_nose_s, v_nose_c])
    f_outer_fwd   = bm.faces.new([v_mid_s, v_mid_o, v_nose_o, v_nose_s])

    # Front Grille faces
    f_grille_in  = bm.faces.new([v_nose_c, v_nose_s, v_grille_s, v_grille_c])
    f_grille_out = bm.faces.new([v_nose_s, v_nose_o, v_grille_o, v_grille_s])

    # Lower belly under nose
    v_belly_c = bm.verts.new(Vector((0.0, 0.85, 0.18)))
    v_belly_o = bm.verts.new(Vector((0.28, 0.85, 0.18)))
    bm.faces.new([v_grille_c, v_grille_s, v_belly_c])
    bm.faces.new([v_grille_s, v_grille_o, v_belly_o, v_belly_c])

    # Side of hood down to belly
    bm.faces.new([v_nose_o, v_mid_o, v_belly_o, v_grille_o])

    mesh = bpy.data.meshes.new("Hood_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    hood = bpy.data.objects.new("Octane_Hood", mesh)
    bpy.context.collection.objects.link(hood)

    # Materials: 0=Blue, 1=White Stripe, 2=Black Grille
    hood.data.materials.append(mats["CarPaint_Cobalt"])
    hood.data.materials.append(mats["RacingStripe_White"])
    hood.data.materials.append(mats["Chassis_MatteBlack"])

    # Face material assignment
    for p in hood.data.polygons:
        p.use_smooth = True
        c = p.center
        if c.y > 1.34: # front grille
            p.material_index = 2
        elif c.x < 0.14: # center stripe
            p.material_index = 1
        else:
            p.material_index = 0

    # Mirror Modifier
    mod_m = hood.modifiers.new(name="Mirror", type='MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    return hood

# ---------------------------------------------------------
# 2. Front Flared Arched Fenders with Titanium White Lips
# ---------------------------------------------------------
def build_front_fenders(mats):
    """
    Constructs the wide arched front fenders that flare high over the front wheels,
    complete with sweeping Titanium White trim lips.
    Front wheel center: X=±0.75, Y=0.85, Z=0.38. Radius = 0.38.
    Fender arch spans from Y=1.30 to Y=0.40, arching over Z=0.74, flaring out to X=0.92!
    """
    bm = bmesh.new()
    
    # Generate arch profile over front wheel
    # 7 key angles along the arch from front (20 deg) to apex (90 deg) to rear (160 deg)
    angles = [20, 45, 70, 95, 120, 145, 165]
    r_inner = 0.44  # body attachment
    r_outer = 0.50  # outer flare over tire
    y_c = 0.85
    z_c = 0.38
    x_in = 0.32
    x_out = 0.90

    inner_verts = []
    outer_verts = []
    lip_verts = []

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad)
        dz = math.sin(rad)
        # Inner edge connecting to hood/chassis
        vi = bm.verts.new(Vector((x_in, y_c - dy * r_inner, z_c + dz * r_inner * 0.85)))
        # Outer flare arching over tire
        vo = bm.verts.new(Vector((x_out, y_c - dy * r_outer, z_c + dz * r_outer * 0.96)))
        # Titanium White trim lip (curled down)
        vl = bm.verts.new(Vector((x_out + 0.025, y_c - dy * (r_outer + 0.03), z_c + dz * (r_outer + 0.03) * 0.96 - 0.03)))
        inner_verts.append(vi)
        outer_verts.append(vo)
        lip_verts.append(vl)

    # Create quad faces
    for i in range(len(angles) - 1):
        # Blue fender arch top
        bm.faces.new([inner_verts[i], outer_verts[i], outer_verts[i+1], inner_verts[i+1]])
        # Titanium White trim lip
        bm.faces.new([outer_verts[i], lip_verts[i], lip_verts[i+1], outer_verts[i+1]])

    mesh = bpy.data.meshes.new("Front_Fender_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    fender = bpy.data.objects.new("Front_Fenders", mesh)
    bpy.context.collection.objects.link(fender)

    fender.data.materials.append(mats["CarPaint_Cobalt"]) # 0
    fender.data.materials.append(mats["CarPaint_White"])  # 1

    for p in fender.data.polygons:
        p.use_smooth = True
        # If face is near the outer lip, paint Titanium White
        if p.center.x > 0.82:
            p.material_index = 1
        else:
            p.material_index = 0

    mod_m = fender.modifiers.new(name="Mirror", type='MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    # Subdivision surface for sleek curves
    mod_s = fender.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_s.levels = 1
    mod_s.render_levels = 2

    return fender

# ---------------------------------------------------------
# 3. Cockpit Canopy with Dark Glass & Titanium White A-Pillars
# ---------------------------------------------------------
def build_cockpit_canopy(mats):
    """
    Constructs the authentic Octane cockpit:
    - Raked dark glass windshield
    - Swept Titanium White A-pillars
    - Flat roof with dual Alpine White stripes
    - Triangular side canopy windows
    - Dual-snorkel roof scoop
    """
    # 1. Dark Glass Windshield & Side Windows
    bm = bmesh.new()
    # Windshield: from (Y=0.35, Z=0.54) to (Y=-0.15, Z=0.86)
    w_b_c = bm.verts.new(Vector((0.00, 0.35, 0.54)))
    w_b_o = bm.verts.new(Vector((0.32, 0.35, 0.54)))
    w_t_c = bm.verts.new(Vector((0.00, -0.15, 0.86)))
    w_t_o = bm.verts.new(Vector((0.24, -0.15, 0.86)))
    bm.faces.new([w_b_c, w_b_o, w_t_o, w_t_c])

    # Side Window: triangular swept window
    w_side_rear = bm.verts.new(Vector((0.26, -0.65, 0.72)))
    w_side_sill = bm.verts.new(Vector((0.36, -0.60, 0.48)))
    bm.faces.new([w_b_o, w_t_o, w_side_rear, w_side_sill])

    mesh_g = bpy.data.meshes.new("Cockpit_Glass_Mesh")
    bm.to_mesh(mesh_g)
    bm.free()
    glass = bpy.data.objects.new("Cockpit_Glass", mesh_g)
    bpy.context.collection.objects.link(glass)
    assign_mat(glass, mats["Cockpit_Glass"])
    mod_m = glass.modifiers.new(name="Mirror", type='MIRROR')
    mod_m.use_axis[0] = True
    mod_m.use_clip = True

    # 2. Titanium White A-Pillars & Roof Trim Bars
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.035,
            depth=0.68,
            vertices=12,
            location=(0.28 * side, 0.10, 0.70)
        )
        p = bpy.context.active_object
        p.name = f"A_Pillar_{'L' if side < 0 else 'R'}"
        p.rotation_euler = (math.radians(-54), 0, math.radians(14 * side))
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(p, mats["CarPaint_White"])
        apply_smooth(p)

    # 3. Flat Blue Roof Deck with Dual White Stripes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.42, 0.86))
    roof = bpy.context.active_object
    roof.name = "Cockpit_Roof"
    roof.scale = (0.50, 0.48, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(roof, mats["CarPaint_Cobalt"])

    # Dual White Stripes on Roof
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.08 * side, -0.42, 0.88))
        rs = bpy.context.active_object
        rs.name = f"Roof_Stripe_{'L' if side < 0 else 'R'}"
        rs.scale = (0.055, 0.23, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(rs, mats["RacingStripe_White"])

    # 4. Signature Dual-Port Roof Air Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.52, 0.92))
    scoop = bpy.context.active_object
    scoop.name = "Roof_Air_Scoop"
    scoop.scale = (0.32, 0.22, 0.065)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(scoop, mats["Chassis_MatteBlack"])

    # Dual Chrome Nostrils
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.08 * side, -0.40, 0.92))
        nostril = bpy.context.active_object
        nostril.name = f"Scoop_Nostril_{'L' if side < 0 else 'R'}"
        nostril.scale = (0.075, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(nostril, mats["Polished_Chrome"])

# ---------------------------------------------------------
# 4. Side Body & Rear Fenders with Titanium White Trim Lips
# ---------------------------------------------------------
def build_side_body_and_rear_fenders(mats):
    """
    Constructs the wasp-waist side body pods, cyan neon rocker tubes,
    and flared rear fenders that arch over the rear wheels with Titanium White trim lips.
    Rear wheel center: X=±0.78, Y=-1.05, Z=0.42. Radius = 0.42.
    """
    # 1. Wasp-Waist Side Body Pod
    bm_side = bmesh.new()
    # Panel connecting front fender rear to rear fender front
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
    mod_m = side_body.modifiers.new(name="Mirror", type='MIRROR')
    mod_m.use_axis[0] = True

    # Subtle Cyan Neon Rocker Tube along side skirt
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.016,
            depth=0.90,
            vertices=8,
            location=(0.36 * side, -0.20, 0.17)
        )
        tube = bpy.context.active_object
        tube.name = f"Neon_Rocker_{'L' if side < 0 else 'R'}"
        tube.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(tube, mats["Neon_Cyan"])

    # 2. Flared Rear Fenders with Arched Titanium White Trim Lips
    bm_rf = bmesh.new()
    angles = [15, 40, 65, 90, 115, 140, 165]
    r_inner = 0.46
    r_outer = 0.54
    y_c = -1.05
    z_c = 0.42
    x_in = 0.40
    x_out = 0.94

    inner_verts = []
    outer_verts = []
    lip_verts = []

    for deg in angles:
        rad = math.radians(deg)
        dy = math.cos(rad)
        dz = math.sin(rad)
        vi = bm_rf.verts.new(Vector((x_in, y_c - dy * r_inner, z_c + dz * r_inner * 0.85)))
        vo = bm_rf.verts.new(Vector((x_out, y_c - dy * r_outer, z_c + dz * r_outer * 0.98)))
        vl = bm_rf.verts.new(Vector((x_out + 0.025, y_c - dy * (r_outer + 0.035), z_c + dz * (r_outer + 0.035) * 0.98 - 0.03)))
        inner_verts.append(vi)
        outer_verts.append(vo)
        lip_verts.append(vl)

    for i in range(len(angles) - 1):
        bm_rf.faces.new([inner_verts[i], outer_verts[i], outer_verts[i+1], inner_verts[i+1]])
        bm_rf.faces.new([outer_verts[i], lip_verts[i], lip_verts[i+1], outer_verts[i+1]])

    mesh_rf = bpy.data.meshes.new("Rear_Fender_Mesh")
    bm_rf.to_mesh(mesh_rf)
    bm_rf.free()

    rear_fender = bpy.data.objects.new("Rear_Fenders", mesh_rf)
    bpy.context.collection.objects.link(rear_fender)
    rear_fender.data.materials.append(mats["CarPaint_Cobalt"]) # 0
    rear_fender.data.materials.append(mats["CarPaint_White"])  # 1

    for p in rear_fender.data.polygons:
        p.use_smooth = True
        if p.center.x > 0.86:
            p.material_index = 1
        else:
            p.material_index = 0

    mod_m = rear_fender.modifiers.new(name="Mirror", type='MIRROR')
    mod_m.use_axis[0] = True

    mod_s = rear_fender.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_s.levels = 1
    mod_s.render_levels = 2

    # Red LED Taillight Bars on Rear Haunches
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.62 * side, -1.52, 0.52))
        tl = bpy.context.active_object
        tl.name = f"Taillight_{'L' if side < 0 else 'R'}"
        tl.scale = (0.12, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(tl, mats["Neon_Red"])

# ---------------------------------------------------------
# 5. Open Rear Engine Cradle, V8 Engine & Rocket Thrusters
# ---------------------------------------------------------
def build_engine_and_thrusters(mats):
    """
    Constructs the open rear engine cradle, detailed V8 engine, red valve covers,
    8 chrome velocity intake stacks, and dual rocket boost thrusters.
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

        # 4 Polished Chrome Velocity Stacks per bank
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
        # Outer Nozzle Bell
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

        # Chrome Beveled Trim Ring
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

        # Deep Glowing Cyan Plasma Core
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
        assign_mat(plasma, mats["Rocket_Plasma"])

# ---------------------------------------------------------
# 6. High-Downforce Rear Wing
# ---------------------------------------------------------
def build_rear_wing(mats):
    """
    Constructs the high-downforce rear wing with Titanium White endplates.
    """
    # Main Airfoil
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.30, 0.98))
    wing = bpy.context.active_object
    wing.name = "Rear_Wing_Airfoil"
    wing.scale = (0.86, 0.22, 0.038)
    wing.rotation_euler = (math.radians(-7), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(wing, mats["CarPaint_Cobalt"])

    # Raked Pylons & Titanium White Endplates
    for side in [-1, 1]:
        # Pylon
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

        # Swept Endplate in Titanium White
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.44 * side, -1.30, 0.98))
        endplate = bpy.context.active_object
        endplate.name = f"Wing_Endplate_{'L' if side < 0 else 'R'}"
        endplate.scale = (0.028, 0.28, 0.16)
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
    # 1. Upper Bullbar Tube
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

    # 2. Lower Bumper Skid Tube
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

    # 3. Bullbar Vertical Guards
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

    # 4. Projector Headlights with Glowing Cyan Halos
    for side in [-1, 1]:
        # Casing
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

        # Cyan Neon Halo Ring
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

    # 5. Lower Fog Lights
    for side in [-1, 1]:
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
# 8. Rocket League Deep-Dish 10-Spoke Wheels
# ---------------------------------------------------------
def build_rocket_league_wheels(mats):
    """
    Constructs the 4 deep-dish sports wheels with chunky tires and red calipers.
    Positioned snugly under the arched fenders!
    """
    configs = [
        # (name, x, y, z, tire_radius, tire_width, rim_radius)
        ("Front_L", -0.74,  0.85, 0.38, 0.38, 0.26, 0.24),
        ("Front_R",  0.74,  0.85, 0.38, 0.38, 0.26, 0.24),
        ("Rear_L",  -0.78, -1.05, 0.42, 0.42, 0.30, 0.26),
        ("Rear_R",   0.78, -1.05, 0.42, 0.42, 0.30, 0.26),
    ]

    for name, wx, wy, wz, r_tire, w_tire, r_rim in configs:
        side_mult = 1 if (wx > 0) else -1
        outer_face_x = wx + (w_tire * 0.50 * side_mult)

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
            minor_radius=0.024,
            major_segments=24,
            minor_segments=10,
            location=(outer_face_x, wy, wz)
        )
        rim_lip = bpy.context.active_object
        rim_lip.name = f"RimLip_{name}"
        rim_lip.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(rim_lip, mats["Polished_Chrome"])
        apply_smooth(rim_lip)

        # 3. Deep-Dish Gunmetal 10-Spoke Wheel Face
        dish_center_x = outer_face_x - (0.045 * side_mult)
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

        # 10 Radial Spokes in bright Gunmetal Alloy
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            spoke_y = wy + math.cos(angle) * (r_rim * 0.50)
            spoke_z = wz + math.sin(angle) * (r_rim * 0.50)
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(dish_center_x + (0.015 * side_mult), spoke_y, spoke_z)
            )
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{name}_{i}"
            spoke.scale = (0.018, 0.032, r_rim * 0.82)
            spoke.rotation_euler = (angle, 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            assign_mat(spoke, mats["Gunmetal_Alloy"])

        # 4. Brake Disc & Red Racing Caliper
        disc_x = wx - (0.035 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_rim * 0.70,
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
            location=(disc_x, wy + (r_rim * 0.52), wz)
        )
        caliper = bpy.context.active_object
        caliper.name = f"BrakeCaliper_{name}"
        caliper.scale = (0.045, 0.065, 0.11)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(caliper, mats["Engine_Red"])

# ---------------------------------------------------------
# Environment, Stadium Lighting & Camera
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

    # Floor with stadium grass/turf
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

    # Camera matching the EXACT hero 3/4 angle in media_1790263831226.png
    cam_data = bpy.data.cameras.new(name="Hero_Camera")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Hero_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (-3.1, 3.4, 1.50)
    target = Vector((0.0, 0.10, 0.50))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.camera = cam_obj

# ---------------------------------------------------------
# Main Routine
# ---------------------------------------------------------
def main():
    print("=== BUILDING PERFECT 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    mats = create_materials()

    build_hood_and_nose(mats)
    build_front_fenders(mats)
    build_cockpit_canopy(mats)
    build_side_body_and_rear_fenders(mats)
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
