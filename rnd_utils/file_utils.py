import base64
import hashlib
import tempfile
import requests


def save_tempfile(file_bytes: bytes, extension: str = ".temp") -> str:
    """Saves temporary file and returns filename for further processing

    If using this for GIV related operations:
    - image files use `.jpg` format
    - video files use `.mp4` format

    Args:
        file_bytes (bytes): The content of the file to write in bytes
        extension (str, optional): `.jpg` for image, `.mp4` for video. Defaults to ".temp".

    Returns:
        str: Filepath to written temporary file
    """
    with tempfile.NamedTemporaryFile(mode="wb", suffix=extension, delete=False) as f:
        f.write(file_bytes)
        return f.name


def save_from_url(url: str, extension: str = ".temp") -> str:
    """Saves temporary file and returns filename for further processing

    If using this for GIV related operations:
    - image files use `.jpg` format
    - video files use `.mp4` format

    Args:
        file_bytes (bytes): The content of the file to write in bytes
        extension (str, optional): `.jpg` for image, `.mp4` for video. Defaults to ".temp".

    Returns:
        str: Filepath to written temporary file
    """

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download the file from the URL.")

    return save_tempfile(file_bytes=response.content, extension=extension)


def hash_bytes_to_md5(byte_obj: bytes):
    return base64.urlsafe_b64encode(hashlib.md5(byte_obj).digest()).decode()


def encode_filebytes_as_b64(filepath: str, extension: str = ""):
    with open(filepath, "rb") as temp:
        md5_hash = hash_bytes_to_md5(temp.read())

    if md5_hash and extension:
        return md5_hash + extension

    return md5_hash
