from pathlib import Path

import pytest
from PIL import Image

from converter.core import SUPPORTED_EXTENSIONS, batch_convert_to_webp, convert_to_webp, is_supported_image


def _create_dummy_image(path: Path, size=(32, 32), color=(255, 0, 0)):
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", size, color)
    im.save(path)
    return path


def test_is_supported_image_true_for_supported_suffixes(tmp_path: Path):
    for ext in SUPPORTED_EXTENSIONS:
        p = tmp_path / f"test{ext}"
        p.write_bytes(b"dummy")
        assert is_supported_image(p)


def test_is_supported_image_false_for_unsupported_suffix(tmp_path: Path):
    p = tmp_path / "test.gif"
    p.write_bytes(b"dummy")
    assert not is_supported_image(p)


def test_convert_to_webp_creates_file_with_webp_extension(tmp_path: Path):
    src = tmp_path / "sample.jpg"
    _create_dummy_image(src)

    dst = convert_to_webp(src)

    assert dst.exists()
    assert dst.suffix == ".webp"


def test_convert_to_webp_raises_for_unsupported_extension(tmp_path: Path):
    src = tmp_path / "sample.gif"
    src.write_bytes(b"not an image")

    with pytest.raises(ValueError):
        convert_to_webp(src)


def test_convert_to_webp_raises_for_missing_file(tmp_path: Path):
    src = tmp_path / "missing.jpg"
    with pytest.raises(FileNotFoundError):
        convert_to_webp(src)


def test_batch_convert_to_webp_skips_unsupported_and_converts_supported(tmp_path: Path):
    img1 = _create_dummy_image(tmp_path / "a.jpg")
    img2 = _create_dummy_image(tmp_path / "b.png")
    unsupported = tmp_path / "c.gif"
    unsupported.write_bytes(b"dummy")

    outputs = batch_convert_to_webp([img1, img2, unsupported])

    assert len(outputs) == 2
    for out in outputs:
        assert out.exists()
        assert out.suffix == ".webp"


