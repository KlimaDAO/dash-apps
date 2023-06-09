import os
import io
import base64
import json
import pandas as pd
from prefect.results import PersistedResultBlob
from prefect_aws.s3 import S3Bucket
from prefect.filesystems import LocalFileSystem
from web3 import Web3
from prefect.serializers import Serializer
from typing_extensions import Literal

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


def is_production() -> bool:
    """ Returns the execution environment (dev, staging or main) """
    env = os.getenv("ENV", "Development")
    return env == "Production"


class DfSerializer(Serializer):
    """
    Serializes Dataframes using feather.
    """
    type: Literal["pandas_feather"] = "pandas_feather"

    def dumps(self, df: pd.DataFrame) -> bytes:
        bytestream = io.BytesIO()
        df.to_feather(bytestream)
        bytestream.seek(0)
        return base64.encodebytes(bytestream.read())

    def loads(self, blob: bytes) -> pd.DataFrame:
        bytestream = io.BytesIO(base64.decodebytes(blob))
        return pd.read_feather(bytestream)


def load_s3_data(slug: str) -> pd.DataFrame:
    """ Loads json file stored on a prefect block as a panda dataframe """
    local_storage_base_path = getenv("DASH_USE_LOCAL_STORAGE")
    if local_storage_base_path:
        block_name = "local"
        block = LocalFileSystem(basepath=local_storage_base_path)
    else:
        block_name = "prod" if is_production() else "dev"
        try:
            debug('2')
            block = S3Bucket.load(block_name)
            debug('3')
        except Exception as e:
            debug('1')
            debug(f"Prefect Error when loading block {block_name}: {str(e)}")
            raise e
    filename = f"{slug}-latest"
    try:
        file_data = block.read_path(filename)
        blob = PersistedResultBlob.parse_raw(file_data).data
        res = DfSerializer().loads(blob)
        return res
    except Exception as e:
        debug(f"Prefect Error when reading {block_name}/{filename}: {str(e)}")
        raise e


def debug(text: str):
    """ Write text to console if not in production """
    if not is_production():
        print(text, flush=True)


def getenv(key: str, default_value=None) -> str:
    """ Reads an environment variable and logs it to console if not in production """
    result = os.getenv(key, default_value)
    debug(f"Env: {key}={result}")
    return result
