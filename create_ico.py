"""
Windows용 아이콘 파일(.ico) 생성 스크립트
기존 PNG 아이콘을 사용하여 .ico 파일을 생성합니다.
"""
from pathlib import Path
from PIL import Image

def create_ico_from_png():
    """icon.iconset의 PNG 파일들을 사용하여 .ico 파일 생성"""
    iconset_dir = Path("icon.iconset")
    output_file = Path("Img2WebP.ico")
    
    if not iconset_dir.exists():
        print(f"오류: {iconset_dir} 디렉토리를 찾을 수 없습니다.")
        return False
    
    # .ico 파일에 포함할 크기들 (Windows에서 일반적으로 사용)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # 1x 버전 먼저 시도
        png_file = iconset_dir / f"icon_{size}x{size}.png"
        if not png_file.exists():
            # 2x 버전이 있으면 그것을 사용 (크기 조정)
            png_file_2x = iconset_dir / f"icon_{size}x{size}@2x.png"
            if png_file_2x.exists():
                img = Image.open(png_file_2x)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                images.append(img)
                continue
        
        if png_file.exists():
            img = Image.open(png_file)
            # 이미 올바른 크기인지 확인
            if img.size != (size, size):
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            images.append(img)
    
    if not images:
        print("오류: 사용 가능한 아이콘 이미지를 찾을 수 없습니다.")
        return False
    
    # .ico 파일로 저장 (여러 크기 포함)
    images[0].save(
        output_file,
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in images],
        append_images=images[1:] if len(images) > 1 else None
    )
    
    print(f"성공: {output_file} 파일이 생성되었습니다.")
    print(f"포함된 크기: {[img.size for img in images]}")
    return True

if __name__ == "__main__":
    create_ico_from_png()

