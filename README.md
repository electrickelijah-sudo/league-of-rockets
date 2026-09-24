# 🚀 League of Rockets

Welcome to **League of Rockets**! A Rocket League inspired vehicular sports game featuring a 1:1 authentic Octane car, Sunset Stadium arena, and full physics-based driving and aerial gameplay.

Collaborators: **Elijah Johnson** & **Josh Johnson**.

---

## 🎮 How to Play

### Option 1: Instant Launch (Mac)
Double-click `Play_Game_Mac.command` to immediately launch the game in your default browser.

### Option 2: Browser (Mac / Windows / Linux)
Open `League_of_Rockets.html` in any modern web browser (Chrome, Safari, Edge, Firefox).

### Option 3: Mac App
Run `League of Rockets.app` directly on macOS.

---

## 🏎️ Controls
- **Drive / Steer**: `W` / `A` / `S` / `D` or Arrow Keys
- **Boost (Supersonic Rocket Thrusters)**: `Spacebar` or `Shift`
- **Jump / Double Jump**: `Spacebar`
- **Air Roll / Pitch**: `W`/`S` and `A`/`D` while in mid-air
- **Powerslide / Handbrake**: `Shift`
- **Camera Toggle (Ball Cam / Car Cam)**: `C`
- **Reset Ball / Car**: `R`

---

## 🛠️ Project Structure

- **Playable Game**:
  - `League_of_Rockets.html`: Self-contained 3D game powered by Three.js and Cannon.js physics.
  - `three.min.js`: Local Three.js 3D graphics library.
  - `Play_Game_Mac.command`: 1-click macOS launcher.
  - `Play_Game_Windows.bat`: 1-click Windows launcher.

- **Blender 3D Models & Assets (Blender 5.x)**:
  - `rocket_league_car.blend`: The 1:1 authentic Rocket League Octane 3D model.
    - Dual Alpine White racing stripes with Cobalt Blue metallic paint.
    - Sweeping Titanium White trim lips over curved arched fenders.
    - Raked cockpit canopy with white A-pillars and dual-port roof scoop.
    - Exposed rear V8 engine with bright red valve covers (`#D32F2F`) and 8 chrome velocity stacks.
    - Dual rocket boost thruster nozzles with glowing cyan plasma cores.
    - Deep-dish 10-spoke gunmetal alloy wheels, hollow rubber tires, and red brake calipers.
    - Front tubular bullbar with glowing cyan projector halos and fog lights.
  - `sunset_stadium_3x.blend`: 3X official regulation Sunset Stadium arena with neon hex goals, curved ramp walls, and stadium lighting.
  - `forbidden_temple.blend`: Forbidden Temple stadium model.
  - `build_octane_championship.py`: Complete Python script to procedurally regenerate and customize the Octane in Blender.

- **Unity Project**:
  - `UnityProject/`: Complete Unity 6 HDRP/URP project setup with vehicle controller, arena models, and materials.

---

## 🤝 How Josh Johnson & Elijah Work Together on GitHub

### 1. Push this Repository to GitHub
Run the following commands in Terminal from this folder:
```bash
git remote add origin https://github.com/electrickelijah-sudo/league-of-rockets.git
git branch -M main
git push -u origin main
```
*(If the repo `league-of-rockets` is not created yet on GitHub, create a new empty repository named `league-of-rockets` on https://github.com/new first!)*

### 2. Add Josh Johnson as a Collaborator
1. Go to your repository on GitHub: `https://github.com/electrickelijah-sudo/league-of-rockets`
2. Click **Settings** (top right tab).
3. In the left sidebar, click **Collaborators**.
4. Click **Add people**.
5. Type **Josh Johnson**'s GitHub username or email address and click **Add to this repository**.
6. Josh will receive an email invitation to accept. Once accepted, he will have full read/write access to work on the game with you!

### 3. For Josh: How to Clone & Work
```bash
git clone https://github.com/electrickelijah-sudo/league-of-rockets.git
cd league-of-rockets
```
To pull latest updates:
```bash
git pull
```
To save and share changes:
```bash
git add .
git commit -m "Describe what was updated"
git push
```
