import os
import zipfile

from io import BytesIO

LICENSE_FILE = os.path.join(os.path.dirname(__file__), "license.txt")


def zipped_with_license(file: str, zip_subdir: str) -> BytesIO:
    filenames = (file, LICENSE_FILE)
    in_memory_data = BytesIO()
    zf = zipfile.ZipFile(in_memory_data, "w")

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    return in_memory_data