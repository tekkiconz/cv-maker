"""Root conftest.py — fixes *.test.py import under --import-mode=importlib.

Patches pytest's compute_module_name so that file stems containing dots
(e.g. profile_service.test.py) are mangled to use underscores
(profile_service_test) instead of being left as dotted names that pytest
then misinterprets as package paths.
"""

from pathlib import Path

import _pytest.pathlib as _pathlib


def _patched_compute_module_name(root: Path, module_path: Path) -> str | None:
    result = _orig_compute_module_name(root, module_path)
    if result is None:
        return None
    # If the last component of the dotted module name itself contains dots
    # (e.g. "profile_service.test" from profile_service.test.py), replace
    # those inner dots with underscores so the name is a valid identifier
    # and pytest doesn't try to treat profile_service as a package.
    parts = result.split(".")
    if "." in parts[-1]:
        parts[-1] = parts[-1].replace(".", "_")
    return ".".join(parts)


_orig_compute_module_name = _pathlib.compute_module_name
_pathlib.compute_module_name = _patched_compute_module_name  # type: ignore[assignment]
