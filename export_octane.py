import bpy
import bmesh
import json
import os
from mathutils import Vector

def export_octane():
    MAT_MAP = {
        'CarPaint_Cobalt': 'paint',
        'CarPaint_White': 'white_trim',
        'RacingStripe_White': 'racing_stripe',
        'Cockpit_Glass': 'glass',
        'Chassis_MatteBlack': 'chassis',
        'Polished_Chrome': 'chrome',
        'Gunmetal_Alloy': 'gunmetal',
        'Tire_Rubber': 'rubber',
        'Engine_Red': 'engine_red',
        'Neon_Cyan': 'neon_cyan',
        'Headlight_WhiteBeam': 'headlight_white',
        'Neon_Red': 'neon_red',
    }

    # Wheels definition (in Blender coords: X, Y, Z)
    # Three.js coords: X_three = X, Y_three = Z, Z_three = Y
    WHEELS = {
        'fl': {'prefix': 'Front_L', 'center': Vector((-0.68, 0.75, 0.35))},
        'fr': {'prefix': 'Front_R', 'center': Vector((0.68, 0.75, 0.35))},
        'rl': {'prefix': 'Rear_L',  'center': Vector((-0.70, -0.75, 0.38))},
        'rr': {'prefix': 'Rear_R',  'center': Vector((0.70, -0.75, 0.38))},
    }

    body_groups = {cat: {'positions': [], 'normals': []} for cat in set(MAT_MAP.values())}
    wheel_groups = {
        w_id: {
            'spin': {cat: {'positions': [], 'normals': []} for cat in ['rubber', 'gunmetal', 'chrome']},
            'fixed': {cat: {'positions': [], 'normals': []} for cat in ['gunmetal', 'engine_red']},
            'center': [round(WHEELS[w_id]['center'].x, 4),
                       round(WHEELS[w_id]['center'].z, 4),
                       round(WHEELS[w_id]['center'].y, 4)]
        }
        for w_id in WHEELS
    }

    def to_three(v):
        # Convert Blender (X, Y, Z) to Three.js forward (+Z): (X, Z, Y)
        return [round(v.x, 4), round(v.z, 4), round(v.y, 4)]

    def to_three_norm(n):
        return [round(n.x, 4), round(n.z, 4), round(n.y, 4)]

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if 'stadium' in obj.name.lower():
            continue

        assigned_wheel = None
        is_fixed = False
        for w_id, w_info in WHEELS.items():
            if w_info['prefix'] in obj.name:
                assigned_wheel = w_id
                if 'BrakeCaliper' in obj.name or 'BrakeDisc' in obj.name:
                    is_fixed = True
                break

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.faces.ensure_lookup_table()

        mat_names = [m.name for m in obj.data.materials if m]
        default_mat = mat_names[0] if mat_names else 'Chassis_MatteBlack'
        mw = obj.matrix_world

        for face in bm.faces:
            mat_name = default_mat
            if face.material_index < len(mat_names):
                mat_name = mat_names[face.material_index]
            cat = MAT_MAP.get(mat_name, 'chassis')

            fn = face.normal
            norm_3 = to_three_norm(mw.to_3x3() @ fn)

            # Extract 3 triangle vertices with reversed winding [0, 2, 1] to preserve counter-clockwise normals
            v0 = mw @ face.verts[0].co
            v1 = mw @ face.verts[2].co
            v2 = mw @ face.verts[1].co
            tri_verts = [v0, v1, v2]

            verts_3 = []
            for v_co in tri_verts:
                if assigned_wheel:
                    rel_pos = v_co - WHEELS[assigned_wheel]['center']
                    verts_3.append(to_three(rel_pos))
                else:
                    verts_3.append(to_three(v_co))

            target = None
            if assigned_wheel:
                w_dict = wheel_groups[assigned_wheel]['fixed'] if is_fixed else wheel_groups[assigned_wheel]['spin']
                if cat not in w_dict:
                    w_dict[cat] = {'positions': [], 'normals': []}
                target = w_dict[cat]
            else:
                target = body_groups[cat]

            for vp in verts_3:
                target['positions'].extend(vp)
                target['normals'].extend(norm_3)

        bm.free()

    body_clean = {k: v for k, v in body_groups.items() if len(v['positions']) > 0}
    for w_id in wheel_groups:
        wheel_groups[w_id]['spin'] = {k: v for k, v in wheel_groups[w_id]['spin'].items() if len(v['positions']) > 0}
        wheel_groups[w_id]['fixed'] = {k: v for k, v in wheel_groups[w_id]['fixed'].items() if len(v['positions']) > 0}

    output_data = {
        'body': body_clean,
        'wheels': wheel_groups
    }

    out_file = '/Users/elijahjohnson/67/nothing/nah/leuge of rockets/octane_model_data.js'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated 1:1 Rocket League Octane Geometry from Blender 5.1.2\n')
        f.write('const OCTANE_BLENDER_MODEL = ')
        json.dump(output_data, f, separators=(',', ':'))
        f.write(';\n')

    print(f'Successfully exported Octane model to {out_file}!')

if __name__ == '__main__':
    export_octane()
