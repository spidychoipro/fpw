import os
import sys
import getpass
import hashlib
import json

CONFIG_DIR = os.path.expanduser("~/.config/fpw")
SHADOW_FILE = os.path.join(CONFIG_DIR, ".shadow")

def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(SHADOW_FILE):
        with open(SHADOW_FILE, "w") as f:
            json.dump({}, f)

def load_passwords():
    with open(SHADOW_FILE, "r") as f:
        return json.load(f)

def save_passwords(data):
    with open(SHADOW_FILE, "w") as f:
        json.dump(data, f)

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

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

    for attempt in range(3):
        pw = getpass.getpass("비밀번호 입력: ")
        if hash_password(pw, abs_path) == passwords[abs_path]:
            print(f"인증 성공. 접근 허용: {abs_path}")
            print(abs_path)  # 셸 스크립트가 읽을 수 있도록 경로 출력
            sys.exit(0)  # 성공 종료
        else:
            print(f"비밀번호가 틀렸습니다. ({2 - attempt}회 남음)")

    print("비밀번호 3회 오류. 접근 차단.")
    sys.exit(1)

def print_usage():
    print("사용법:")
    print("  python main.py set <폴더경로>    # 비밀번호 설정/변경")
    print("  python main.py enter <폴더경로>  # 비밀번호 입력 및 인증")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    folder = sys.argv[2]

    if command == "set":
        set_password(folder)
        sys.exit(0)
    elif command == "enter":
        enter_folder(folder)
    else:
        print_usage()
        sys.exit(1)