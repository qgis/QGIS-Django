import io
import os
import shutil
import uuid
import zipfile


def create_license_file(string):
    tmp_dir = f"/tmp/{uuid.uuid4().hex}"
    file = f"{tmp_dir}/license.txt"
    os.mkdir(tmp_dir)
    with open(file, "w") as f:
        f.write(string)
        f.seek(0)
    return file, tmp_dir


def zipped_with_license(file, zip_subdir, custom_license):
    license_file, tmp_dir = create_license_file(custom_license)
    filenames = (file, license_file)
    in_memory_data = io.BytesIO()
    zf = zipfile.ZipFile(in_memory_data, "w")

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    shutil.rmtree(tmp_dir)

    return in_memory_data
