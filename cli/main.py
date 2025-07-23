import os
import sys
import getpass
import hashlib
import json
import subprocess
import signal
import time

CONFIG_DIR = os.path.expanduser("~/.config/fpw")
SHADOW_FILE = os.path.join(CONFIG_DIR, ".shadow")
SESSION_FILE = os.path.join(CONFIG_DIR, ".sessions")

def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        os.chmod(CONFIG_DIR, 0o700)  # Only user can access
    if not os.path.exists(SHADOW_FILE):
        with open(SHADOW_FILE, "w") as f:
            json.dump({}, f)
        os.chmod(SHADOW_FILE, 0o600)  # Only user can read/write
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            json.dump({}, f)
        os.chmod(SESSION_FILE, 0o600)

def load_passwords():
    with open(SHADOW_FILE, "r") as f:
        return json.load(f)

def save_passwords(data):
    with open(SHADOW_FILE, "w") as f:
        json.dump(data, f)
    os.chmod(SHADOW_FILE, 0o600)

def load_sessions():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)
    os.chmod(SESSION_FILE, 0o600)

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def is_session_valid(folder_path, session_timeout=3600):  # 1 hour default
    sessions = load_sessions()
    abs_path = os.path.abspath(folder_path)
    
    if abs_path in sessions:
        last_access = sessions[abs_path]
        if time.time() - last_access < session_timeout:
            # Update last access time
            sessions[abs_path] = time.time()
            save_sessions(sessions)
            return True
        else:
            # Session expired, remove it
            del sessions[abs_path]
            save_sessions(sessions)
    
    return False

def create_session(folder_path):
    sessions = load_sessions()
    abs_path = os.path.abspath(folder_path)
    sessions[abs_path] = time.time()
    save_sessions(sessions)

def remove_session(folder_path):
    sessions = load_sessions()
    abs_path = os.path.abspath(folder_path)
    if abs_path in sessions:
        del sessions[abs_path]
        save_sessions(sessions)

def set_password(folder_path):
    ensure_config()
    passwords = load_passwords()

    abs_path = os.path.abspath(folder_path)
    if not os.path.isdir(abs_path):
        print(f"오류: '{abs_path}'는 유효한 폴더가 아닙니다.")
        sys.exit(1)

    if abs_path in passwords:
        old_pw = getpass.getpass("현재 비밀번호 입력: ")
        hashed_old = hash_password(old_pw, abs_path)
        if passwords[abs_path] != hashed_old:
            print("비밀번호가 틀렸습니다.")
            sys.exit(1)
        print("새 비밀번호를 설정하세요.")
    else:
        print("새 비밀번호를 설정하세요.")

    while True:
        pw1 = getpass.getpass("새 비밀번호: ")
        pw2 = getpass.getpass("비밀번호 확인: ")
        if pw1 != pw2:
            print("비밀번호가 일치하지 않습니다. 다시 시도하세요.")
        elif not pw1:
            print("비밀번호는 비워둘 수 없습니다.")
        else:
            break

    passwords[abs_path] = hash_password(pw1, abs_path)
    save_passwords(passwords)
    print(f"'{abs_path}' 폴더 비밀번호가 설정되었습니다.")

def start_protected_shell(folder_path):
    """Start an interactive shell in the protected folder"""
    abs_path = os.path.abspath(folder_path)
    
    # Get user's preferred shell
    user_shell = os.environ.get('SHELL', '/bin/bash')
    
    print(f"\n=== fpw 보호된 셸 세션 시작 ===")
    print(f"폴더: {abs_path}")
    print(f"셸 종료시 (exit 또는 Ctrl+D) 폴더 접근이 자동으로 잠깁니다.")
    print("=" * 50)
    
    try:
        # Change to the target directory and start shell
        process = subprocess.Popen(
            [user_shell],
            cwd=abs_path,
            env=dict(os.environ, 
                    PS1=f"[fpw:{os.path.basename(abs_path)}] $ ",  # Custom prompt
                    FPW_PROTECTED_DIR=abs_path)  # Environment variable for reference
        )
        
        # Wait for the shell to exit
        return_code = process.wait()
        
    except KeyboardInterrupt:
        print("\n셸 세션이 중단되었습니다.")
        return_code = 1
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return_code = 1
    
    # Clean up session when shell exits
    remove_session(abs_path)
    print(f"\n=== fpw 보호된 셸 세션 종료 ===")
    print(f"'{abs_path}' 폴더가 다시 잠겼습니다.")
    
    return return_code

