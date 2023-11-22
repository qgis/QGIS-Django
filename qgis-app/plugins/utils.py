import requests
import re


def extract_version(tag):
    """
    Extracts the major and minor version from a given tag.

    The tag should be in the format of x.y.z where x, y, and z are
    numbers representing major, minor, and patch versions respectively.

    Args:
       tag (str): The version tag to be processed.

    Returns:
       str: The major and minor version as x.y, or None if no match.
    """
    match = re.search(r'(\d+\.\d+\.\d+)', tag)
    if match:
        version = match.group(1)
        version_parts = version.split('.')
        return '.'.join(version_parts[:-1])
    else:
        return None


def get_qgis_versions():
    """
    Fetches all releases from the QGIS GitHub repository and extracts their
    major and minor versions.

    Returns:
        list: A list of unique major and minor versions of the releases.

    Raises:
        Exception: If the request to the GitHub API fails.
    """
    url = 'https://api.github.com/repos/qgis/QGIS/releases'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Request failed')
    releases = response.json()
    all_versions = []
    for release in releases:
        tag_name = release['tag_name'].replace('_', '.')
        version = extract_version(tag_name)
        if version not in all_versions:
            all_versions.append(version)
    return all_versions
