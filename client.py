import grpc
import time
import random
import uuid
import generated.task_pb2 as task_pb2
import generated.task_pb2_grpc as task_pb2_grpc

# List of server addresses you want to send tasks to
# SERVER_ADDRESSES = [
#     "localhost:50051",
#     "localhost:50052",
#     "localhost:50053"
# ]

PEERS = {
    "Server1": "192.168.1.10:50051",  # Machine A
    "Server2": "192.168.1.10:50052",  # Machine A
    "Server3": "192.168.1.10:50053",  # Machine A
    "Server4": "192.168.1.20:50051",  # Machine B
    "Server5": "192.168.1.20:50052",  # Machine B
}

def send_task(server_address, task):
    with grpc.insecure_channel(server_address) as channel:
        stub = task_pb2_grpc.TaskServiceStub(channel)
        response = stub.EnqueueTask(task)
        print(f"[Client] Sent task {task.id} to {server_address} | Response: {response.info}")

def run_task_sender(num_tasks=10, delay=0.5):
    for i in range(num_tasks):
        task = task_pb2.Task(
            id=str(uuid.uuid4()),
            type="compute",
            priority=random.randint(0, 2),
            hop_count=0
        )
        server = random.choice(SERVER_ADDRESSES)
        send_task(server, task)
        time.sleep(delay)

if __name__ == "__main__":
    run_task_sender(num_tasks=20, delay=0.3)