def enter_folder(folder_path):
    ensure_config()
    passwords = load_passwords()
    abs_path = os.path.abspath(folder_path)

    if not os.path.isdir(abs_path):
        print(f"오류: '{abs_path}'는 유효한 폴더가 아닙니다.")
        sys.exit(1)

    if abs_path not in passwords:
        print("비밀번호가 설정되지 않은 폴더입니다.")
        sys.exit(1)

    # Check if there's a valid session
    if is_session_valid(abs_path):
        print(f"기존 세션을 사용합니다: {abs_path}")
        return start_protected_shell(abs_path)

    # Authentication required
    for attempt in range(3):
        pw = getpass.getpass("비밀번호 입력: ")
        if hash_password(pw, abs_path) == passwords[abs_path]:
            print(f"인증 성공!")
            create_session(abs_path)
            return start_protected_shell(abs_path)
        else:
            print(f"비밀번호가 틀렸습니다. ({2 - attempt}회 남음)")

    print("비밀번호 3회 오류. 접근 차단.")
    sys.exit(1)

def list_protected_folders():
    """List all folders that have passwords set"""
    ensure_config()
    passwords = load_passwords()
    sessions = load_sessions()
    
    if not passwords:
        print("보호된 폴더가 없습니다.")
        return
    
    print("보호된 폴더 목록:")
    print("-" * 60)
    for folder, _ in passwords.items():
        status = "🔓 활성 세션" if folder in sessions and is_session_valid(folder, 0) else "🔒 잠김"
        print(f"{status} {folder}")

def remove_password(folder_path):
    """Remove password protection from a folder"""
    ensure_config()
    passwords = load_passwords()
    abs_path = os.path.abspath(folder_path)
    
    if abs_path not in passwords:
        print("이 폴더는 보호되지 않습니다.")
        sys.exit(1)
    
    # Verify current password
    pw = getpass.getpass("현재 비밀번호 입력: ")
    if hash_password(pw, abs_path) != passwords[abs_path]:
        print("비밀번호가 틀렸습니다.")
        sys.exit(1)
    
    # Remove password and any active session
    del passwords[abs_path]
    save_passwords(passwords)
    remove_session(abs_path)
    
    print(f"'{abs_path}' 폴더의 비밀번호 보호가 제거되었습니다.")

def print_usage():
    print("fpw - Folder Password Wrapper")
    print("사용법:")
    print("  fpw set <폴더경로>      # 비밀번호 설정/변경")
    print("  fpw enter <폴더경로>    # 비밀번호 입력 및 보호된 셸 시작")
    print("  fpw list               # 보호된 폴더 목록 보기")
    print("  fpw remove <폴더경로>   # 비밀번호 보호 제거")
    print("")
    print("보호된 셸에서는:")
    print("  - 해당 폴더에서 모든 작업 가능")
    print("  - 'exit' 또는 Ctrl+D로 종료시 자동 잠금")
    print("  - 세션은 1시간 동안 유지됨")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_protected_folders()
        sys.exit(0)
    elif len(sys.argv) < 3 and command not in ["list"]:
        print_usage()
        sys.exit(1)

    if len(sys.argv) >= 3:
        folder = sys.argv[2]
    
    if command == "set":
        set_password(folder)
        sys.exit(0)
    elif command == "enter":
        enter_folder(folder)
    elif command == "remove":
        remove_password(folder)
        sys.exit(0)
    else:
        print_usage()
        sys.exit(1)
