import sys
import time
from itertools import count
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads" / "gunnerkriggcourt"

if not DOWNLOAD_DIR.exists():
    DOWNLOAD_DIR.mkdir(parents=True)


def download_imagefile(url=None, filepath=None):
    if url is None or filepath is None:
        raise ValueError("filepath and url required")
    response = requests.get(url=url)
    if response.status_code == 200:
        with open(filepath, "wb") as fp:
            fp.write(response.content)
        return True
    elif response.status_code == 404:
        return False
    else:
        raise IOError("unable to download or save file")


def gunnerkrigg_dl(imgnum):
    filename = "{:08d}.jpg".format(imgnum)  # filename
    filepath = DOWNLOAD_DIR / filename

    if filepath.exists():
        print(f"{filename} Already present on disk. skipping download")
        return True
    else:
        url = f"https://www.gunnerkrigg.com/comics/{filename}"
        print(f"Downloading {imgnum }")
        print(f"FROM:\n{url}\nTo:\n{filepath}\n")
        downloaded = download_imagefile(url=url, filepath=filepath)
        print(f"STATUS:\t{downloaded}\n")
        if downloaded:
            return True
    return False


def download_all_images():
    for num in count(1):
        reply = gunnerkrigg_dl(num)
        if not reply:
            sys.exit()
        print("waiting one second")
        time.sleep(1)
