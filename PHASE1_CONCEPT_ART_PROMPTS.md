# Phase 1 - Concept Art Prompts (feed this file to your image AI)

You are a AAA concept artist for a Rocket League-style vehicular sports game.
Goal: make League of Rockets look realistic, professional, and authentic like Rocket League, with variable cars.

Project context:
- Web game: League_of_Rockets.html / index.html (Three.js + Cannon.js)
- Unity project: UnityProject/Assets/Art/Models/, UnityProject/Assets/Scenes/MainArena.unity
- Existing style ref: rocket_league_car.blend (Octane), sunset_stadium_3x.blend, forbidden_temple.blend

Generate 3 categories. All 16:9, photorealistic, high detail, no HUD, no watermark, no cartoon.

## 1A. Arena concept
Copy-paste:
```
photorealistic Rocket League-style stadium concept art, sunset championship arena, enclosed rectangular pitch with curved wall-to-ceiling transitions, glowing blue and orange hex-pattern goals, green turf with mowed stripes and white field lines, packed crowd stands with LED banners and floodlights, dusk sky visible through open roof, cinematic wide-angle, high detail, octane render, Unreal Engine 5, 8k --ar 16:9 --style raw
Negative: open field, real soccer stadium, no walls, no ceiling, blurry, cartoon, low poly
```

## 1B. Variable car meshes (run 4 times, change bracket)
Copy-paste:
```
photorealistic Rocket League [Octane / Dominus / Fennec / Breakout] battle-car concept, 3/4 front hero view + side + rear + top orthographic on same sheet, white studio background, metallic cobalt blue paint with white racing stripes, exposed rear engine, large off-road tires with deep-dish gunmetal wheels, roof scoop and rear rocket boosters with cyan glow, hard-surface automotive design, PBR, game-ready vehicle sheet --ar 16:9 --style raw
Negative: cartoon, toy, deformed wheels, asymmetric, blurry, human driver, interior
```

Variants to generate:
1. Octane (boxy, tall, baseline - match rocket_league_car.blend)
2. Dominus (long hood, low muscle car)
3. Fennec (boxy van, flat front)
4. Breakout (long, low, sharp wedge)

## 1C. Gameplay concept
Copy-paste:
```
cinematic Rocket League gameplay still, blue Octane car aerialing to hit glowing white ball in sunset stadium, orange car defending below, boost trails and ball cam motion blur, broadcast sports camera angle, dramatic rim lighting, photorealistic, high contrast, 8k --ar 16:9
Negative: empty scene, UI overlay, HUD, watermark, cartoon
```

## Output naming
Save winners as:
- concept_arena.png
- concept_car_octane.png
- concept_car_dominus.png
- concept_car_fennec.png
- concept_car_breakout.png
- concept_gameplay.png

Pick 1 winner per car before moving to Phase 2.
