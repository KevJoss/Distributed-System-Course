#!/usr/bin/env python3
import argparse
from rpc import start_server

def add(a:int,b:int)->int: return a+b
def multiply(a:int,b:int)->int: return a*b
def fib(n:int)->int:
    if n<0: raise ValueError("n>=0 required")
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def powi(a:int,b:int)->int:
    if b<0: raise ValueError("b>=0 required")
    res=1
    while b>0:
        if b&1: res*=a
        a*=a; b//=2
    return res

REGISTRY = {"add":add, "multiply":multiply, "fib":fib, "pow":powi}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Python RPC server")
    ap.add_argument("--port", type=int, default=6000)
    args = ap.parse_args()
    start_server(args.port, REGISTRY)
