# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import task.bank.rpc.callback_pb2 as callback__pb2


class CallbackStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

    Args:
      channel: A grpc.Channel.
    """
        self.DepositCallback = channel.unary_unary(
            "/Callback/DepositCallback",
            request_serializer=callback__pb2.DepositCallbackRequest.SerializeToString,
            response_deserializer=callback__pb2.DepositCallbackResponse.FromString,
        )


class CallbackServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def DepositCallback(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_CallbackServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "DepositCallback": grpc.unary_unary_rpc_method_handler(
            servicer.DepositCallback,
            request_deserializer=callback__pb2.DepositCallbackRequest.FromString,
            response_serializer=callback__pb2.DepositCallbackResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "Callback", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
