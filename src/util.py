import os
import s3fs
import json
import pandas as pd
from . import constants
from web3 import Web3

INFURA_PROJ_ID = os.environ["WEB3_INFURA_PROJECT_ID"]


def get_polygon_web3():
    polygon_mainnet_endpoint = f"https://polygon-mainnet.infura.io/v3/{INFURA_PROJ_ID}"

    web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))

    assert web3.is_connected()

    return web3


def get_eth_web3():
    ethereum_mainnet_endpoint = f"https://mainnet.infura.io/v3/{INFURA_PROJ_ID}"

    web3_eth = Web3(Web3.HTTPProvider(ethereum_mainnet_endpoint))

    assert web3_eth.is_connected()

    return web3_eth


def load_abi(filename):
    """Load a single ABI from the `abis` folder under `src`"""
    script_dir = os.path.dirname(__file__)
    abi_dir = os.path.join(script_dir, "abis")

    with open(os.path.join(abi_dir, filename), "r") as f:
        abi = json.loads(f.read())

    return abi


def is_production():
    """ Returns the execution environment (dev, staging or main) """
    env = os.getenv("ENV", "Development")
    return env == "Production"


def load_s3_data(name):
    """ Loads json file stored on S3 as a panda dataframe """
    s3 = s3fs.S3FileSystem(endpoint_url=constants.DIGITAL_OCEAN_S3_ENDPOINT)

    if is_production():
        bucket = constants.DIGITAL_OCEAN_S3_PROD_BUCKET
    else:
        bucket = constants.DIGITAL_OCEAN_S3_DEV_BUCKET

    with s3.open(f'{bucket}/lake/{name}.json', 'rb') as f:
        data = json.load(f)
        return pd.DataFrame(data)


def debug(text):
    """ Write text to console if not in production """
    if not is_production():
        print(text)


def getenv(key, default_value):
    """ Reads an environment variable and logs it to console if not in production """
    result = os.getenv(key, default_value)
    debug(f"{key}={result}")
    return result
