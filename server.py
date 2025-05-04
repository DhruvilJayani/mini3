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

PEERS = {
    "Server1": "localhost:50051",
    "Server2": "localhost:50052",
    "Server3": "localhost:50053"
}


class TaskService(task_pb2_grpc.TaskServiceServicer):
    def __init__(self, server_id, port, peers, capacity=100):
        self.server_id = server_id
        self.port = port
        self.peers = peers  # dictionary of {peer_id: "host:port"}
        self.queue = queue.Queue()
        self.capacity = capacity
        self.lock = threading.Lock()
        print(f"[{self.server_id}] Server initialized.")

        # Start the background work stealing thread
        self.last_steal_time = time.time()
        threading.Thread(target=self.run_work_stealer, daemon=True).start()

    def EnqueueTask(self, request, context):
        best_server = self.select_best_server(request.priority)

        if best_server == self.server_id:
            with self.lock:
                if self.queue.qsize() < self.capacity:
                    self.queue.put(request)
                    print(f"[{self.server_id}] Enqueued task {request.id}")
                    return task_pb2.Ack(success=True, info="Enqueued locally")
                else:
                    return task_pb2.Ack(success=False, info="Queue full")
        else:
            try:
                target_addr = self.peers[best_server]
                with grpc.insecure_channel(target_addr) as ch:
                    stub = task_pb2_grpc.TaskServiceStub(ch)
                    forwarded_task = task_pb2.Task(
                        id=request.id,
                        type=request.type,
                        priority=request.priority,
                        hop_count=request.hop_count + 1
                    )
                    return stub.EnqueueTask(forwarded_task)
            except Exception as e:
                print(f"[{self.server_id}] Failed to forward: {e}")
                return task_pb2.Ack(success=False, info="Forwarding failed")

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

    def select_best_server(self, priority):
        best_id = self.server_id
        best_score = self.calculate_score(self.get_local_metrics(), priority, distance=0)

        for peer_id, peer_addr in self.peers.items():
            try:
                with grpc.insecure_channel(peer_addr) as ch:
                    stub = task_pb2_grpc.TaskServiceStub(ch)
                    status = stub.GetStatus(task_pb2.StatusRequest())
                    metrics = {
                        "queue_len": status.queue_len,
                        "cpu": status.cpu_usage,
                        "mem": status.mem_usage
                    }
                    score = self.calculate_score(metrics, priority, distance=1.0)
                    if score > best_score:
                        best_score = score
                        best_id = peer_id
            except Exception:
                continue  # Skip unreachable peers

        return best_id

    def run_work_stealer(self):
        while True:
            time.sleep(5)  # Check every 5 seconds

            with self.lock:
                local_queue_len = self.queue.qsize()

            if local_queue_len > 5:
                continue  # We're not idle

            for peer_id, peer_addr in self.peers.items():
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
                            break  # Only steal from one peer per cycle

                except Exception:
                    continue  # Peer unreachable, try next one



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
