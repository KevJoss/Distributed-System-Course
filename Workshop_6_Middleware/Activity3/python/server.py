#!/usr/bin/env python3
import argparse, statistics
from rpc_json import start_server

def add(a:int,b:int)->int: return a+b
def multiply(a:int,b:int)->int: return a*b

def sum_list(nums:list[int])->int:
    return int(sum(int(x) for x in nums))

def stats(nums:list[int])->dict:
    if not nums: return {"count":0,"sum":0,"mean":0}
    nums = [int(x) for x in nums]
    return {"count":len(nums), "sum":sum(nums), "mean": sum(nums)/len(nums)}

def echo(obj): return obj

METHODS = {
    "add": add,
    "multiply": multiply,
    "sum_list": sum_list,
    "stats": stats,
    "echo": echo,
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Python JSON-RPC server (Activity 3)")
    ap.add_argument("--port", type=int, default=7000)
    ap.add_argument("--registry-host", default=None)
    ap.add_argument("--registry-port", type=int, default=7001)
    ap.add_argument("--name", default="calc_service")
    args = ap.parse_args()

    registry = None
    if args.registry_host:
        registry = (args.registry_host, args.registry_port)

    start_server(args.port, registry=registry, name=args.name, methods=METHODS)
