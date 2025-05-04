#!/bin/bash

# Launch 3 servers on ports 50051–50053
# You can increase this number or spread to other machines

python server.py --port=50051 --id=Server1 &
sleep 0.5
python server.py --port=50052 --id=Server2 &
sleep 0.5
python server.py --port=50053 --id=Server3 &
sleep 0.5

echo "🚀 All servers started."
