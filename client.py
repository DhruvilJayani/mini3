import grpc
import time
import random
import uuid
import threading
import generated.task_pb2 as task_pb2
import generated.task_pb2_grpc as task_pb2_grpc

# List of server addresses you want to send tasks to
SERVER_ADDRESSES = [
    "localhost:50051",
    "localhost:50052",
    "localhost:50053",
    "localhost:50054",
    "localhost:50055"
]

# Shared set of alive servers (updated by heartbeat thread)
alive_servers_lock = threading.Lock()
alive_servers = set(SERVER_ADDRESSES)

def heartbeat_monitor(interval=3):
    global alive_servers
    while True:
        alive = set()
        for server_address in SERVER_ADDRESSES:
            try:
                with grpc.insecure_channel(server_address) as channel:
                    stub = task_pb2_grpc.TaskServiceStub(channel)
                    _ = stub.GetStatus(task_pb2.StatusRequest(), timeout=1)
                    alive.add(server_address)
            except grpc.RpcError:
                print(f"[Heartbeat] {server_address} is unreachable.")
        with alive_servers_lock:
            alive_servers = alive
        time.sleep(interval)

def send_task_with_retry(task, max_retries=3):
    tried = set()
    for _ in range(max_retries):
        with alive_servers_lock:
            available = [addr for addr in alive_servers if addr not in tried]

        if not available:
            print(f"[Client] Task {task.id} failed to send: no alive servers available.")
            return

        server_address = random.choice(available)
        tried.add(server_address)

        try:
            with grpc.insecure_channel(server_address) as channel:
                stub = task_pb2_grpc.TaskServiceStub(channel)
                response = stub.EnqueueTask(task)
                print(f"[Client] Sent task {task.id} to {server_address} | Response: {response.info}")
                return
        except grpc.RpcError as e:
            print(f"[Client] Failed to send task {task.id} to {server_address}: {e.code().name}")

    print(f"[Client] All retries failed for task {task.id}.")

def run_task_sender(num_tasks=10, delay=0.5):
    # Start heartbeat monitor thread
    threading.Thread(target=heartbeat_monitor, daemon=True).start()

    for _ in range(num_tasks):
        task = task_pb2.Task(
            id=str(uuid.uuid4()),
            type="compute",
            priority=random.randint(0, 2),
            hop_count=0
        )
        send_task_with_retry(task)
        time.sleep(delay)

if __name__ == "__main__":
    run_task_sender(num_tasks=200, delay=0.2)
