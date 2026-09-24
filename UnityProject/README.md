# Rocket League Unity Project (1 Unit = 1 Meter Scale)

This Unity package implements an authentic Rocket League stadium, vehicle physics, ball dynamics, and match management according to exact 1:1 scale specifications.

---

## Arena Specifications (1 Unit = 1 Meter)

- **Field Dimensions**:
  - Length: 100 m ($X = -50$ to $+50$)
  - Width: 80 m ($Z = -40$ to $+40$)
  - Playable grass height: 0.1 m
- **Side Walls**:
  - Wall height: 8 m
  - Wall thickness: 0.5 m
- **Curved Transitions**:
  - Floor-to-wall quarter-pipe transition: 8 m radius
  - Corner radius: 12 m
- **Upper Curved Wall & Ceiling**:
  - Upper curved wall: $Y = 8\text{m}$ to $12\text{m}$
  - Arena ceiling height: 20 m
  - Curved transparent dome: 110 m long $\times$ 90 m wide $\times$ 20 m high (thickness 0.25 m)
- **Goals**:
  - Blue Goal at $X = -50\text{m}$, Orange Goal at $X = +50\text{m}$
  - Width: 20 m, Height: 8 m, Depth: 8 m
  - Side posts & top beam: 0.75 m thick
  - Goal detection volume: 19 m wide $\times$ 7 m high $\times$ 7 m deep
- **Center Field**:
  - Center circle radius: 8 m
  - Center line: 80 m length $\times$ 0.15 m width
  - Kickoff ball position: $(0, 1.25, 0)$
- **Boost Pads**:
  - 12 Small Pads (Diameter 2 m, Height 0.15 m, $+12$ boost, 4s respawn) placed at exact suggested coordinates
  - 4 Large Corner Pads (Diameter 4 m, Height 0.2 m, $+100$ boost, 10s respawn) at $(\pm 42, 0.15, \pm 32)$

---

## Vehicle Specifications

- **Chassis Dimensions**:
  - Length: 4.2 m, Width: 2.0 m, Height: 1.3 m
  - Body: 3.6 m L $\times$ 1.8 m W $\times$ 0.9 m H
  - Roof: 1.8 m L $\times$ 1.6 m W $\times$ 0.45 m H
  - Front Bumper: 1.8 m W $\times$ 0.35 m H $\times$ 0.3 m D
  - Spoiler: 1.7 m W $\times$ 0.35 m H
  - Wheelbase: 2.6 m (Front wheels at $+1.3\text{m}$, Rear wheels at $-1.3\text{m}$)
  - Wheel spacing: 1.55 m
  - Wheels: 0.8 m diameter (0.4 m radius) $\times$ 0.35 m width
  - Ground clearance: 0.25 m
- **Vehicle Physics**:
  - Rigidbody mass: 1500 kg
  - Center of mass: 0.3 m above ground
  - Wheel suspension travel: 0.3 m
  - Max ground speed: 22 m/s
  - Max boost speed: 35 m/s
  - Boost acceleration: ~25 m/s²
  - Jump force: ~7 m/s upward impulse
  - Double jump & directional air roll / dodge flipping

---

## Ball Specifications

- Ball diameter: 2.5 m (Radius: 1.25 m)
- Sphere collider: Radius 1.25 m
- Kickoff center: $(0, 1.25, 0)$
- Dynamic bumper impact impulse multiplier and speed trail

---

## Team Spawn Positions

- **Blue Team** (Facing center $+X$, rotation $Y = 90^\circ$):
  - Player: $(-35, 0.8, 0)$
  - Teammate 1: $(-30, 0.8, -20)$
  - Teammate 2: $(-30, 0.8, 20)$
- **Orange Team** (Facing center $-X$, rotation $Y = -90^\circ$):
  - Player: $(35, 0.8, 0)$
  - Teammate 1: $(30, 0.8, -20)$
  - Teammate 2: $(30, 0.8, 20)$

---

## How to Run in Unity Editor

1. Open **Unity Hub** and click **Open** $\rightarrow$ select the `UnityProject` folder.
2. In the top menu bar, click:
   - **Rocket League** $\rightarrow$ **1. Build Complete Arena Scene**: Generates the 100m $\times$ 80m stadium, ramps, goals, dome, boost pads, and ball.
   - **Rocket League** $\rightarrow$ **2. Create Player Car (Exact Dimensions)**: Spawns the player car at $(-35, 0.8, 0)$ with 4-wheel suspension and exact body parts.
   - **Rocket League** $\rightarrow$ **3. Validate Dimensions & Physics Specs**: Verifies all measurements in the Unity console.
3. Press **Play** in Unity:
   - `W` / `S`: Drive / Reverse
   - `A` / `D`: Steer
   - `Left Shift` / `Space`: Handbrake drift
   - `Right Click` / `J`: Jump (double tap to double jump or dodge)
   - `Left Click` / `Left Ctrl`: Rocket Boost
   - `C`: Toggle Ball Cam / Car Cam
