import pywinauto
import win32gui
import ctypes
import win32con

from automation.base_adapter import ensure_interactive_desktop
ensure_interactive_desktop()

desktop = pywinauto.Desktop(backend="uia")
for win in desktop.windows():
    try:
        t = win.window_text()
        if "Cursor" in t or "Agents" in t:
            print("Found window:", t, "Handle:", win.handle)
            # Find all buttons or links
            for elem in win.descendants():
                ctrl = elem.element_info.control_type
                name = elem.element_info.name
                auto_id = elem.element_info.automation_id
                if ctrl in ["Button", "MenuItem", "Hyperlink", "TabItem"] or "IDE" in (name or ""):
                    print(f"   [{ctrl}] name='{name}' auto_id='{auto_id}'")
    except Exception:
        pass

