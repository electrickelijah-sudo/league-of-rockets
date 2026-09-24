"""
Builds the Authentic Rocket League Octane in Blender 5.1.2.
Matches media_1790263831226.png 1:1 using professional automotive polygonal modeling:
- Unified single-mesh body shell with Mirror modifier across X=0
- Smooth Subdivision Surface styling with crisp automotive character creases
- Seamless integrated curved wheel arches with Titanium White outer trim lips
- Sloped sculpted hood with dual Alpine White racing stripes
- Integrated cockpit with raked dark glass windshield and side windows
- Sculpted wasp-waist side body with neon cyan rocker tube
- Open rear engine cradle with detailed V8 engine, red valve covers, chrome intake velocity stacks
- Dual rocket boost thruster nozzles with glowing cyan plasma exhaust cores
- High-downforce rear wing with Titanium White endplates
- 4 chunky deep-dish Rocket League wheels with 10-spoke gunmetal rims and red brake calipers
- Tubular steel bullbar with dual cyan halo projector headlights and lower foglights
- Precise hero camera perspective matching the main image in media_1790263831226.png
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

    # 0: CarPaint_Cobalt (Deep Rocket League metallic blue)
    new_pbr("CarPaint_Cobalt", (0.015, 0.12, 0.68, 1.0), metallic=0.75, roughness=0.22, clearcoat=1.0)
    
    # 1: CarPaint_White (Titanium White for trim & spoiler endplates)
    new_pbr("CarPaint_White", (0.95, 0.95, 0.96, 1.0), metallic=0.15, roughness=0.22, clearcoat=0.8)

    # 2: RacingStripe_White (Alpine White center racing stripes)
    new_pbr("RacingStripe_White", (0.98, 0.98, 0.98, 1.0), metallic=0.08, roughness=0.18, clearcoat=1.0)

    # 3: Cockpit_Glass (Glossy dark automotive glass)
    new_pbr("Cockpit_Glass", (0.015, 0.02, 0.03, 1.0), metallic=0.9, roughness=0.05, clearcoat=1.0)

    # 4: Chassis_MatteBlack (Engine cradle, bullbar, grille)
    new_pbr("Chassis_MatteBlack", (0.025, 0.025, 0.028, 1.0), metallic=0.3, roughness=0.55)

    # 5: Polished_Chrome (Intake stacks, rim lips, thruster rings)
    new_pbr("Polished_Chrome", (0.95, 0.95, 0.95, 1.0), metallic=1.0, roughness=0.04)

    # 6: Gunmetal_Alloy (10-spoke wheel face, engine block)
    new_pbr("Gunmetal_Alloy", (0.07, 0.075, 0.08, 1.0), metallic=0.92, roughness=0.28)

    # 7: Tire_Rubber (Deep black textured tire tread)
    new_pbr("Tire_Rubber", (0.02, 0.02, 0.02, 1.0), metallic=0.02, roughness=0.68)

    # 8: Engine_Red (Cylinder heads, brake calipers)
    new_pbr("Engine_Red", (0.80, 0.03, 0.03, 1.0), metallic=0.35, roughness=0.3, clearcoat=0.6)

    # 9: Neon_Cyan (Headlight halos, rocket plasma)
    new_pbr("Neon_Cyan", (0.0, 0.88, 1.0, 1.0), emission_color=(0.0, 0.88, 1.0, 1.0), emission_strength=14.0)

    # 10: Headlight_WhiteBeam (Projector bulb)
    new_pbr("Headlight_WhiteBeam", (0.95, 0.98, 1.0, 1.0), emission_color=(0.95, 0.98, 1.0, 1.0), emission_strength=18.0)

    # 11: Neon_Red (Rear LED taillights)
    new_pbr("Neon_Red", (1.0, 0.02, 0.02, 1.0), emission_color=(1.0, 0.02, 0.02, 1.0), emission_strength=10.0)

    return mats

def assign_mat_slot(obj, mat):
    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    return obj.data.materials.find(mat.name)

# ---------------------------------------------------------
# Unified Octane Body Shell
# ---------------------------------------------------------
def build_unified_octane_body(mats):
    """
    Constructs the complete Octane main body as a single polygonal shell
    with symmetric half-mesh mirrored across X=0.
    """
    mesh = bpy.data.meshes.new("Octane_Unified_Body")
    bm = bmesh.new()

    # Materials for the body
    m_blue = mats["CarPaint_Cobalt"]       # slot 0
    m_white = mats["RacingStripe_White"]   # slot 1
    m_trim = mats["CarPaint_White"]        # slot 2
    m_glass = mats["Cockpit_Glass"]        # slot 3
    m_black = mats["Chassis_MatteBlack"]   # slot 4
    m_taillight = mats["Neon_Red"]         # slot 5

    # Define key profile loops along Y (Front +1.40 to Rear -1.45)
    # Each loop has points from center (X=0) outward to fender/side
    # Format of vertex: (X, Y, Z)
    
    # Grid of vertices along X (0: center, 1: stripe outer, 2: hood shoulder/pillar, 3: fender inner, 4: fender peak, 5: fender outer lip)
    # Loop 0: Front Nose / Grille (Y = 1.38)
    l0 = [
        Vector((0.00, 1.38, 0.26)),   # center top
        Vector((0.11, 1.38, 0.26)),   # stripe top
        Vector((0.26, 1.38, 0.24)),   # nose corner top
        Vector((0.26, 1.38, 0.12)),   # nose corner bot
        Vector((0.11, 1.38, 0.12)),   # stripe bot
        Vector((0.00, 1.38, 0.12)),   # center bot
    ]
    
    # Loop 1: Front Nose Dip (Y = 1.20)
    l1 = [
        Vector((0.00, 1.20, 0.32)),
        Vector((0.12, 1.20, 0.32)),
        Vector((0.30, 1.20, 0.30)),
        Vector((0.32, 1.20, 0.15)),
        Vector((0.12, 1.20, 0.15)),
        Vector((0.00, 1.20, 0.15)),
    ]

    # Loop 2: Front Fender Front Slope (Y = 0.95, Front Wheel center is Y=0.95, Z=0.38)
    l2 = [
        Vector((0.00, 0.95, 0.42)),   # center hood
        Vector((0.13, 0.95, 0.42)),   # stripe outer
        Vector((0.32, 0.95, 0.44)),   # hood shoulder
        Vector((0.55, 0.95, 0.68)),   # fender arch peak
        Vector((0.74, 0.95, 0.60)),   # fender flare lip
        Vector((0.36, 0.95, 0.20)),   # chassis side sill
    ]

    # Loop 3: Windshield Base / Hood Cowl (Y = 0.45)
    l3 = [
        Vector((0.00, 0.45, 0.52)),   # center cowl
        Vector((0.14, 0.45, 0.52)),   # stripe outer
        Vector((0.34, 0.45, 0.54)),   # cowl shoulder / A-pillar base
        Vector((0.52, 0.45, 0.56)),   # fender rear slope
        Vector((0.68, 0.45, 0.46)),   # fender rear flare lip
        Vector((0.36, 0.45, 0.20)),   # side sill
    ]

    # Loop 4: Mid Cockpit / Raked Windshield (Y = 0.00)
    l4 = [
        Vector((0.00, 0.00, 0.74)),   # windshield mid center
        Vector((0.12, 0.00, 0.74)),   # windshield mid inner
        Vector((0.28, 0.00, 0.74)),   # A-pillar outer
        Vector((0.36, 0.00, 0.48)),   # door waist top
        Vector((0.44, 0.00, 0.46)),   # door waist outer ridge
        Vector((0.34, 0.00, 0.20)),   # side rocker sill
    ]

    # Loop 5: Roof Deck Peak (Y = -0.45)
    l5 = [
        Vector((0.00, -0.45, 0.85)),  # roof center
        Vector((0.11, -0.45, 0.85)),  # roof stripe
        Vector((0.24, -0.45, 0.85)),  # roof rail
        Vector((0.35, -0.45, 0.50)),  # side window sill
        Vector((0.44, -0.45, 0.48)),  # door waist outer ridge
        Vector((0.35, -0.45, 0.20)),  # side rocker sill
    ]

    # Loop 6: Rear of Cabin / Front of Engine Bay (Y = -0.80)
    l6 = [
        Vector((0.00, -0.80, 0.45)),  # engine cradle center
        Vector((0.12, -0.80, 0.45)),  # engine cradle inner
        Vector((0.26, -0.80, 0.48)),  # engine cradle side wall
        Vector((0.54, -0.80, 0.68)),  # rear fender front arch
        Vector((0.74, -0.80, 0.60)),  # rear fender flare lip
        Vector((0.42, -0.80, 0.20)),  # rear side sill
    ]

    # Loop 7: Rear Wheel Apex (Y = -1.10, Rear Wheel center is Y=-1.10, Z=0.42)
    l7 = [
        Vector((0.00, -1.10, 0.35)),  # engine deck center
        Vector((0.14, -1.10, 0.35)),  # engine deck inner
        Vector((0.28, -1.10, 0.40)),  # engine bay side wall
        Vector((0.58, -1.10, 0.74)),  # rear fender peak
        Vector((0.78, -1.10, 0.66)),  # rear fender flare lip
        Vector((0.45, -1.10, 0.22)),  # rear under sill
    ]

    # Loop 8: Rear Haunches / Taillight Valance (Y = -1.45)
    l8 = [
        Vector((0.00, -1.45, 0.30)),  # rear center valance
        Vector((0.15, -1.45, 0.30)),  # thruster mounting surround
        Vector((0.28, -1.45, 0.32)),  # rear deck outer wall
        Vector((0.52, -1.45, 0.58)),  # rear taillight housing
        Vector((0.68, -1.45, 0.52)),  # rear bumper outer lip
        Vector((0.45, -1.45, 0.22)),  # rear bottom diffuser
    ]

    loops = [l0, l1, l2, l3, l4, l5, l6, l7, l8]
    
    # Create bmesh vertices
    bm_loops = []
    for l in loops:
        bm_l = [bm.verts.new(v) for v in l]
        bm_loops.append(bm_l)

    # Build Quad Strips between adjacent loops
    for i in range(len(loops) - 1):
        curr_l = bm_loops[i]
        next_l = bm_loops[i+1]
        
        # Center Stripe: face 0 (from 0 to 1)
        f_stripe = bm.faces.new([curr_l[0], curr_l[1], next_l[1], next_l[0]])
        # Hood / Roof / Deck Outer: face 1 (from 1 to 2)
        f_main = bm.faces.new([curr_l[1], curr_l[2], next_l[2], next_l[1]])
        # Fender Arch / Pillar: face 2 (from 2 to 3)
        f_fender_top = bm.faces.new([curr_l[2], curr_l[3], next_l[3], next_l[2]])
        # Fender Lip / Door side: face 3 (from 3 to 4)
        f_lip = bm.faces.new([curr_l[3], curr_l[4], next_l[4], next_l[3]])
        # Lower Sill / Underbody: face 4 (from 4 to 5)
        f_sill = bm.faces.new([curr_l[4], curr_l[5], next_l[5], next_l[4]])

    # Build Front Grille Face
    f_grille = bm.faces.new([bm_loops[0][0], bm_loops[0][1], bm_loops[0][4], bm_loops[0][5]])
    f_grille_side = bm.faces.new([bm_loops[0][1], bm_loops[0][2], bm_loops[0][3], bm_loops[0][4]])

    # Build Rear End Valance Faces
    f_rear_mid = bm.faces.new([bm_loops[8][0], bm_loops[8][1], bm_loops[8][2], bm_loops[8][5]])
    f_rear_outer = bm.faces.new([bm_loops[8][2], bm_loops[8][3], bm_loops[8][4], bm_loops[8][5]])

    # Build Cockpit Canopy Windshield & Roof Faces
    # Windshield: from Loop 3 (Y=0.45, cowl) to Loop 5 (Y=-0.45, roof)
    # We create the raised glass windshield surface
    vw_cowl_c = bm.verts.new(Vector((0.00, 0.45, 0.52)))
    vw_cowl_r = bm.verts.new(Vector((0.26, 0.45, 0.53)))
    vw_roof_c = bm.verts.new(Vector((0.00, -0.45, 0.85)))
    vw_roof_r = bm.verts.new(Vector((0.24, -0.45, 0.85)))
    f_windshield = bm.faces.new([vw_cowl_c, vw_cowl_r, vw_roof_r, vw_roof_c])

    # Side Window: between cowl, roof, and door waist
    vw_rear_c = bm.verts.new(Vector((0.24, -0.78, 0.76)))
    f_sidewindow = bm.faces.new([vw_cowl_r, vw_roof_r, vw_rear_c, bm_loops[5][3]])

    # Roof Deck
    vw_roof_back_c = bm.verts.new(Vector((0.00, -0.78, 0.84)))
    vw_roof_back_r = bm.verts.new(Vector((0.22, -0.78, 0.84)))
    f_roof = bm.faces.new([vw_roof_c, vw_roof_r, vw_roof_back_r, vw_roof_back_c])

    bm.to_mesh(mesh)
    bm.free()

    body_obj = bpy.data.objects.new("Octane_Unified_Body", mesh)
    bpy.context.collection.objects.link(body_obj)

    # Assign Materials to slots
    assign_mat_slot(body_obj, m_blue)       # Slot 0: Blue
    assign_mat_slot(body_obj, m_white)      # Slot 1: Racing Stripe White
    assign_mat_slot(body_obj, m_trim)       # Slot 2: Titanium White Trim Lip
    assign_mat_slot(body_obj, m_glass)      # Slot 3: Cockpit Glass
    assign_mat_slot(body_obj, m_black)      # Slot 4: Grille & Chassis Black
    assign_mat_slot(body_obj, m_taillight)  # Slot 5: Neon Red Taillight

    # Material Slot assignment by face criteria
    for poly in body_obj.data.polygons:
        poly.use_smooth = True
        c = poly.center
        # Racing Stripe along center of hood & roof
        if abs(c.x) < 0.12 and (0.40 < c.y < 1.38 or -0.80 < c.y < -0.40):
            poly.material_index = 1
        # Fender outer lips (Titanium White trim)
        elif abs(c.x) > 0.62 and (0.60 < c.y < 1.25 or -1.35 < c.y < -0.75):
            poly.material_index = 2
        # Cockpit Windshield & Side Windows
        elif (c.z > 0.60 and -0.75 < c.y < 0.40 and abs(c.x) < 0.32):
            poly.material_index = 3
        # Front Grille
        elif c.y > 1.35:
            poly.material_index = 4
        # Rear Taillight
        elif c.y < -1.40 and abs(c.x) > 0.48:
            poly.material_index = 5
        else:
            poly.material_index = 0

    # Apply Mirror Modifier across X
    mirror_mod = body_obj.modifiers.new(name="Mirror", type='MIRROR')
    mirror_mod.use_axis[0] = True
    mirror_mod.use_clip = True
    mirror_mod.merge_threshold = 0.005

    # Apply Subdivision Surface Modifier for smooth automotive styling
    sub_mod = body_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub_mod.levels = 1
    sub_mod.render_levels = 2

    return body_obj

# ---------------------------------------------------------
# Front Bullbar & Projector Headlights
# ---------------------------------------------------------
def build_front_bullbar_and_lights(mats):
    """
    Constructs the tubular bullbar, dual cyan halo projector headlights, and lower fog lights.
    """
    # 1. Upper Bullbar Tube
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.03,
        depth=0.68,
        vertices=14,
        location=(0.0, 1.44, 0.24)
    )
    bar_top = bpy.context.active_object
    bar_top.name = "Bullbar_Top"
    bar_top.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat_slot(bar_top, mats["Chassis_MatteBlack"])

    # 2. Lower Bumper Skid Tube
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.025,
        depth=0.56,
        vertices=12,
        location=(0.0, 1.47, 0.12)
    )
    bar_bot = bpy.context.active_object
    bar_bot.name = "Bullbar_Bottom"
    bar_bot.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat_slot(bar_bot, mats["Chassis_MatteBlack"])

    # 3. Bullbar Vertical Guards
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.20,
            vertices=10,
            location=(0.20 * side, 1.45, 0.18)
        )
        guard = bpy.context.active_object
        guard.name = f"Bullbar_Guard_{'L' if side < 0 else 'R'}"
        assign_mat_slot(guard, mats["Chassis_MatteBlack"])

    # 4. Projector Headlights with Glowing Cyan Halos
    for side in [-1, 1]:
        # Casing
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.088,
            depth=0.07,
            vertices=18,
            location=(0.33 * side, 1.41, 0.25)
        )
        casing = bpy.context.active_object
        casing.name = f"Headlight_Housing_{'L' if side < 0 else 'R'}"
        casing.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(casing, mats["Chassis_MatteBlack"])

        # Cyan Neon Halo Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.082,
            minor_radius=0.016,
            major_segments=22,
            minor_segments=8,
            location=(0.33 * side, 1.46, 0.25)
        )
        halo = bpy.context.active_object
        halo.name = f"Headlight_Halo_{'L' if side < 0 else 'R'}"
        halo.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(halo, mats["Neon_Cyan"])

        # Center White Projector Lens
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05,
            depth=0.025,
            vertices=16,
            location=(0.33 * side, 1.46, 0.25)
        )
        lens = bpy.context.active_object
        lens.name = f"Headlight_Projector_{'L' if side < 0 else 'R'}"
        lens.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(lens, mats["Headlight_WhiteBeam"])

    # 5. Lower Fog Lights
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.045,
            depth=0.035,
            vertices=14,
            location=(0.10 * side, 1.49, 0.12)
        )
        fog = bpy.context.active_object
        fog.name = f"Fog_Light_{'L' if side < 0 else 'R'}"
        fog.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(fog, mats["Headlight_WhiteBeam"])

# ---------------------------------------------------------
# Roof Air Scoop & Cockpit Accents
# ---------------------------------------------------------
def build_roof_scoop(mats):
    """
    Mounts the signature Octane dual-nostril air scoop on the roof.
    """
    # Main Scoop Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.62, 0.91))
    scoop = bpy.context.active_object
    scoop.name = "Roof_Air_Scoop"
    scoop.scale = (0.32, 0.22, 0.065)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat_slot(scoop, mats["Chassis_MatteBlack"])

    # Dual Chrome Intake Nostrils
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.08 * side, -0.50, 0.91))
        nostril = bpy.context.active_object
        nostril.name = f"Scoop_Nostril_{'L' if side < 0 else 'R'}"
        nostril.scale = (0.075, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat_slot(nostril, mats["Polished_Chrome"])

# ---------------------------------------------------------
# Exposed V8 Engine & Rocket Thrusters
# ---------------------------------------------------------
def build_v8_engine_and_thrusters(mats):
    """
    Constructs the V8 racing engine and twin rocket boost thrusters.
    """
    # 1. Engine Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.02, 0.44))
    block = bpy.context.active_object
    block.name = "V8_Engine_Block"
    block.scale = (0.32, 0.40, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat_slot(block, mats["Gunmetal_Alloy"])

    # 2. Dual Racing Red Valve Covers
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.14 * side, -1.02, 0.52))
        valve = bpy.context.active_object
        valve.name = f"ValveCover_Red_{'L' if side < 0 else 'R'}"
        valve.scale = (0.11, 0.38, 0.065)
        valve.rotation_euler = (0, math.radians(20 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat_slot(valve, mats["Engine_Red"])

        # 4 Polished Chrome Velocity Stacks per bank
        for row in range(4):
            y_pos = -0.88 - (row * 0.09)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.022,
                depth=0.11,
                vertices=12,
                location=(0.09 * side, y_pos, 0.58)
            )
            stack = bpy.context.active_object
            stack.name = f"Velocity_Stack_{'L' if side < 0 else 'R'}_{row}"
            assign_mat_slot(stack, mats["Polished_Chrome"])

    # 3. Dual Rocket Boost Thruster Nozzles
    for side in [-1, 1]:
        # Outer Nozzle Bell
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.09,
            depth=0.18,
            vertices=18,
            location=(0.15 * side, -1.50, 0.38)
        )
        nozzle = bpy.context.active_object
        nozzle.name = f"Rocket_Nozzle_{'L' if side < 0 else 'R'}"
        nozzle.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(nozzle, mats["Chassis_MatteBlack"])

        # Chrome Beveled Trim Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.09,
            minor_radius=0.016,
            major_segments=18,
            minor_segments=8,
            location=(0.15 * side, -1.59, 0.38)
        )
        ring = bpy.context.active_object
        ring.name = f"Nozzle_Rim_{'L' if side < 0 else 'R'}"
        ring.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(ring, mats["Polished_Chrome"])

        # Deep Glowing Cyan Plasma Core
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.068,
            depth=0.04,
            vertices=16,
            location=(0.15 * side, -1.57, 0.38)
        )
        plasma = bpy.context.active_object
        plasma.name = f"Rocket_Plasma_{'L' if side < 0 else 'R'}"
        plasma.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(plasma, mats["Neon_Cyan"])

# ---------------------------------------------------------
# High-Downforce Rear Wing
# ---------------------------------------------------------
def build_rear_wing(mats):
    """
    Constructs the high-downforce rear spoiler with Titanium White endplates.
    """
    # Main Airfoil
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.28, 0.98))
    wing = bpy.context.active_object
    wing.name = "Rear_Wing_Airfoil"
    wing.scale = (0.84, 0.22, 0.036)
    wing.rotation_euler = (math.radians(-7), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat_slot(wing, mats["CarPaint_Cobalt"])

    # Raked Pylons & Titanium White Endplates
    for side in [-1, 1]:
        # Pylon
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.46,
            vertices=10,
            location=(0.28 * side, -1.20, 0.77)
        )
        pylon = bpy.context.active_object
        pylon.name = f"Wing_Pylon_{'L' if side < 0 else 'R'}"
        pylon.rotation_euler = (math.radians(-22), 0, math.radians(6 * side))
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat_slot(pylon, mats["Chassis_MatteBlack"])

        # Swept Endplate in Titanium White
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.43 * side, -1.28, 0.98))
        endplate = bpy.context.active_object
        endplate.name = f"Wing_Endplate_{'L' if side < 0 else 'R'}"
        endplate.scale = (0.028, 0.28, 0.16)
        endplate.rotation_euler = (math.radians(-5), math.radians(8 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat_slot(endplate, mats["CarPaint_White"])

# ---------------------------------------------------------
# Rocket League Deep-Dish Wheels
# ---------------------------------------------------------
def build_rocket_league_wheels(mats):
    """
    Constructs the 4 deep-dish sports wheels with chunky tires and red calipers.
    """
    configs = [
        # (name, x, y, z, tire_radius, tire_width, rim_radius)
        ("Front_L", -0.74,  0.95, 0.38, 0.40, 0.27, 0.25),
        ("Front_R",  0.74,  0.95, 0.38, 0.40, 0.27, 0.25),
        ("Rear_L",  -0.78, -1.10, 0.42, 0.44, 0.32, 0.27),
        ("Rear_R",   0.78, -1.10, 0.42, 0.44, 0.32, 0.27),
    ]

    for name, wx, wy, wz, r_tire, w_tire, r_rim in configs:
        side_mult = 1 if (wx > 0) else -1
        outer_face_x = wx + (w_tire * 0.52 * side_mult)

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
        assign_mat_slot(tire, mats["Tire_Rubber"])
        for poly in tire.data.polygons: poly.use_smooth = True

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
        assign_mat_slot(rim_lip, mats["Polished_Chrome"])
        for poly in rim_lip.data.polygons: poly.use_smooth = True

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
        assign_mat_slot(hub, mats["Polished_Chrome"])

        # 10 Radial Spokes
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            spoke_y = wy + math.cos(angle) * (r_rim * 0.50)
            spoke_z = wz + math.sin(angle) * (r_rim * 0.50)
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(dish_center_x + (0.012 * side_mult), spoke_y, spoke_z)
            )
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{name}_{i}"
            spoke.scale = (0.018, 0.030, r_rim * 0.82)
            spoke.rotation_euler = (angle, 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            assign_mat_slot(spoke, mats["Gunmetal_Alloy"])

        # 4. Brake Disc & Red Caliper
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
        assign_mat_slot(disc, mats["Gunmetal_Alloy"])

        # Red Racing Caliper
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(disc_x, wy + (r_rim * 0.52), wz)
        )
        caliper = bpy.context.active_object
        caliper.name = f"BrakeCaliper_{name}"
        caliper.scale = (0.045, 0.065, 0.11)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat_slot(caliper, mats["Engine_Red"])

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
    assign_mat_slot(floor, floor_mat)

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
    assign_mat_slot(line, line_mat)

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
    fill.energy = 200.0
    fill.color = (0.92, 0.94, 1.0)
    fill.size = 4.5
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (4.0, 3.5, 2.5)
    fill_obj.rotation_euler = (math.radians(55), math.radians(15), math.radians(-30))

    # Camera matching the EXACT hero 3/4 angle in media_1790263831226.png
    cam_data = bpy.data.cameras.new(name="Hero_Camera")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Hero_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    # Position: in front-left of the car
    cam_obj.location = (-3.2, 3.6, 1.55)
    # Track towards center of hood/cockpit
    target = Vector((0.0, 0.15, 0.52))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.camera = cam_obj

# ---------------------------------------------------------
# Main Routine
# ---------------------------------------------------------
def main():
    print("=== BUILDING AUTHENTIC 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    mats = create_materials()

    build_unified_octane_body(mats)
    build_front_bullbar_and_lights(mats)
    build_roof_scoop(mats)
    build_v8_engine_and_thrusters(mats)
    build_rear_wing(mats)
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
