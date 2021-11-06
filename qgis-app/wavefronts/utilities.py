import io
import os.path
from zipfile import ZipFile, ZIP_DEFLATED

from base.license import LICENSE_FILE


def zipped_all_with_license(folder_path: str, zip_subdir: str) -> io.BytesIO:
    """Zip all wavefront files with license."""
    if not os.path.isdir(folder_path):
        return None

    in_memory_data = io.BytesIO()
    filelist = os.listdir(folder_path)
    filelist.append(LICENSE_FILE)
    with ZipFile(in_memory_data, "w", ZIP_DEFLATED) as zf:
        for file in filelist:
            if file.endswith('.dummy'):
                continue
            file_path, filename = os.path.split(file)
            zf.write(
                os.path.join(folder_path, file),
                os.path.join(zip_subdir, filename)
            )
    return in_memory_data
