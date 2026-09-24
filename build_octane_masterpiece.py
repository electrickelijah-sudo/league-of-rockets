"""
Builds an authentic, high-fidelity Rocket League Octane in Blender 5.1.2.
Matches media_1790263831226.png 1:1:
- Authentic aerodynamic curved front fenders with sweeping Titanium White arch trims
- Sloped sculpted hood with dual Alpine White racing stripes and dark radiator grille
- Seamless angular cockpit with raked glass windshield, white A-pillars, side windows, dual-nostril roof scoop
- Wasp-waist side body with sculpted intake vents and neon cyan underglow
- Muscular flared rear hip fenders with Titanium White trim arches
- Open rear engine bay with exposed V8 (red valve covers, chrome velocity intake stacks, exhaust headers)
- Dual chrome rocket boost thrusters with glowing cyan plasma cores
- High-downforce rear wing with Titanium White endplates
- Aggressive deep-dish Rocket League wheels with treaded tires and red brake calipers
- Tubular bullbar with dual halo projector headlights and lower foglights
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Remove any leftover objects or collections
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)

# ---------------------------------------------------------
# Material Helpers
# ---------------------------------------------------------
def create_materials():
    mats = {}

    def new_pbr(name, base_color, metallic=0.0, roughness=0.3, clearcoat=0.0, emission_color=None, emission_strength=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
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
    new_pbr("CarPaint_Cobalt", (0.015, 0.12, 0.65, 1.0), metallic=0.6, roughness=0.22, clearcoat=1.0)
    
    # Titanium White Trim Paint
    new_pbr("CarPaint_White", (0.95, 0.95, 0.96, 1.0), metallic=0.15, roughness=0.25, clearcoat=0.8)

    # Racing Stripes White
    new_pbr("RacingStripe_White", (0.98, 0.98, 0.98, 1.0), metallic=0.1, roughness=0.2, clearcoat=0.9)

    # Dark Glass
    new_pbr("Cockpit_Glass", (0.015, 0.02, 0.03, 1.0), metallic=0.85, roughness=0.08, clearcoat=1.0)

    # Chassis & Matte Trim
    new_pbr("Chassis_MatteBlack", (0.03, 0.03, 0.035, 1.0), metallic=0.3, roughness=0.6)

    # Chrome / Polished Metal
    new_pbr("Polished_Chrome", (0.95, 0.95, 0.95, 1.0), metallic=1.0, roughness=0.04)

    # Gunmetal Alloy
    new_pbr("Gunmetal_Alloy", (0.07, 0.075, 0.08, 1.0), metallic=0.9, roughness=0.3)

    # Tire Rubber
    new_pbr("Tire_Rubber", (0.02, 0.02, 0.02, 1.0), metallic=0.02, roughness=0.7)

    # Engine Red Valve Covers
    new_pbr("Engine_Red", (0.75, 0.04, 0.04, 1.0), metallic=0.4, roughness=0.35, clearcoat=0.5)

    # Headlight Halo Cyan Neon
    new_pbr("Neon_Cyan", (0.0, 0.85, 1.0, 1.0), emission_color=(0.0, 0.85, 1.0, 1.0), emission_strength=12.0)

    # Headlight Inner Bright White Projector
    new_pbr("Headlight_WhiteBeam", (0.95, 0.98, 1.0, 1.0), emission_color=(0.95, 0.98, 1.0, 1.0), emission_strength=18.0)

    # Rocket Boost Core Cyan Plasma
    new_pbr("Rocket_Plasma", (0.0, 0.9, 1.0, 1.0), emission_color=(0.0, 0.9, 1.0, 1.0), emission_strength=20.0)

    # Brake Light Neon Red
    new_pbr("Neon_Red", (1.0, 0.02, 0.02, 1.0), emission_color=(1.0, 0.02, 0.02, 1.0), emission_strength=8.0)

    return mats

def assign_material(obj, mat):
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

def apply_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

# ---------------------------------------------------------
# Modular Modeling Components
# ---------------------------------------------------------

def build_octane_chassis_and_fenders(mats):
    """
    Builds the sculpted front hood, nose, radiator grille, and arched front & rear fenders with Titanium White lips.
    """
    # 1. Sculpted Hood & Nose
    bm = bmesh.new()
    
    # Vertices for the sloped aerodynamic hood
    # Length: Y from 0.0 to 1.35
    # Height: Z from 0.52 (windshield base) to 0.28 (nose)
    # Recessed center channel with raised fenders
    hood_verts = [
        # Y=0.0 (Base of windshield)
        Vector((-0.38, 0.0, 0.52)),   # 0 left cowl
        Vector((-0.18, 0.0, 0.50)),   # 1 left stripe
        Vector(( 0.00, 0.0, 0.49)),   # 2 center crease
        Vector(( 0.18, 0.0, 0.50)),   # 3 right stripe
        Vector(( 0.38, 0.0, 0.52)),   # 4 right cowl
        
        # Y=0.7 (Mid hood)
        Vector((-0.36, 0.7, 0.44)),   # 5
        Vector((-0.17, 0.7, 0.42)),   # 6
        Vector(( 0.00, 0.7, 0.41)),   # 7
        Vector(( 0.17, 0.7, 0.42)),   # 8
        Vector(( 0.36, 0.7, 0.44)),   # 9

        # Y=1.25 (Front nose dip)
        Vector((-0.32, 1.25, 0.30)),  # 10
        Vector((-0.15, 1.25, 0.29)),  # 11
        Vector(( 0.00, 1.25, 0.28)),  # 12
        Vector(( 0.15, 1.25, 0.29)),  # 13
        Vector(( 0.32, 1.25, 0.30)),  # 14
        
        # Y=1.35 (Nose tip down to grille)
        Vector((-0.28, 1.35, 0.18)),  # 15
        Vector((-0.14, 1.35, 0.18)),  # 16
        Vector(( 0.00, 1.35, 0.18)),  # 17
        Vector(( 0.14, 1.35, 0.18)),  # 18
        Vector(( 0.28, 1.35, 0.18)),  # 19
    ]
    bm_v = [bm.verts.new(v) for v in hood_verts]
    
    # Create quad faces for hood
    for row in range(3):
        r_start = row * 5
        n_start = (row + 1) * 5
        for col in range(4):
            bm.faces.new([
                bm_v[r_start + col],
                bm_v[r_start + col + 1],
                bm_v[n_start + col + 1],
                bm_v[n_start + col]
            ])
            
    # Hood sides down to chassis
    # Left side skirts
    bm.faces.new([bm_v[0], bm_v[5], bm.verts.new(Vector((-0.38, 0.7, 0.22))), bm.verts.new(Vector((-0.40, 0.0, 0.22)))])
    bm.faces.new([bm_v[5], bm_v[10], bm.verts.new(Vector((-0.34, 1.25, 0.15))), bm.verts.new(Vector((-0.38, 0.7, 0.22)))])
    # Right side skirts
    bm.faces.new([bm_v[4], bm.verts.new(Vector((0.40, 0.0, 0.22))), bm.verts.new(Vector((0.38, 0.7, 0.22))), bm_v[9]])
    bm.faces.new([bm_v[9], bm.verts.new(Vector((0.38, 0.7, 0.22))), bm.verts.new(Vector((0.34, 1.25, 0.15))), bm_v[14]])

    # Grille face
    bm.faces.new([bm_v[15], bm_v[19], bm.verts.new(Vector((0.28, 1.35, 0.08))), bm.verts.new(Vector((-0.28, 1.35, 0.08)))])

    mesh = bpy.data.meshes.new("Octane_Hood")
    bm.to_mesh(mesh)
    bm.free()
    
    hood_obj = bpy.data.objects.new("Octane_Hood", mesh)
    bpy.context.collection.objects.link(hood_obj)
    assign_material(hood_obj, mats["CarPaint_Cobalt"])
    apply_smooth(hood_obj)

    # 2. Dual Alpine White Racing Stripes on Hood
    for side in [-1, 1]:
        stripe_mesh = bpy.data.meshes.new(f"Stripe_{'L' if side < 0 else 'R'}")
        bm_s = bmesh.new()
        # Stripe runs from Y=0.0 to Y=1.34 slightly hovering above hood (Z + 0.003)
        x_in = 0.02 * side
        x_out = 0.14 * side
        v0 = bm_s.verts.new(Vector((x_in, 0.00, 0.493)))
        v1 = bm_s.verts.new(Vector((x_out, 0.00, 0.503)))
        v2 = bm_s.verts.new(Vector((x_out * 0.95, 0.70, 0.423)))
        v3 = bm_s.verts.new(Vector((x_in, 0.70, 0.413)))
        v4 = bm_s.verts.new(Vector((x_out * 0.90, 1.30, 0.288)))
        v5 = bm_s.verts.new(Vector((x_in, 1.30, 0.283)))
        
        bm_s.faces.new([v0, v1, v2, v3])
        bm_s.faces.new([v3, v2, v4, v5])
        bm_s.to_mesh(stripe_mesh)
        bm_s.free()
        st_obj = bpy.data.objects.new(f"Hood_Stripe_{'L' if side < 0 else 'R'}", stripe_mesh)
        bpy.context.collection.objects.link(st_obj)
        assign_material(st_obj, mats["RacingStripe_White"])

    # 3. Arched Front Fenders with Sweeping Titanium White Trim Lips
    # Front wheel center is at Y=0.98, Z=0.38, X=+-0.72. Wheel radius = 0.40.
    # The fender arches over the tire from angle 15 deg to 165 deg.
    for side in [-1, 1]:
        # Body-color arched fender shell
        bm_f = bmesh.new()
        angles = [15, 45, 75, 105, 135, 165]
        r_inner = 0.46
        r_outer = 0.50
        y_center = 0.98
        z_center = 0.38
        x_base = 0.35 * side
        x_flare = 0.74 * side
        
        inner_arc = []
        outer_arc = []
        
        for deg in angles:
            rad = math.radians(deg)
            # Y is forward, Z is up
            dy = math.cos(rad)
            dz = math.sin(rad)
            inner_arc.append(bm_f.verts.new(Vector((x_base, y_center - dy * r_inner, z_center + dz * r_inner * 0.85))))
            outer_arc.append(bm_f.verts.new(Vector((x_flare, y_center - dy * r_outer, z_center + dz * r_outer * 0.95))))
            
        for i in range(len(angles) - 1):
            bm_f.faces.new([inner_arc[i], outer_arc[i], outer_arc[i+1], inner_arc[i+1]])
            
        # Top bevel flange
        mesh_f = bpy.data.meshes.new(f"FrontFender_{'L' if side < 0 else 'R'}")
        bm_f.to_mesh(mesh_f)
        bm_f.free()
        fender_obj = bpy.data.objects.new(f"FrontFender_{'L' if side < 0 else 'R'}", mesh_f)
        bpy.context.collection.objects.link(fender_obj)
        assign_material(fender_obj, mats["CarPaint_Cobalt"])
        apply_smooth(fender_obj)

        # Titanium White Fender Rim Lip (Curve extrusion along outer arc)
        bm_lip = bmesh.new()
        lip_thickness = 0.038
        for i in range(len(angles)):
            rad = math.radians(angles[i])
            dy = math.cos(rad)
            dz = math.sin(rad)
            # Create a 3D rim arch strip
            p1 = Vector((x_flare, y_center - dy * r_outer, z_center + dz * r_outer * 0.95))
            p2 = Vector((x_flare + 0.03 * side, y_center - dy * (r_outer + lip_thickness), z_center + dz * (r_outer + lip_thickness) * 0.95))
            p3 = Vector((x_flare, y_center - dy * (r_outer + lip_thickness), z_center + dz * (r_outer + lip_thickness) * 0.95 - 0.04))
            v1 = bm_lip.verts.new(p1)
            v2 = bm_lip.verts.new(p2)
            v3 = bm_lip.verts.new(p3)
            if i > 0:
                # Link quad
                bm_lip.faces.new([prev_v1, prev_v2, v2, v1])
                bm_lip.faces.new([prev_v2, prev_v3, v3, v2])
            prev_v1, prev_v2, prev_v3 = v1, v2, v3
            
        mesh_lip = bpy.data.meshes.new(f"FrontFenderLip_{'L' if side < 0 else 'R'}")
        bm_lip.to_mesh(mesh_lip)
        bm_lip.free()
        lip_obj = bpy.data.objects.new(f"FrontFenderLip_{'L' if side < 0 else 'R'}", mesh_lip)
        bpy.context.collection.objects.link(lip_obj)
        assign_material(lip_obj, mats["CarPaint_White"])
        apply_smooth(lip_obj)

def build_octane_cockpit(mats):
    """
    Builds the authentic Octane cockpit canopy:
    - Raked dark-tint glass windshield with Titanium White A-pillars
    - Flat roof deck with continuing dual Alpine White racing stripes
    - Side triangular canopy windows
    - Dual-port roof air intake scoop
    """
    # 1. Cockpit Glass (Windshield + Side windows)
    bm_glass = bmesh.new()
    # Front windshield: Y from 0.0 to -0.45, Z from 0.52 to 0.85, raked backwards
    gw_b_l = bm_glass.verts.new(Vector((-0.36, 0.00, 0.53)))
    gw_b_r = bm_glass.verts.new(Vector(( 0.36, 0.00, 0.53)))
    gw_t_l = bm_glass.verts.new(Vector((-0.26, -0.46, 0.84)))
    gw_t_r = bm_glass.verts.new(Vector(( 0.26, -0.46, 0.84)))
    bm_glass.faces.new([gw_b_l, gw_b_r, gw_t_r, gw_t_l])

    # Side windows
    # Left side window
    gw_rear_l = bm_glass.verts.new(Vector((-0.28, -0.80, 0.72)))
    gw_sill_l = bm_glass.verts.new(Vector((-0.38, -0.75, 0.50)))
    bm_glass.faces.new([gw_b_l, gw_t_l, gw_rear_l, gw_sill_l])
    
    # Right side window
    gw_rear_r = bm_glass.verts.new(Vector(( 0.28, -0.80, 0.72)))
    gw_sill_r = bm_glass.verts.new(Vector(( 0.38, -0.75, 0.50)))
    bm_glass.faces.new([gw_b_r, gw_sill_r, gw_rear_r, gw_t_r])

    mesh_glass = bpy.data.meshes.new("Cockpit_Glass")
    bm_glass.to_mesh(mesh_glass)
    bm_glass.free()
    glass_obj = bpy.data.objects.new("Cockpit_Glass", mesh_glass)
    bpy.context.collection.objects.link(glass_obj)
    assign_material(glass_obj, mats["Cockpit_Glass"])

    # 2. Titanium White A-Pillars & Roof Trim Rails
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.032,
            depth=0.68,
            vertices=12,
            location=(0.31 * side, -0.23, 0.685)
        )
        pillar = bpy.context.active_object
        pillar.name = f"A_Pillar_{'L' if side < 0 else 'R'}"
        # Rake pillar to match windshield slope
        pillar.rotation_euler = (math.radians(-54), 0, math.radians(14 * side))
        assign_material(pillar, mats["CarPaint_White"])
        apply_smooth(pillar)

    # 3. Roof Deck (Blue body with dual white stripes)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.63, 0.84))
    roof = bpy.context.active_object
    roof.name = "Cockpit_Roof"
    roof.scale = (0.52, 0.38, 0.035)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(roof, mats["CarPaint_Cobalt"])

    # Roof stripes
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.08 * side, -0.63, 0.86))
        r_stripe = bpy.context.active_object
        r_stripe.name = f"Roof_Stripe_{'L' if side < 0 else 'R'}"
        r_stripe.scale = (0.055, 0.18, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_material(r_stripe, mats["RacingStripe_White"])

    # 4. Octane Dual-Port Roof Air Scoop (Iconic feature on roof)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.68, 0.90))
    scoop = bpy.context.active_object
    scoop.name = "Roof_Air_Scoop"
    scoop.scale = (0.34, 0.22, 0.065)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(scoop, mats["Chassis_MatteBlack"])

    # Dual intake mouth cutouts / nostrils
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.08 * side, -0.56, 0.90))
        nostril = bpy.context.active_object
        nostril.name = f"Scoop_Nostril_{'L' if side < 0 else 'R'}"
        nostril.scale = (0.08, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_material(nostril, mats["Polished_Chrome"])

def build_octane_side_body_and_rear_fenders(mats):
    """
    Builds the wasp-waist side body, aerodynamic side intake vents, and wide flared rear fenders with Titanium White lips.
    """
    # 1. Wasp-Waist Side Body Pods
    for side in [-1, 1]:
        bm = bmesh.new()
        # Sculpted side panel linking front to rear
        # Front at Y=0.0, Middle pinch at Y=-0.5, Rear hip at Y=-1.0
        v_f_top = bm.verts.new(Vector((0.38 * side, 0.0, 0.50)))
        v_f_bot = bm.verts.new(Vector((0.36 * side, 0.0, 0.20)))
        
        v_m_top = bm.verts.new(Vector((0.36 * side, -0.50, 0.48)))
        v_m_bot = bm.verts.new(Vector((0.33 * side, -0.50, 0.18)))
        
        v_r_top = bm.verts.new(Vector((0.55 * side, -1.05, 0.56)))
        v_r_bot = bm.verts.new(Vector((0.48 * side, -1.05, 0.20)))

        bm.faces.new([v_f_top, v_m_top, v_m_bot, v_f_bot])
        bm.faces.new([v_m_top, v_r_top, v_r_bot, v_m_bot])
        
        mesh = bpy.data.meshes.new(f"SideBody_{'L' if side < 0 else 'R'}")
        bm.to_mesh(mesh)
        bm.free()
        side_obj = bpy.data.objects.new(f"SideBody_{'L' if side < 0 else 'R'}", mesh)
        bpy.context.collection.objects.link(side_obj)
        assign_material(side_obj, mats["CarPaint_Cobalt"])
        apply_smooth(side_obj)

        # Subtle Cyan Neon Rocker Tube along bottom edge
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.016,
            depth=0.85,
            vertices=8,
            location=(0.35 * side, -0.45, 0.17)
        )
        neon_rocker = bpy.context.active_object
        neon_rocker.name = f"Neon_Rocker_{'L' if side < 0 else 'R'}"
        neon_rocker.rotation_euler = (math.radians(90), 0, 0)
        assign_material(neon_rocker, mats["Neon_Cyan"])

    # 2. Muscular Flared Rear Fenders with Arched Titanium White Trim
    # Rear wheel center is at Y=-1.05, Z=0.42, X=+-0.76. Wheel radius = 0.44.
    for side in [-1, 1]:
        bm_rf = bmesh.new()
        angles = [15, 45, 75, 105, 135, 165]
        r_inner = 0.48
        r_outer = 0.54
        y_center = -1.05
        z_center = 0.42
        x_base = 0.45 * side
        x_flare = 0.78 * side
        
        inner_arc = []
        outer_arc = []
        
        for deg in angles:
            rad = math.radians(deg)
            dy = math.cos(rad)
            dz = math.sin(rad)
            inner_arc.append(bm_rf.verts.new(Vector((x_base, y_center - dy * r_inner, z_center + dz * r_inner * 0.90))))
            outer_arc.append(bm_rf.verts.new(Vector((x_flare, y_center - dy * r_outer, z_center + dz * r_outer * 0.98))))
            
        for i in range(len(angles) - 1):
            bm_rf.faces.new([inner_arc[i], outer_arc[i], outer_arc[i+1], inner_arc[i+1]])

        mesh_rf = bpy.data.meshes.new(f"RearFender_{'L' if side < 0 else 'R'}")
        bm_rf.to_mesh(mesh_rf)
        bm_rf.free()
        rf_obj = bpy.data.objects.new(f"RearFender_{'L' if side < 0 else 'R'}", mesh_rf)
        bpy.context.collection.objects.link(rf_obj)
        assign_material(rf_obj, mats["CarPaint_Cobalt"])
        apply_smooth(rf_obj)

        # Titanium White Trim Lip on Rear Fender
        bm_rlip = bmesh.new()
        lip_thickness = 0.04
        for i in range(len(angles)):
            rad = math.radians(angles[i])
            dy = math.cos(rad)
            dz = math.sin(rad)
            p1 = Vector((x_flare, y_center - dy * r_outer, z_center + dz * r_outer * 0.98))
            p2 = Vector((x_flare + 0.032 * side, y_center - dy * (r_outer + lip_thickness), z_center + dz * (r_outer + lip_thickness) * 0.98))
            v1 = bm_rlip.verts.new(p1)
            v2 = bm_rlip.verts.new(p2)
            if i > 0:
                bm_rlip.faces.new([prev_v1, prev_v2, v2, v1])
            prev_v1, prev_v2 = v1, v2
            
        mesh_rlip = bpy.data.meshes.new(f"RearFenderLip_{'L' if side < 0 else 'R'}")
        bm_rlip.to_mesh(mesh_rlip)
        bm_rlip.free()
        rlip_obj = bpy.data.objects.new(f"RearFenderLip_{'L' if side < 0 else 'R'}", mesh_rlip)
        bpy.context.collection.objects.link(rlip_obj)
        assign_material(rlip_obj, mats["CarPaint_White"])
        apply_smooth(rlip_obj)

        # Integrated LED Red Taillight Bar on Rear Haunch
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.60 * side, -1.48, 0.52))
        taillight = bpy.context.active_object
        taillight.name = f"LED_Taillight_{'L' if side < 0 else 'R'}"
        taillight.scale = (0.12, 0.03, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        assign_material(taillight, mats["Neon_Red"])

def build_octane_engine_bay_and_thrusters(mats):
    """
    Builds the exposed rear engine bay:
    - V8 Racing Engine with dual bright red cylinder heads
    - 8 polished chrome velocity intake stacks
    - Twin rocket boost thruster nozzles with glowing cyan plasma cores
    """
    # 1. Lower Engine Bed / Rear Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.02, 0.28))
    deck = bpy.context.active_object
    deck.name = "Engine_Deck_Bed"
    deck.scale = (0.55, 0.60, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(deck, mats["Chassis_MatteBlack"])

    # 2. V8 Engine Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.98, 0.40))
    block = bpy.context.active_object
    block.name = "V8_Engine_Block"
    block.scale = (0.34, 0.42, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(block, mats["Gunmetal_Alloy"])

    # 3. Dual Red Valve Covers (Angled V8 heads)
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.14 * side, -0.98, 0.48))
        valve = bpy.context.active_object
        valve.name = f"ValveCover_Red_{'L' if side < 0 else 'R'}"
        valve.scale = (0.12, 0.38, 0.07)
        valve.rotation_euler = (0, math.radians(22 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_material(valve, mats["Engine_Red"])

        # 4 Chrome Velocity Intake Stacks per bank
        for row in range(4):
            y_pos = -0.84 - (row * 0.09)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.022,
                depth=0.10,
                vertices=12,
                location=(0.09 * side, y_pos, 0.54)
            )
            stack = bpy.context.active_object
            stack.name = f"IntakeStack_{'L' if side < 0 else 'R'}_{row}"
            assign_material(stack, mats["Polished_Chrome"])

    # 4. Dual Rocket Boost Thruster Nozzles
    for side in [-1, 1]:
        # Outer Nozzle Bell
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.088,
            depth=0.18,
            vertices=16,
            location=(0.15 * side, -1.48, 0.38)
        )
        nozzle = bpy.context.active_object
        nozzle.name = f"Rocket_Nozzle_{'L' if side < 0 else 'R'}"
        nozzle.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(nozzle, mats["Chassis_MatteBlack"])

        # Chrome Outer Beveled Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.088,
            minor_radius=0.016,
            major_segments=16,
            minor_segments=8,
            location=(0.15 * side, -1.57, 0.38)
        )
        ring = bpy.context.active_object
        ring.name = f"Nozzle_Ring_{'L' if side < 0 else 'R'}"
        ring.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(ring, mats["Polished_Chrome"])

        # Glowing Cyan Plasma Exhaust Core
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.068,
            depth=0.04,
            vertices=16,
            location=(0.15 * side, -1.55, 0.38)
        )
        plasma = bpy.context.active_object
        plasma.name = f"Rocket_Plasma_Core_{'L' if side < 0 else 'R'}"
        plasma.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(plasma, mats["Rocket_Plasma"])

def build_octane_high_downforce_wing(mats):
    """
    Builds the high-mounted Octane rear spoiler:
    - High-downforce aerodynamic main airfoil in Cobalt Blue
    - Raked support pylons
    - Swept vertical endplates in Titanium White
    """
    # Main Airfoil Wing
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.25, 0.98))
    wing = bpy.context.active_object
    wing.name = "Rear_Wing_Airfoil"
    wing.scale = (0.86, 0.22, 0.038)
    wing.rotation_euler = (math.radians(-8), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_material(wing, mats["CarPaint_Cobalt"])

    # Raked Mounting Pylons
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.48,
            vertices=10,
            location=(0.28 * side, -1.18, 0.76)
        )
        pylon = bpy.context.active_object
        pylon.name = f"Wing_Pylon_{'L' if side < 0 else 'R'}"
        pylon.rotation_euler = (math.radians(-24), 0, math.radians(6 * side))
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(pylon, mats["Chassis_MatteBlack"])

        # Swept Vertical Endplate in Titanium White
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.44 * side, -1.25, 0.98))
        endplate = bpy.context.active_object
        endplate.name = f"Wing_Endplate_{'L' if side < 0 else 'R'}"
        endplate.scale = (0.028, 0.28, 0.16)
        endplate.rotation_euler = (math.radians(-6), math.radians(8 * side), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_material(endplate, mats["CarPaint_White"])

def build_octane_front_bullbar_and_lights(mats):
    """
    Builds the front tubular steel bullbar and 4 projector lights:
    - Upper bullbar horizontal loop
    - Lower skid bar
    - 2 main round projector headlights with bright glowing cyan halo rings
    - 2 lower auxiliary fog lights
    """
    # Upper Main Tubular Bar
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.028,
        depth=0.62,
        vertices=12,
        location=(0.0, 1.40, 0.22)
    )
    top_bar = bpy.context.active_object
    top_bar.name = "Bullbar_Top_Tube"
    top_bar.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(top_bar, mats["Chassis_MatteBlack"])

    # Lower Skid Tube
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.024,
        depth=0.52,
        vertices=12,
        location=(0.0, 1.44, 0.11)
    )
    bot_bar = bpy.context.active_object
    bot_bar.name = "Bullbar_Bottom_Tube"
    bot_bar.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(bot_bar, mats["Chassis_MatteBlack"])

    # Vertical Connecting Uprights
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024,
            depth=0.18,
            vertices=10,
            location=(0.20 * side, 1.41, 0.165)
        )
        upright = bpy.context.active_object
        upright.name = f"Bullbar_Upright_{'L' if side < 0 else 'R'}"
        assign_material(upright, mats["Chassis_MatteBlack"])

    # 2 Main Projector Headlights with Glowing Cyan Halo Rings
    for side in [-1, 1]:
        # Light Casing
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.082,
            depth=0.08,
            vertices=16,
            location=(0.32 * side, 1.38, 0.23)
        )
        casing = bpy.context.active_object
        casing.name = f"Headlight_Casing_{'L' if side < 0 else 'R'}"
        casing.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(casing, mats["Chassis_MatteBlack"])

        # Glowing Cyan Halo Outer Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.076,
            minor_radius=0.016,
            major_segments=20,
            minor_segments=8,
            location=(0.32 * side, 1.43, 0.23)
        )
        halo = bpy.context.active_object
        halo.name = f"Headlight_Halo_{'L' if side < 0 else 'R'}"
        halo.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(halo, mats["Neon_Cyan"])

        # Center White Projector Bulb
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.045,
            depth=0.025,
            vertices=14,
            location=(0.32 * side, 1.43, 0.23)
        )
        lens = bpy.context.active_object
        lens.name = f"Headlight_Lens_{'L' if side < 0 else 'R'}"
        lens.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(lens, mats["Headlight_WhiteBeam"])

    # 2 Lower Auxiliary Fog Lights
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.045,
            depth=0.04,
            vertices=14,
            location=(0.10 * side, 1.46, 0.11)
        )
        fog = bpy.context.active_object
        fog.name = f"FogLight_{'L' if side < 0 else 'R'}"
        fog.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(fog, mats["Headlight_WhiteBeam"])

def build_octane_wheels(mats):
    """
    Builds the 4 aggressive Rocket League deep-dish wheels:
    - Chunky grooved rubber tires
    - Polished chrome outer rim lips
    - Deep-dish 10-spoke gunmetal alloy centers
    - Red racing brake calipers and brake discs
    """
    wheel_configs = [
        # (name, x, y, z, tire_radius, tire_width, rim_radius)
        ("Front_L", -0.74,  0.98, 0.38, 0.40, 0.28, 0.25),
        ("Front_R",  0.74,  0.98, 0.38, 0.40, 0.28, 0.25),
        ("Rear_L",  -0.78, -1.05, 0.42, 0.44, 0.32, 0.27),
        ("Rear_R",   0.78, -1.05, 0.42, 0.44, 0.32, 0.27),
    ]

    for name, wx, wy, wz, r_tire, w_tire, r_rim in wheel_configs:
        is_right = (wx > 0)
        side_mult = 1 if is_right else -1

        # 1. Tire Rubber (Torus with thick cross section)
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
        assign_material(tire, mats["Tire_Rubber"])
        apply_smooth(tire)

        # 2. Chrome Outer Rim Lip
        outer_rim_x = wx + (w_tire * 0.52 * side_mult)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r_rim,
            minor_radius=0.024,
            major_segments=24,
            minor_segments=10,
            location=(outer_rim_x, wy, wz)
        )
        rim_lip = bpy.context.active_object
        rim_lip.name = f"RimLip_{name}"
        rim_lip.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(rim_lip, mats["Polished_Chrome"])
        apply_smooth(rim_lip)

        # 3. Deep-Dish Gunmetal 10-Spoke Wheel Face
        dish_center_x = outer_rim_x - (0.045 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.075,
            depth=0.04,
            vertices=16,
            location=(dish_center_x, wy, wz)
        )
        hub = bpy.context.active_object
        hub.name = f"WheelHub_{name}"
        hub.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(hub, mats["Polished_Chrome"])

        # 10 Radial Spokes
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            spoke_y = wy + math.cos(angle) * (r_rim * 0.52)
            spoke_z = wz + math.sin(angle) * (r_rim * 0.52)
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(dish_center_x + (0.015 * side_mult), spoke_y, spoke_z)
            )
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{name}_{i}"
            spoke.scale = (0.02, 0.032, r_rim * 0.85)
            spoke.rotation_euler = (angle, 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            assign_material(spoke, mats["Gunmetal_Alloy"])

        # 4. Brake Disc & Red Racing Caliper
        brake_disc_x = wx - (0.04 * side_mult)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_rim * 0.72,
            depth=0.02,
            vertices=20,
            location=(brake_disc_x, wy, wz)
        )
        disc = bpy.context.active_object
        disc.name = f"BrakeDisc_{name}"
        disc.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(disc, mats["Gunmetal_Alloy"])

        # Red Caliper
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(brake_disc_x, wy + (r_rim * 0.55), wz)
        )
        caliper = bpy.context.active_object
        caliper.name = f"BrakeCaliper_{name}"
        caliper.scale = (0.045, 0.065, 0.12)
        bpy.ops.object.transform_apply(scale=True)
        assign_material(caliper, mats["Engine_Red"])

# ---------------------------------------------------------
# Scene Environment, Camera & Studio Lighting
# ---------------------------------------------------------

def setup_studio_environment():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.film_transparent = False

    # Floor with subtle stadium grid line
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Stadium_Floor"
    floor_mat = bpy.data.materials.new(name="Stadium_Turf_Floor")
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.12, 0.15, 0.14, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.65
    assign_material(floor, floor_mat)

    # Floor pitch line
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0.002))
    line = bpy.context.active_object
    line.name = "Stadium_Pitch_Line"
    line.scale = (0.08, 15.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    line_mat = bpy.data.materials.new(name="Pitch_Line_White")
    line_mat.use_nodes = True
    lbsdf = line_mat.node_tree.nodes.get("Principled BSDF")
    lbsdf.inputs["Base Color"].default_value = (0.9, 0.92, 0.95, 1.0)
    lbsdf.inputs["Roughness"].default_value = 0.5
    assign_material(line, line_mat)

    # World background dark stadium atmosphere
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.05, 0.08, 0.12, 1.0)
        bg_node.inputs["Strength"].default_value = 0.5

    # 3-Point Cinematic Studio Lights
    # Key Light (Warm Sunlight)
    key_light = bpy.data.lights.new(name="Key_Light", type='SUN')
    key_light.energy = 4.0
    key_light.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("Key_Light", key_light)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (5.0, 4.0, 8.0)
    key_obj.rotation_euler = (math.radians(52), math.radians(18), math.radians(-38))

    # Rim / Accent Light (Cool Stadium Blue)
    rim_light = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_light.energy = 450.0
    rim_light.color = (0.35, 0.75, 1.0)
    rim_light.size = 3.5
    rim_obj = bpy.data.objects.new("Rim_Light", rim_light)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-4.0, -5.0, 4.5)
    rim_obj.rotation_euler = (math.radians(-50), math.radians(25), math.radians(140))

    # Fill Light (Soft warm bounce)
    fill_light = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_light.energy = 180.0
    fill_light.color = (0.9, 0.92, 1.0)
    fill_light.size = 4.0
    fill_obj = bpy.data.objects.new("Fill_Light", fill_light)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (4.0, -3.0, 3.0)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-20), math.radians(30))

    # Camera matching the exact 3/4 beauty angle of media_1790263831226.png
    cam_data = bpy.data.cameras.new(name="Beauty_Camera")
    cam_data.lens = 48.0
    cam_obj = bpy.data.objects.new("Beauty_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (3.5, 3.8, 1.85)
    direction = Vector((0.0, 0.05, 0.55)) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.camera = cam_obj

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
def main():
    print("=== BUILDING HIGH-FIDELITY 1:1 ROCKET LEAGUE OCTANE IN BLENDER ===")
    reset_scene()
    mats = create_materials()
    
    # Assemble all authentic components
    build_octane_chassis_and_fenders(mats)
    build_octane_cockpit(mats)
    build_octane_side_body_and_rear_fenders(mats)
    build_octane_engine_bay_and_thrusters(mats)
    build_octane_high_downforce_wing(mats)
    build_octane_front_bullbar_and_lights(mats)
    build_octane_wheels(mats)
    
    setup_studio_environment()

    # Save cleanly to .blend file
    blend_path = "/Users/elijahjohnson/67/nothing/nah/leuge of rockets/rocket_league_car.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master car scene to {blend_path}")

    # Render image
    render_path = "/Users/elijahjohnson/67/nothing/nah/leuge of rockets/blueprint_car_render.png"
    bpy.context.scene.render.filepath = render_path
    print(f"Rendering blueprint beauty shot to {render_path}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render complete: {render_path}")

if __name__ == "__main__":
    main()
