# Phase 2 - Blender Mesh Prompts (feed this file to your 3D AI + Blender)

You are a senior Blender hard-surface artist. Turn Phase 1 concept art into game-ready 3D meshes.
Target: Blender 4.x / 5.x. Matches existing repo scripts: build_octane_*.py, build_forbidden_temple.py, build_sunset_stadium.py.

## Global constraints
- Car: <80k tris, 4.2m long x 2.1m wide, origin at ground center, Y-up, +Z forward to match rocket_league_car.blend
- Arena: <300k tris, regulation pitch with curved wall-to-ceiling transitions
- PBR 2048px max: BaseColor (sRGB) + Metallic + Roughness + Normal (Linear)
- Keep physics hitbox unchanged - visuals only, do not resize collision

## 2A. Car build task (repeat per concept_car_*.png)
Paste with concept image attached:
```
Convert this battle-car concept into a Blender game-ready mesh plan and build steps.

Required separate objects: Body, Canopy, Wheels_FL_FR_RL_RR, Bullbar, Spoiler, Boosters, Engine
Required materials: CarPaint_Blue (metallic), Trim_White, Tire_Rubber, Alloy_Gunmetal, Boost_Cyan (emissive), Brake_Red, Glass_Dark

Output:
1. Orthographic blueprint dimensions (length/width/height/wheelbase)
2. Modeling steps with modifiers (mirror, bevel, subdivision level - apply before export)
3. Material node setup per part
4. Retopo + UV (single 0-1 layout, mirrored where possible) + bake checklist
5. Rig: wheels as separate pivots for spin/steer, boosters as emissive anchors
6. Export settings for FBX + GLB
```

## 2B. Procedural rebuild (matches repo style)
Paste to code AI:
```
Extend build_octane_championship.py to generate a new variant from concept_car_dominus.png.
Keep function structure, add parameters for length/width/hood_slope/spoiler_style.
Keep separate materials listed above. Apply transforms, triangulate on export only.
Output a runnable Blender Python script.
```

Reference blends: rocket_league_car.blend, sunset_stadium_3x.blend, forbidden_temple.blend

## 2C. Arena build task
Paste with concept_arena.png attached:
```
Model this stadium as separate objects: Floor, Walls, CeilingCurve, Goals x2, Stands, Lights, LEDBoards.
Keep goal openings and wall curves identical to sunset_stadium_3x.blend so gameplay stays regulation.
UV unwrap floor for turf stripes, bake AO for stands.
```

## Done check
- [ ] All transforms applied, normals correct, no N-gons on curved panels
- [ ] Wheels pivot at axle center
- [ ] FBX + GLB test exports open clean in Blender
