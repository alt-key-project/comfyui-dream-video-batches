# -*- coding: utf-8 -*-
def _get_node_name(cls):
    return cls.__dict__.get("NODE_NAME", str(cls))

def raise_error(message: str):
    msg = "Failure:" + message
    print(msg)
    raise Exception(msg)

def on_node_error(node_cls: type, message: str):
    msg = "Failure in [" + _get_node_name(node_cls) + "]:" + message
    print(msg)
    raise Exception(msg)
