## 이미지 → WebP 변환 GUI (macOS / Windows)

이 프로젝트는 **macOS 및 Windows**용 이미지 변환 GUI 도구입니다.  
PNG / JPG / JPEG 파일(또는 폴더)을 창에 **드래그 앤 드롭** 하면, 같은 위치에 WebP 파일을 자동으로 만들어 줍니다.

- **입력 포맷**: `.png`, `.jpg`, `.jpeg`
- **출력 포맷**: `.webp`
- **기술 스택**: Python, Pillow, PySide6

### 1. Conda 환경 구성

- **환경 생성**

```bash
conda create -n img2webp python=3.11 -y
conda activate img2webp
```

- **의존성 설치**

```bash
pip install -r requirements.txt
```

### 2. 테스트 실행

이미지 변환 로직은 `converter/core.py` 에 있으며, `pytest` 로 테스트됩니다.

```bash
pytest
```

### 3. GUI 실행

개발/로컬 실행은 아래 둘 중 하나를 사용하면 됩니다.

- 모듈로 실행:

```bash
python -m converter.gui
```

- 진입점 스크립트 실행:

```bash
python run_gui.py
```

### 4. 사용 방법 (GUI 기능)

- **드래그 앤 드롭**

  - PNG / JPG / JPEG 파일 또는 폴더를 창 위로 드래그 앤 드롭
  - 폴더를 넣으면 내부를 재귀적으로 탐색하여 지원 포맷만 변환
  - 결과 WebP 파일은 **원본 파일과 같은 폴더**에 `이름.webp` 로 생성

- **품질(퀄리티) 슬라이더**

  - 상단에 **품질 (Quality) 슬라이더**가 있으며, 범위는 **10 ~ 100**, 기본값 **80**
  - 슬라이더 값에 따라 WebP `quality` 값이 변경됨
  - 상태바에 예: `WebP 변환 중... (품질 80)` 형식으로 표시

- **변환 목록 초기화 버튼**
  - 상단 컨트롤 영역에 **“변환 목록 초기화” 버튼**이 있음
  - 버튼 클릭 시 리스트에 표시된 항목이 모두 지워지고, 상태바에 “목록이 초기화되었습니다.” 출력

### 5. 내부 구조 요약

- **변환 코어**: `converter/core.py`
  - `convert_to_webp(input_path, output_path=None, quality=80)`
  - `batch_convert_to_webp(inputs, quality=80)`
  - `is_supported_image(path)`
- **GUI**: `converter/gui.py`
  - 드래그앤드롭, 품질 슬라이더, 초기화 버튼, 상태바 표시
- **테스트**: `tests/test_core.py`
  - 지원 확장자 체크, 변환 성공/실패 케이스, 배치 변환 동작 확인

### 6. 실행 파일로 패키징하기 (PyInstaller)

일반 사용자도 파이썬 설치 없이 쓸 수 있도록 **실행 파일** 형태로 패키징할 수 있습니다.

> **⚠️ 중요**: PyInstaller는 **크로스 컴파일을 지원하지 않습니다**. 각 플랫폼에서 해당 플랫폼용으로 빌드해야 합니다.
>
> - **macOS에서 빌드** → macOS용 `.app` 파일만 생성 (Windows에서 실행 불가)
> - **Windows에서 빌드** → Windows용 `.exe` 파일만 생성 (macOS에서 실행 불가)
>
> Windows용 실행 파일이 필요하면 **Windows PC에서 빌드**해야 합니다.

#### 6-1. macOS 앱(.app)으로 패키징하기

1. **의존성 확인**

```bash
conda activate img2webp
pip install -r requirements.txt
```

> **참고**: `requirements.txt`에 PyInstaller가 포함되어 있습니다. 이미 설치했다면 이 단계를 건너뛰어도 됩니다.

2. **앱 빌드 (`run_gui.py` 진입점 사용)**

```bash
cd .../Img2Webp
pyinstaller \
  --onedir \
  --windowed \
  --name "Img2WebP" \
  run_gui.py
```

- 빌드 후 `dist/Img2WebP.app` 생성
- 이 파일을 다른 Mac으로 복사해서 **더블클릭** 하면 바로 실행 가능  
  (첫 실행 때는 "확인되지 않은 개발자" 경고가 뜰 수 있으므로, 우클릭 → _열기_ 로 한 번 허용)

3. **앱 아이콘 설정(선택 사항)**

- 아이콘 이미지를 기반으로 `Img2WebP.icns` 파일을 만든 뒤, PyInstaller 옵션에 `--icon` 을 추가합니다.

```bash
pyinstaller \
  --onedir \
  --windowed \
  --name "Img2WebP" \
  --icon "Img2WebP.icns" \
  run_gui.py
```

또는 spec 파일 사용:

```bash
pyinstaller Img2WebP.spec
```

4. **DMG 패키지 만들기(선택 사항)**

- `dist/Img2WebP.app` 를 DMG로 감싸서 배포하고 싶다면:

```bash
cd dist
hdiutil create -volname "Img2WebP" -srcfolder "Img2WebP.app" -ov -format UDZO Img2WebP.dmg
```

- 그러면 `dist/Img2WebP.dmg` 가 생성되고, 이 파일 하나만 배포해도 사용자가 DMG를 열어 `Img2WebP.app` 를 `/Applications` 로 드래그해서 설치할 수 있습니다.

#### 6-2. Windows 실행 파일(.exe)로 패키징하기

1. **의존성 확인**

```bash
conda activate img2webp
pip install -r requirements.txt
```

> **참고**: `requirements.txt`에 PyInstaller가 포함되어 있습니다. 이미 설치했다면 이 단계를 건너뛰어도 됩니다.

2. **Windows용 아이콘 파일 생성**

- Windows에서는 `.ico` 파일이 필요합니다. 기존 PNG 아이콘을 사용하여 `.ico` 파일을 생성합니다:

```bash
python create_ico.py
```

- 이 명령어를 실행하면 `Img2WebP.ico` 파일이 생성됩니다.

3. **Windows 실행 파일 빌드**

- spec 파일을 사용하여 빌드:

```bash
pyinstaller Img2WebP_windows.spec
```

- 또는 직접 명령어로 빌드:

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "Img2WebP" \
  --icon "Img2WebP.ico" \
  run_gui.py
```

- 빌드 후 `dist/Img2WebP.exe` 생성
- 이 파일을 다른 Windows 컴퓨터로 복사해서 **더블클릭** 하면 바로 실행 가능

4. **배포 패키지 만들기(선택 사항)**

- Windows에서는 ZIP 파일로 배포하는 것이 일반적입니다:

```bash
cd dist
# Windows에서
powershell Compress-Archive -Path Img2WebP.exe -DestinationPath Img2WebP.zip
```

- 또는 수동으로 `dist/Img2WebP.exe` 파일을 ZIP으로 압축하여 배포할 수 있습니다.
