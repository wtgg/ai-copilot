#!/usr/bin/env bash
# 临时启动 + 测试 uvicorn(可删)
set +e
cd /mnt/e/Users/wt/codes/ai_copilot
source .venv/bin/activate

LLM_MOCK=true nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > /tmp/uvicorn.log 2>&1 &
PID=$!
echo "started pid=$PID"

# 等到 Uvicorn 启动成功 或 超时 180s(torch+bge-m3 加载 80s+)
for i in $(seq 1 90); do
  if grep -q "Uvicorn running on" /tmp/uvicorn.log 2>/dev/null; then
    echo "STARTED in ~$((i*2))s"
    break
  fi
  sleep 2
done

# 保险: 多睡 3s 等 'Application startup complete'
sleep 3

echo "=== uvicorn log ==="
cat /tmp/uvicorn.log

echo "=== /docs ==="
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/docs

echo "=== /api/v1/chat ==="
curl -sS -X POST -H "Content-Type: application/json" -d '{"query":"hello world"}' http://127.0.0.1:8000/api/v1/chat
echo

echo "=== killing pid=$PID ==="
kill "$PID" 2>/dev/null
sleep 1

echo "=== final log tail ==="
tail -30 /tmp/uvicorn.log
