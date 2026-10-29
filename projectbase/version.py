"""Exact Project Base 0.8.4.2 inputs required"""

from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

from .ips import apply_ips
from .difficulty import apply_difficulty

APWORLD_VERSION = "1.0.0"

ARCHIVE_SHA256 = "4cdd024d7f65d94969417337ac78ab595250653d3d1cad236e76240aad14a293"
PATCH_SHA256 = "71e03d4e8202c368a42de174d498658c035838823fbc6955c1b912b983bfdae7"
VANILLA_SHA256 = "12b77c4bc9c1832cee8881244659065ee1d84c70c3d29e6eaf92e6798cc2ca72"
PROJECT_BASE_SHA256 = "98e42d15792724e712c1519852b6a0c79020da91a1e42d36335a4b24df2ea0b4"
PROJECT_BASE_MD5 = "991fdb0079dad19ff589908cae88eb99"


def build_base_rom(
    vanilla_rom: bytes, project_base_zip: bytes, *, difficulty: str | None = None
) -> bytes:
    """validate the pinned base, optionally apply difficulty"""
    if sha256(vanilla_rom).hexdigest() != VANILLA_SHA256:
        raise ValueError("Expected the unheadered Super Metroid (JU) base ROM")
    if sha256(project_base_zip).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Expected project_base_0.8.4.2.zip with the pinned SHA256")
    with ZipFile(BytesIO(project_base_zip)) as archive:
        patch = archive.read("project_base_0.8.4.2.ips")
    if sha256(patch).hexdigest() != PATCH_SHA256:
        raise ValueError("Project Base IPS checksum mismatch")
    result = apply_ips(vanilla_rom, patch)
    if sha256(result).hexdigest() != PROJECT_BASE_SHA256:
        raise ValueError("Project Base patched ROM checksum mismatch")
    return apply_difficulty(result, difficulty) if difficulty is not None else result
