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


def zip_a_file_if_not_zipfile(filename: str) -> BytesIO:
    """ Zip a file without license """

    if zipfile.is_zipfile(filename):
        in_memory_data = BytesIO(filename)
    else:
        in_memory_data = BytesIO()
        zf = zipfile.ZipFile(in_memory_data, "w")
        fdir, fname = os.path.split(filename)
        zf.write(filename, fname)
        zf.close()
    return in_memory_data
