# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: callback.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='callback.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0e\x63\x61llback.proto\"}\n\x16\x44\x65positCallbackRequest\x12*\n\x04\x62ody\x18\x01 \x01(\x0b\x32\x1c.DepositCallbackRequest.Body\x1a\x37\n\x04\x42ody\x12\x17\n\x0fvirtual_account\x18\x01 \x01(\t\x12\x16\n\x0epayment_amount\x18\x02 \x01(\t\")\n\x17\x44\x65positCallbackResponse\x12\x0e\n\x06status\x18\x01 \x01(\t2R\n\x08\x43\x61llback\x12\x46\n\x0f\x44\x65positCallback\x12\x17.DepositCallbackRequest\x1a\x18.DepositCallbackResponse\"\x00\x62\x06proto3')
)




_DEPOSITCALLBACKREQUEST_BODY = _descriptor.Descriptor(
  name='Body',
  full_name='DepositCallbackRequest.Body',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='virtual_account', full_name='DepositCallbackRequest.Body.virtual_account', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payment_amount', full_name='DepositCallbackRequest.Body.payment_amount', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=88,
  serialized_end=143,
)

_DEPOSITCALLBACKREQUEST = _descriptor.Descriptor(
  name='DepositCallbackRequest',
  full_name='DepositCallbackRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='body', full_name='DepositCallbackRequest.body', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_DEPOSITCALLBACKREQUEST_BODY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=143,
)


_DEPOSITCALLBACKRESPONSE = _descriptor.Descriptor(
  name='DepositCallbackResponse',
  full_name='DepositCallbackResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='DepositCallbackResponse.status', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=145,
  serialized_end=186,
)

_DEPOSITCALLBACKREQUEST_BODY.containing_type = _DEPOSITCALLBACKREQUEST
_DEPOSITCALLBACKREQUEST.fields_by_name['body'].message_type = _DEPOSITCALLBACKREQUEST_BODY
DESCRIPTOR.message_types_by_name['DepositCallbackRequest'] = _DEPOSITCALLBACKREQUEST
DESCRIPTOR.message_types_by_name['DepositCallbackResponse'] = _DEPOSITCALLBACKRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DepositCallbackRequest = _reflection.GeneratedProtocolMessageType('DepositCallbackRequest', (_message.Message,), dict(

  Body = _reflection.GeneratedProtocolMessageType('Body', (_message.Message,), dict(
    DESCRIPTOR = _DEPOSITCALLBACKREQUEST_BODY,
    __module__ = 'callback_pb2'
    # @@protoc_insertion_point(class_scope:DepositCallbackRequest.Body)
    ))
  ,
  DESCRIPTOR = _DEPOSITCALLBACKREQUEST,
  __module__ = 'callback_pb2'
  # @@protoc_insertion_point(class_scope:DepositCallbackRequest)
  ))
_sym_db.RegisterMessage(DepositCallbackRequest)
_sym_db.RegisterMessage(DepositCallbackRequest.Body)

DepositCallbackResponse = _reflection.GeneratedProtocolMessageType('DepositCallbackResponse', (_message.Message,), dict(
  DESCRIPTOR = _DEPOSITCALLBACKRESPONSE,
  __module__ = 'callback_pb2'
  # @@protoc_insertion_point(class_scope:DepositCallbackResponse)
  ))
_sym_db.RegisterMessage(DepositCallbackResponse)



_CALLBACK = _descriptor.ServiceDescriptor(
  name='Callback',
  full_name='Callback',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=188,
  serialized_end=270,
  methods=[
  _descriptor.MethodDescriptor(
    name='DepositCallback',
    full_name='Callback.DepositCallback',
    index=0,
    containing_service=None,
    input_type=_DEPOSITCALLBACKREQUEST,
    output_type=_DEPOSITCALLBACKRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_CALLBACK)

DESCRIPTOR.services_by_name['Callback'] = _CALLBACK

# @@protoc_insertion_point(module_scope)
