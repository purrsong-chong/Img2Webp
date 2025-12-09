from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Union

from PIL import Image


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_supported_image(path: Union[str, Path]) -> bool:
    """지원하는 확장자인지 여부만 빠르게 체크."""
    p = Path(path)
    return p.suffix.lower() in SUPPORTED_EXTENSIONS


def convert_to_webp(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    quality: int = 80,
) -> Path:
    """
    단일 파일을 WebP로 변환한다.

    - input_path: PNG / JPG / JPEG 파일 경로
    - output_path: 지정하지 않으면 input_path와 동일한 디렉토리에 확장자만 .webp로 변경
    - quality: WebP 품질 (0~100)
    """
    src = Path(input_path)
    if not src.is_file():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {src}")

    if not is_supported_image(src):
        raise ValueError(f"지원하지 않는 이미지 포맷입니다: {src.suffix}")

    if output_path is None:
        dst = src.with_suffix(".webp")
    else:
        dst = Path(output_path)

    dst.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as im:
        # 원본 이미지의 DPI 정보 보존 (convert 전에 저장)
        dpi = im.info.get("dpi")
        
        # 투명도가 있는 이미지는 RGBA로 유지/변환
        if im.mode in ("RGBA", "LA", "PA"):
            # 이미 RGBA 모드이거나 알파 채널이 있는 모드
            im = im.convert("RGBA")
        elif im.mode == "P":
            # 팔레트 모드: 투명도가 있는지 확인
            if "transparency" in im.info:
                im = im.convert("RGBA")
            else:
                im = im.convert("RGB")
        else:
            # 그 외 모드는 RGB로 변환
            im = im.convert("RGB")
        
        # DPI 정보가 있으면 저장 시 포함
        save_kwargs = {"quality": quality}
        if dpi:
            save_kwargs["dpi"] = dpi
        
        im.save(dst, "WEBP", **save_kwargs)

    return dst


def batch_convert_to_webp(
    inputs: Iterable[Union[str, Path]],
    quality: int = 80,
) -> List[Path]:
    """
    여러 파일을 한꺼번에 WebP로 변환한다.
    지원하지 않는 확장자는 조용히 건너뛴다.
    """
    results: List[Path] = []
    for path in inputs:
        if not is_supported_image(path):
            continue
        converted = convert_to_webp(path, quality=quality)
        results.append(converted)
    return results


