import grpc
import time
import random
import uuid
import generated.task_pb2 as task_pb2
import generated.task_pb2_grpc as task_pb2_grpc

# List of server addresses you want to send tasks to
SERVER_ADDRESSES = [
    "localhost:50051",
    "localhost:50052",
    "localhost:50053"
]

def send_task_with_retry(task, max_retries=3):
    tried = set()
    for _ in range(max_retries):
        remaining = [addr for addr in SERVER_ADDRESSES if addr not in tried]
        if not remaining:
            print(f"[Client] Task {task.id} failed to send after retries.")
            return

        server_address = random.choice(remaining)
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
    for i in range(num_tasks):
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
