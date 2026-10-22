import os
import sys
import subprocess
import webbrowser
import time

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "backend", "data", "rimberio_enterprise.db")
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found at: {db_path}")
        return

    python_dir = os.path.dirname(sys.executable)
    sqlite_web_exe = os.path.join(python_dir, "Scripts", "sqlite_web.exe")
    
    if not os.path.exists(sqlite_web_exe):
        # Fallback to local appdata scripts
        sqlite_web_exe = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python310\Scripts\sqlite_web.exe")

    port = 8090
    print(f"============================================================")
    print(f"  RIMBERIO ENTERPRISE DATABASE WORKBENCH (WEB GUI)")
    print(f"============================================================")
    print(f" Database File: {db_path}")
    print(f" Opening in your Web Browser at: http://127.0.0.1:{port}")
    print(f" Press Ctrl + C to exit.")
    print(f"============================================================")

    # Launch browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://127.0.0.1:{port}")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    cmd = [sqlite_web_exe, db_path, f"--port={port}", "--host=127.0.0.1"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDatabase viewer stopped.")

if __name__ == "__main__":
    main()
