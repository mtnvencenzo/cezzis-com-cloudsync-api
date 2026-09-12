"""Application version helper.

Builds the full version string from package metadata and optional version tag.
Format: "{semVer}+{tag}" (e.g., "1.2.3+abc123def") when APP_VERSION_TAG is set,
otherwise just "{semVer}" (e.g., "1.2.3").
"""

import os
from functools import lru_cache
from importlib.metadata import version


@lru_cache(maxsize=1)
def get_app_version() -> str:
    """Get the full application version string.

    Returns:
        Version string in format "semVer+tag" or "semVer" if no tag is set.
    """
    package_version = version("cezzis_com_cloudsync_api")
    version_tag = os.environ.get("APP_VERSION_TAG", "")
    if version_tag:
        return f"{package_version}+{version_tag}"
    return package_version
