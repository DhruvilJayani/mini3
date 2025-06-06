# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import task_pb2 as task__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in task_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TaskServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.EnqueueTask = channel.unary_unary(
                '/replication.TaskService/EnqueueTask',
                request_serializer=task__pb2.Task.SerializeToString,
                response_deserializer=task__pb2.Ack.FromString,
                _registered_method=True)
        self.StealTasks = channel.unary_unary(
                '/replication.TaskService/StealTasks',
                request_serializer=task__pb2.StealRequest.SerializeToString,
                response_deserializer=task__pb2.TaskList.FromString,
                _registered_method=True)
        self.GetStatus = channel.unary_unary(
                '/replication.TaskService/GetStatus',
                request_serializer=task__pb2.StatusRequest.SerializeToString,
                response_deserializer=task__pb2.Status.FromString,
                _registered_method=True)


class TaskServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def EnqueueTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StealTasks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TaskServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'EnqueueTask': grpc.unary_unary_rpc_method_handler(
                    servicer.EnqueueTask,
                    request_deserializer=task__pb2.Task.FromString,
                    response_serializer=task__pb2.Ack.SerializeToString,
            ),
            'StealTasks': grpc.unary_unary_rpc_method_handler(
                    servicer.StealTasks,
                    request_deserializer=task__pb2.StealRequest.FromString,
                    response_serializer=task__pb2.TaskList.SerializeToString,
            ),
            'GetStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStatus,
                    request_deserializer=task__pb2.StatusRequest.FromString,
                    response_serializer=task__pb2.Status.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'replication.TaskService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('replication.TaskService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TaskService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def EnqueueTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.TaskService/EnqueueTask',
            task__pb2.Task.SerializeToString,
            task__pb2.Ack.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StealTasks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.TaskService/StealTasks',
            task__pb2.StealRequest.SerializeToString,
            task__pb2.TaskList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.TaskService/GetStatus',
            task__pb2.StatusRequest.SerializeToString,
            task__pb2.Status.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
