import requests
import re
from django.http import HttpRequest


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


def parse_remote_addr(request: HttpRequest) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.headers.get("X-Forwarded-For", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR", "")

def get_version_from_label(param):
    """
    Fetches the QGIS version based on the given parameter.

    Args:
        param (str): The parameter to determine which version to fetch.
                     Accepts 'ltr', 'stable', or 'latest'.

    Returns:
        str: The major and minor version of QGIS.

    Raises:
        ValueError: If the parameter value is invalid.
        Exception: If the request to the QGIS version service fails or the version is not found.
    """
    if param.lower() in ['ltr', 'stable']:
        url = 'https://version.qgis.org/version-ltr.txt'
    elif param.lower() == 'latest':
        url = 'https://version.qgis.org/version.txt'
    else:
        raise ValueError('Invalid parameter value')

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Request failed')

    content = response.text
    match = re.search(r'QGIS Version \d+\|Visit .+ version (\d+\.\d+)', content)
    if match:
        return match.group(1)
    else:
        raise Exception('Version not found in response')