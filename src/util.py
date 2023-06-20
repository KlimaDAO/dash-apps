import os
import io
import base64
import pandas as pd
from datetime import datetime
from prefect.results import PersistedResultBlob
from prefect_aws.s3 import S3Bucket
from prefect.filesystems import LocalFileSystem
from prefect.serializers import Serializer
from typing_extensions import Literal


def is_production() -> bool:
    """ Indicates if we are on a production environment """
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


class Perf():
    """
    Helper Class to make performance tests
    """
    def __init__(self):
        self.start = datetime.now()
        self.prev = None

    def tag(self, tag):
        ts = datetime.now() - self.start
        tp = datetime.now() - self.prev if self.prev else ""
        with open("perf.txt", "a") as f:
            f.write(f"{ts} {tp} {tag}\n")
        self.prev = datetime.now()


def load_s3_data(slug: str) -> pd.DataFrame:
    """ Loads json file stored on a prefect block as a panda dataframe """
    local_storage_base_path = getenv("DASH_USE_LOCAL_STORAGE")
    if local_storage_base_path:
        block_name = "local"
        block = LocalFileSystem(basepath=local_storage_base_path)
    else:
        block_name = "prod" if is_production() else "dev"
        try:
            block = S3Bucket.load(block_name)
        except Exception as e:
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
