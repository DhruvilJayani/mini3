#!/bin/bash

echo "🛑 Killing any existing server processes on ports 50051–50055..."

for port in 50051 50052 50053 50054 50055; do
  lsof -ti tcp:$port | xargs -r kill -9
done

sleep 2

echo "🚀 Starting servers..."
python server.py --port=50051 --id=Server1 &
sleep 0.5
python server.py --port=50052 --id=Server2 &
sleep 0.5
python server.py --port=50053 --id=Server3 &
sleep 0.5
python server.py --port=50054 --id=Server4 &
sleep 0.5
python server.py --port=50055 --id=Server5 &
sleep 0.5

echo "✅ All 5 servers started with clean queues."
