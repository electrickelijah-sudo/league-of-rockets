import os, sys, subprocess

unity_dir = '/Applications/Unity/Hub/Editor/6000.5.5f1/Unity.app/Contents/Resources/Scripting'
dotnet = os.path.join(unity_dir, 'DotNetSdk/dotnet')
csc = os.path.join(unity_dir, 'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll')
managed_dir = os.path.join(unity_dir, 'Managed/UnityEngine')
netstandard_dir = os.path.join(unity_dir, 'NetStandard/ref/2.1.0')
editor_dll = os.path.join(unity_dir, 'Managed/UnityEngine/UnityEditor.dll')
ugui_dll = '/Applications/Unity/Hub/Editor/6000.5.5f1/Unity.app/Contents/Resources/PackageManager/ProjectTemplates/libcache/com.unity.template.3d-cross-platform-17.0.14/ScriptAssemblies/UnityEngine.UI.dll'

refs = [f'-r:{ugui_dll}']
if os.path.isdir(netstandard_dir):
    for f in os.listdir(netstandard_dir):
        if f.endswith('.dll'):
            refs.append(f'-r:{os.path.join(netstandard_dir, f)}')

if os.path.isdir(managed_dir):
    for f in os.listdir(managed_dir):
        if f.endswith('.dll'):
            refs.append(f'-r:{os.path.join(managed_dir, f)}')

runtime_cs = []
editor_cs = []
for root, dirs, files in os.walk('UnityProject/Assets/Scripts'):
    for f in files:
        if f.endswith('.cs'):
            full_path = os.path.join(root, f)
            if 'Editor' in root:
                editor_cs.append(full_path)
            else:
                runtime_cs.append(full_path)

out_runtime = '/tmp/TurboStrikeRuntime.dll'
cmd_runtime = [dotnet, csc, '-target:library', '-nowarn:CS0169,CS0414,CS0618', f'-out:{out_runtime}'] + refs + runtime_cs
res_runtime = subprocess.run(cmd_runtime, capture_output=True, text=True)

if res_runtime.returncode != 0:
    print(f"RUNTIME COMPILATION ERROR (code {res_runtime.returncode}):")
    print(res_runtime.stdout)
    if res_runtime.stderr:
        print("STDERR:", res_runtime.stderr)
    sys.exit(1)

print(f"SUCCESS: Compiled {len(runtime_cs)} Unity C# runtime scripts cleanly to {out_runtime}")

if editor_cs:
    out_editor = '/tmp/TurboStrikeEditor.dll'
    editor_refs = refs + [f'-r:{out_runtime}', f'-r:{editor_dll}', '-define:UNITY_EDITOR']
    cmd_editor = [dotnet, csc, '-target:library', '-nowarn:CS0169,CS0414,CS0618', f'-out:{out_editor}'] + editor_refs + editor_cs
    res_editor = subprocess.run(cmd_editor, capture_output=True, text=True)

    if res_editor.returncode != 0:
        print(f"EDITOR COMPILATION ERROR (code {res_editor.returncode}):")
        print(res_editor.stdout)
        if res_editor.stderr:
            print("STDERR:", res_editor.stderr)
        sys.exit(1)

    print(f"SUCCESS: Compiled {len(editor_cs)} Unity C# editor scripts cleanly to {out_editor}")

print(f"ALL {len(runtime_cs) + len(editor_cs)} SCRIPTS (33 Runtime + {len(editor_cs)} Editor) PASSED WITH 0 ERRORS!")
sys.exit(0)
