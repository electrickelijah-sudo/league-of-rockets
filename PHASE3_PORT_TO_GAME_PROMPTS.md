# Phase 3 - Port Meshes Into Game (feed this file to your coding AI)

You are a game integrator. Port Phase 2 Blender exports into League of Rockets without breaking gameplay.
Repo: League_of_Rockets.html / index.html (Three.js + Cannon.js, uses three.min.js), UnityProject/ (Unity 6).

## 3A. Blender export (do first)
```
Car: File > Export > glTF 2.0 (.glb) + FBX. Apply transforms, Y-up, +Z forward to match existing Octane. Embed textures.
  Names: models/Car_Octane.glb, models/Car_Dominus.glb, models/Car_Fennec.glb, models/Car_Breakout.glb (+ .fbx copies)
Arena: File > Export > FBX, selected only, apply modifiers.
  Name: SunsetStadiumV2.fbx
Textures: 2048px PNG, sRGB for BaseColor, Linear for Metal/Rough/Normal
```

## 3B. Three.js web game (League_of_Rockets.html)
Task for code AI:
```
In League_of_Rockets.html, replace the primitive car builder with a GLB loader.
Keep Cannon.js BoxCollider hitbox exactly 1:1. Parent the loaded mesh to the physics body.
Wheels must spin/steer, Boost_Cyan material must pulse on boost.
Add a CAR_MODELS = {octane, dominus, fennec, breakout} selector and garage switcher.
Verify: car drives, jumps, ball collides, no scale drift.
```
Snippet pattern:
```js
loader.load('models/Car_Dominus.glb', (gltf)=>{
  carMesh = gltf.scene;
  carMesh.traverse(o=>{ if(o.isMesh){o.castShadow=true;} });
});
```

## 3C. Unity 6 project
Task for code AI:
```
1. Drop FBX into UnityProject/Assets/Art/Models/, textures into UnityProject/Assets/Art/Textures/
2. Import: Scale 1.0, Generate Colliders OFF, Materials: Use External URP/Lit
3. Prefab car: MeshFilter + existing CarController under Assets/Scripts/Car/, keep BoxCollider hitbox
4. Arena: swap SunsetStadiumArena.fbx / ForbiddenTempleArena.fbx reference in Assets/Scenes/MainArena.unity, keep ArenaSetup.cs + ArenaMeshBuilder.cs bounds
5. Verify play mode: drive, boost, goal triggers still fire
```

## Order
Do ONE car end-to-end first (Blender > GLB > HTML test), then batch the other 3. Then arena.

## Done check
- [ ] Hitbox unchanged, no gameplay regression
- [ ] 60fps on target hardware, textures <=2048px
- [ ] Both Three.js and Unity load the same FBX source
