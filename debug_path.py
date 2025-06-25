import os

current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

backend_app_dir = "/home/ubuntu/repos/bot_forge/backend/app"
potential_paths = [
    os.path.join(backend_app_dir, "../../../libs/root-bot/topgun"),
    os.path.join(backend_app_dir, "../../libs/root-bot/topgun"),
    os.path.join(backend_app_dir, "../libs/root-bot/topgun"),
    "/home/ubuntu/repos/bot_forge/libs/root-bot/topgun"
]

for i, path in enumerate(potential_paths):
    abs_path = os.path.abspath(path)
    exists = os.path.exists(abs_path)
    print(f"Path {i+1}: {abs_path}")
    print(f"  Exists: {exists}")
    if exists:
        print(f"  Contents: {os.listdir(abs_path)}")
    print()
