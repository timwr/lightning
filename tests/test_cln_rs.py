import os
import subprocess
from pathlib import Path

import grpc
import node_pb2 as nodepb
import pytest
from fixtures import TEST_NETWORK
from fixtures import *  # noqa: F401,F403
from node_pb2_grpc import NodeStub
from pyln.testing.utils import env

# Skip the entire module if we don't have Rust.
pytestmark = pytest.mark.skipif(
    env('RUST') != '1',
    reason='RUST is not enabled, skipping rust-dependent tests'
)

os.environ["RUST_LOG"] = "trace"


def test_rpc_client(node_factory):
    l1 = node_factory.get_node()
    bin_path = Path.cwd() / "target" / "debug" / "examples" / "cln-rpc-getinfo"
    rpc_path = Path(l1.daemon.lightning_dir) / TEST_NETWORK / "lightning-rpc"
    out = subprocess.check_output([bin_path, rpc_path], stderr=subprocess.STDOUT)
    assert(b'0266e4598d1d3c415f572a8488830b60f7e744ed9235eb0b1ba93283b315c03518' in out)


def test_grpc_connect(node_factory):
    """Attempts to connect to the grpc interface and call getinfo"""
    bin_path = Path.cwd() / "target" / "debug" / "grpc-plugin"
    node_factory.get_node(options={"plugin": str(bin_path)})
    channel = grpc.insecure_channel("localhost:50051")
    stub = NodeStub(channel)

    response = stub.Getinfo(nodepb.GetinfoRequest())
    print(response)

    response = stub.ListFunds(nodepb.ListfundsRequest())
    print(response)
