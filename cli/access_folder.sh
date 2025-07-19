#!/bin/bash
if [ $# -ne 1 ]; then
    echo "사용법: $0 <폴더경로>"
    exit 1
fi

# Python 스크립트 실행하고 출력(폴더 경로) 캡처
folder_path=$(python main.py enter "$1" 2>/dev/null)
exit_code=$?

if [ $exit_code -eq 0 ]; then
    cd "$folder_path" || {
        echo "오류: '$folder_path'로 이동할 수 없습니다. 권한을 확인하세요."
        exit 1
    }
    echo "현재 디렉토리: $(pwd)"
else
    exit $exit_code  # Python 스크립트의 오류 코드 전달
fi