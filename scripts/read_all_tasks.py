import os, yaml

tasks_dir = 'tasks'
for t in sorted(os.listdir(tasks_dir)):
    meta_path = os.path.join(tasks_dir, t, 'task_meta.yaml')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"\n=== [{data.get('task_id')}] {data.get('name')} ===")
        print("Prompt summary:")
        prompt_path = os.path.join(tasks_dir, t, 'prompt.txt')
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as pf:
                print(" ", pf.readline().strip())
                print(" ", pf.readline().strip())
        print("UI Requirements:")
        for u in data.get('ui_requirements', []):
            print(f"  * {u}")
