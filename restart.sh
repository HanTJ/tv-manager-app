#!/bin/bash

# 고유 식별자 정의
APP_ID="TV_MANAGER_SERVER_8080"
LOG_FILE="server.log"

echo "=== TV Manager Server Management ==="

# 1. 고유 식별자를 가진 기존 프로세스만 정밀 타격하여 종료
echo "Stopping TV Manager server (ID: $APP_ID)..."
# -f: 전체 명령행 매칭, -9: 강제 종료
pkill -9 -f "$APP_ID" || echo "No existing server found."
sleep 2

# 2. 서버 재기동 (명령행 끝에 고유 식별자 추가)
echo "Starting TV Manager server on port 8080..."
# 명령행 끝에 주석(#)과 함께 고유 ID를 붙여 나중에 pkill -f로 식별 가능하게 함
nohup uv run python app.py --id=$APP_ID > "$LOG_FILE" 2>&1 &

# 3. 기동 확인 (포트 점유 여부 체크)
echo "Checking server status..."
for i in {1..10}; do
    if netstat -tuln | grep -q ":8080 "; then
        echo "------------------------------------------------"
        echo "✅ Server started successfully!"
        echo "🔗 URL: http://$(curl -s ifconfig.me || echo "localhost"):8080"
        echo "🆔 Process ID matching string: $APP_ID"
        echo "------------------------------------------------"
        exit 0
    fi
    sleep 1
done

echo "❌ Error: Server failed to start. Last 10 lines of $LOG_FILE:"
tail -n 10 "$LOG_FILE"
exit 1
