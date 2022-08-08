import os

import json
from web3 import Web3

INFURA_PROJ_ID = os.environ["WEB3_INFURA_PROJECT_ID"]


def get_polygon_web3():
    polygon_mainnet_endpoint = f"https://polygon-mainnet.infura.io/v3/{INFURA_PROJ_ID}"

    web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))

    assert web3.isConnected()

    return web3


def get_eth_web3():
    ethereum_mainnet_endpoint = f"https://mainnet.infura.io/v3/{INFURA_PROJ_ID}"

    web3_eth = Web3(Web3.HTTPProvider(ethereum_mainnet_endpoint))

    assert web3_eth.isConnected()

    return web3_eth


def load_abi(filename):
    """Load a single ABI from the `abis` folder under `src`"""
    script_dir = os.path.dirname(__file__)
    abi_dir = os.path.join(script_dir, "abis")

    with open(os.path.join(abi_dir, filename), "r") as f:
        abi = json.loads(f.read())

    return abi
