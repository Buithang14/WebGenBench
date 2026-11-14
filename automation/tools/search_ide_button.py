import os
from pathlib import Path

app_dir = Path(r"E:\kì 2 năm 4\NCKH\Cursor\cursor\resources\app\out")
for p in app_dir.rglob("*.js"):
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
        if "IDE ↗" in content or "classic editor" in content:
            print(f"Found in {p.name}")
            idx = content.find("IDE ↗")
            if idx != -1:
                print("Context:", content[max(0, idx-100):min(len(content), idx+100)])
    except Exception:
        pass

