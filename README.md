# Mini 3 – Adaptive NWR Replication System (gRPC, Python)

This project implements an adaptive, distributed NWR (Network-Write-Read) task replication system using Python and gRPC. The system features dynamic load balancing, task forwarding based on scoring, and automatic work stealing across multiple servers — even across multiple machines.

---

## 🚀 Features

- Dynamic task routing using real-time CPU, memory, and queue size
- Smart scoring algorithm for replication/load balancing
- Automatic work stealing between idle and busy servers
- gRPC-based, modular architecture (Python)
- Multi-machine, multi-server ready

---

## 🧰 Requirements

- Python 3.8+
- pip packages:
  - grpcio
  - grpcio-tools
  - psutil

Install them with:

```bash
pip install grpcio grpcio-tools psutil

Project Structure
adaptive_nwr/
├── protos/                  # .proto file
│   └── task.proto
├── generated/               # Generated gRPC Python files
│   ├── task_pb2.py
│   ├── task_pb2_grpc.py
│   └── __init__.py
├── server.py                # gRPC server logic
├── client.py                # Task sender (load injector)
├── run_servers.sh           # Script to launch multiple servers
├── requirements.txt
└── README.md
```

Steps to Set up

git clone https://github.com/yourusername/mini3.git

cd mini3

python -m venv venv

source venv/bin/activate

pip install grpcio grpcio-tools psutil

python -m grpc_tools.protoc -I./protos --python_out=./generated --grpc_python_out=./generated ./protos/task.proto

touch generated/__init__.py


Run Command 

./run_servers.sh

python client.py

