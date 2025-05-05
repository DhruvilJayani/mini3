import grpc
from concurrent import futures
import time
import threading
import queue
import argparse
import psutil
import random
import generated.task_pb2 as task_pb2
import generated.task_pb2_grpc as task_pb2_grpc

# Define known peers
PEERS = {
    "Server1": "localhost:50051",
    "Server2": "localhost:50052",
    "Server3": "localhost:50053",
    "Server4": "localhost:50054",
    "Server5": "localhost:50055"
}

class TaskService(task_pb2_grpc.TaskServiceServicer):
    def __init__(self, server_id, port, peers, capacity=100):
        self.server_id = server_id
        self.port = port
        self.peers = peers  # Dictionary of peer_id: address
        self.queue = queue.Queue(maxsize=capacity)  # Enforced capacity
        self.capacity = capacity
        self.lock = threading.Lock()
        self.alive_peers_lock = threading.Lock()
        self.alive_peers = set(peers.keys())  # Track reachable peers
        print(f"[{self.server_id}] Server initialized.")

        # Start background threads
        threading.Thread(target=self.run_work_stealer, daemon=True).start()
        threading.Thread(target=self.run_task_worker, daemon=True).start()
        threading.Thread(target=self.run_heartbeat_monitor, daemon=True).start()

    def EnqueueTask(self, request, context):
        try:
            self.queue.put(request, block=False)
            print(f"[{self.server_id}] Enqueued task {request.id} locally")
            return task_pb2.Ack(success=True, info="Enqueued locally")
        except queue.Full:
            print(f"[{self.server_id}] Queue full. Attempting to forward task {request.id}")
            scored_peers = []

            with self.alive_peers_lock:
                for peer_id in self.alive_peers:
                    peer_addr = self.peers[peer_id]
                    try:
                        with grpc.insecure_channel(peer_addr) as ch:
                            stub = task_pb2_grpc.TaskServiceStub(ch)
                            status = stub.GetStatus(task_pb2.StatusRequest())
                            metrics = {
                                "queue_len": status.queue_len,
                                "cpu": status.cpu_usage,
                                "mem": status.mem_usage
                            }
                            score = self.calculate_score(metrics, request.priority)
                            scored_peers.append((score, peer_id, peer_addr))
                    except Exception as e:
                        print(f"[{self.server_id}] Failed to get status from {peer_id}: {e}")

            scored_peers.sort(reverse=True)  # Highest score first

            for _, peer_id, peer_addr in scored_peers:
                try:
                    with grpc.insecure_channel(peer_addr) as ch:
                        stub = task_pb2_grpc.TaskServiceStub(ch)
                        forwarded_task = task_pb2.Task(
                            id=request.id,
                            type=request.type,
                            priority=request.priority,
                            hop_count=request.hop_count + 1
                        )
                        ack = stub.EnqueueTask(forwarded_task)
                        if ack.success:
                            print(f"[{self.server_id}] Forwarded task {request.id} to {peer_id}")
                            return ack
                except Exception as e:
                    print(f"[{self.server_id}] Failed to forward to {peer_id}: {e}")

            print(f"[{self.server_id}] All forward attempts failed for task {request.id}")
            return task_pb2.Ack(success=False, info="Queue full and forwarding failed")

    def StealTasks(self, request, context):
        tasks = []
        with self.lock:
            while not self.queue.empty() and len(tasks) < request.max_tasks:
                tasks.append(self.queue.get())
        print(f"[{self.server_id}] Sent {len(tasks)} stolen tasks.")
        return task_pb2.TaskList(tasks=tasks)

    def GetStatus(self, request, context):
        cpu = psutil.cpu_percent(interval=None) / 100.0
        mem = psutil.virtual_memory().percent / 100.0
        return task_pb2.Status(
            queue_len=self.queue.qsize(),
            cpu_usage=cpu,
            mem_usage=mem
        )

    def get_local_metrics(self):
        return {
            "queue_len": self.queue.qsize(),
            "cpu": psutil.cpu_percent(interval=None) / 100.0,
            "mem": psutil.virtual_memory().percent / 100.0
        }

    def calculate_score(self, metrics, priority, distance=1.0):
        w_q = 0.4
        w_c = 0.2
        w_m = 0.2
        w_d = 0.1
        w_p = 0.1

        available_slots = max(0, self.capacity - metrics["queue_len"])
        return (
            w_q * available_slots +
            w_c * (1.0 - metrics["cpu"]) +
            w_m * (1.0 - metrics["mem"]) -
            w_d * distance +
            w_p * priority
        )

    def run_work_stealer(self):
        while True:
            time.sleep(5)
            with self.lock:
                local_queue_len = self.queue.qsize()

            if local_queue_len > 5:
                continue

            with self.alive_peers_lock:
                for peer_id in self.alive_peers:
                    peer_addr = self.peers[peer_id]
                    try:
                        with grpc.insecure_channel(peer_addr) as ch:
                            stub = task_pb2_grpc.TaskServiceStub(ch)
                            status = stub.GetStatus(task_pb2.StatusRequest())

                            if status.queue_len > 15:
                                steal_req = task_pb2.StealRequest(max_tasks=5)
                                stolen_tasks = stub.StealTasks(steal_req).tasks

                                with self.lock:
                                    for task in stolen_tasks:
                                        self.queue.put(task)

                                print(f"[{self.server_id}] Stole {len(stolen_tasks)} tasks from {peer_id}")
                                break
                    except Exception:
                        continue

    def run_task_worker(self):
        while True:
            task = self.queue.get()
            print(f"[{self.server_id}] Processing task {task.id} (priority: {task.priority})")
            time.sleep(random.uniform(0.2, 1.0))  # Simulate task work
            print(f"[{self.server_id}] Finished task {task.id}")
            self.queue.task_done()

    def run_heartbeat_monitor(self):
        while True:
            time.sleep(3)
            alive = set()
            for peer_id, peer_addr in self.peers.items():
                try:
                    with grpc.insecure_channel(peer_addr) as ch:
                        stub = task_pb2_grpc.TaskServiceStub(ch)
                        _ = stub.GetStatus(task_pb2.StatusRequest())
                        alive.add(peer_id)
                except:
                    print(f"[{self.server_id}] Peer {peer_id} is unreachable.")
            with self.alive_peers_lock:
                self.alive_peers = alive


def serve(port, server_id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_pb2_grpc.add_TaskServiceServicer_to_server(
        TaskService(server_id, port, {k: v for k, v in PEERS.items() if k != server_id}),
        server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[{server_id}] Server started on port {port}.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"[{server_id}] Shutting down.")
        server.stop(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--id", required=True, type=str)
    args = parser.parse_args()
    serve(args.port, args.id)
