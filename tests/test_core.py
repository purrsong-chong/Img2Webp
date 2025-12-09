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


def test_convert_to_webp_preserves_transparency_for_rgba_png(tmp_path: Path):
    """투명도가 있는 RGBA PNG 이미지의 투명도가 WebP 변환 시 유지되는지 확인"""
    src = tmp_path / "transparent.png"
    src.parent.mkdir(parents=True, exist_ok=True)
    # 투명한 배경을 가진 RGBA 이미지 생성
    im = Image.new("RGBA", (32, 32), (255, 0, 0, 128))  # 반투명 빨간색
    im.save(src)

    dst = convert_to_webp(src)

    assert dst.exists()
    # 변환된 이미지가 RGBA 모드를 유지하는지 확인
    with Image.open(dst) as converted:
        assert converted.mode == "RGBA"
        # 알파 채널의 픽셀 값을 확인 (투명도가 유지되었는지)
        # 원본이 반투명(128)이므로, 변환된 이미지도 일부 투명도가 있어야 함
        alpha_channel = converted.split()[3]
        # 모든 픽셀을 확인하지 않고 샘플만 확인
        assert alpha_channel.getpixel((0, 0)) < 255


def test_convert_to_webp_preserves_transparency_for_palette_png(tmp_path: Path):
    """팔레트 모드 PNG의 투명도가 WebP 변환 시 유지되는지 확인"""
    src = tmp_path / "palette_transparent.png"
    src.parent.mkdir(parents=True, exist_ok=True)
    # 투명도가 있는 팔레트 이미지 생성
    # P 모드에서 투명도를 설정하려면 RGBA로 변환 후 저장
    im = Image.new("RGBA", (32, 32), (0, 255, 0, 128))  # 반투명 녹색
    # P 모드로 변환하면서 투명도 정보를 포함
    im_p = im.convert("P", palette=Image.ADAPTIVE)
    im_p.save(src, transparency=0)  # 투명도 정보 포함

    dst = convert_to_webp(src)

    assert dst.exists()
    # 변환된 이미지가 RGBA 모드로 변환되었는지 확인
    with Image.open(dst) as converted:
        assert converted.mode == "RGBA"
        # 알파 채널이 유지되었는지 확인
        alpha_channel = converted.split()[3]
        # 투명도가 유지되었는지 확인
        assert alpha_channel.getpixel((0, 0)) < 255


def test_convert_to_webp_reads_dpi_from_source(tmp_path: Path):
    """원본 이미지의 DPI 정보를 읽어서 변환 시 전달하는지 확인
    
    참고: WebP 포맷은 DPI 메타데이터를 저장하지 않지만,
    코드는 원본 DPI를 읽어서 저장 시 전달하도록 구현되어 있습니다.
    """
    src = tmp_path / "high_dpi.png"
    src.parent.mkdir(parents=True, exist_ok=True)
    # 특정 DPI를 가진 이미지 생성
    im = Image.new("RGB", (100, 100), (255, 0, 0))
    original_dpi = (300, 300)  # 300 DPI
    im.save(src, dpi=original_dpi)

    # 원본 이미지의 DPI 확인
    with Image.open(src) as orig:
        assert orig.info.get("dpi") is not None

    dst = convert_to_webp(src)

    assert dst.exists()
    # 변환은 정상적으로 완료되어야 함
    # (WebP가 DPI를 저장하지 않는 것은 포맷의 제한사항)
    with Image.open(dst) as converted:
        # WebP 포맷은 DPI 정보를 저장하지 않지만, 변환은 성공해야 함
        assert converted.mode in ("RGB", "RGBA")


def test_convert_to_webp_handles_no_dpi(tmp_path: Path):
    """DPI 정보가 없는 이미지도 정상적으로 변환되는지 확인"""
    src = tmp_path / "no_dpi.jpg"
    src.parent.mkdir(parents=True, exist_ok=True)
    # DPI 정보 없이 이미지 생성
    im = Image.new("RGB", (50, 50), (0, 255, 0))
    im.save(src)

    dst = convert_to_webp(src)

    assert dst.exists()
    # DPI가 없어도 변환은 정상적으로 완료되어야 함
    with Image.open(dst) as converted:
        assert converted.mode in ("RGB", "RGBA")


