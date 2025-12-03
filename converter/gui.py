from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QSlider,
    QHBoxLayout,
    QPushButton,
)

from .core import SUPPORTED_EXTENSIONS, batch_convert_to_webp


class DropListWidget(QListWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        # 항목을 선택할 수 없도록 설정 (단순 로그/표시용 리스트)
        self.setSelectionMode(QListWidget.NoSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # type: ignore[override]
        mime: QMimeData = event.mimeData()
        if not mime.hasUrls():
            event.ignore()
            return

        paths: List[Path] = []
        for url in mime.urls():
            local_path = url.toLocalFile()
            if not local_path:
                continue
            p = Path(local_path)
            if p.is_dir():
                # 디렉토리면 내부 파일까지 재귀적으로 탐색
                for child in p.rglob("*"):
                    if child.suffix.lower() in SUPPORTED_EXTENSIONS:
                        paths.append(child)
            else:
                paths.append(p)

        if not paths:
            QMessageBox.information(self, "알림", "지원하는 이미지 파일(PNG, JPG, JPEG)이 없습니다.")
            return

        # 최상위 윈도우(MainWindow)를 찾아서 콜백 호출
        window = self.window()
        if hasattr(window, "handle_files_dropped"):
            window.handle_files_dropped(paths)  # type: ignore[call-arg]
        else:
            # 이 경우는 구조가 바뀐 특수 케이스이므로, 안전하게 에러만 알림
            QMessageBox.warning(self, "경고", "드롭 이벤트를 처리할 수 있는 윈도우를 찾지 못했습니다.")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Image → WebP 변환기")
        self.setMinimumSize(480, 360)

        central = QWidget(self)
        layout = QVBoxLayout(central)

        info_label = QLabel(
            "이미지 파일(PNG, JPG, JPEG) 또는 폴더를 이 창으로 드래그 앤 드롭하면\n"
            "자동으로 WebP로 변환됩니다.",
            self,
        )
        info_label.setAlignment(Qt.AlignCenter)

        # 상단 컨트롤 영역 (품질 슬라이더 + 초기화 버튼)
        control_layout = QHBoxLayout()

        # 품질 슬라이더
        quality_title = QLabel("품질 (Quality):", self)
        self.quality_value_label = QLabel("80", self)
        self.quality_slider = QSlider(Qt.Horizontal, self)
        self.quality_slider.setMinimum(10)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(80)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.setTickPosition(QSlider.TicksBelow)
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_value_label.setText(str(v))
        )

        # 변환 목록 초기화 버튼
        self.clear_button = QPushButton("변환 목록 초기화", self)
        self.clear_button.clicked.connect(self.clear_converted_list)

        control_layout.addWidget(quality_title)
        control_layout.addWidget(self.quality_slider)
        control_layout.addWidget(self.quality_value_label)
        control_layout.addWidget(self.clear_button)

        self.list_widget = DropListWidget(self)
        self.list_widget.setAlternatingRowColors(True)

        layout.addWidget(info_label)
        layout.addLayout(control_layout)
        layout.addWidget(self.list_widget)

        self.setCentralWidget(central)

        status = QStatusBar(self)
        self.setStatusBar(status)
        self.statusBar().showMessage("준비 완료")

    # DropListWidget에서 호출
    def handle_files_dropped(self, paths: List[Path]) -> None:
        # UI 갱신
        self.list_widget.clear()
        for p in paths:
            item = QListWidgetItem(str(p))
            self.list_widget.addItem(item)

        quality = self.quality_slider.value()
        self.statusBar().showMessage(f"WebP 변환 중... (품질 {quality})")
        try:
            outputs = batch_convert_to_webp(paths, quality=quality)
        except Exception as e:  # 방어적 처리
            QMessageBox.critical(self, "에러", f"변환 중 오류가 발생했습니다:\n{e}")
            self.statusBar().showMessage("에러 발생")
            return

        self.statusBar().showMessage(f"변환 완료: {len(outputs)}개 파일")
        QMessageBox.information(
            self,
            "완료",
            f"WebP 변환이 완료되었습니다.\n변환된 파일 수: {len(outputs)}",
        )

    def clear_converted_list(self) -> None:
        """변환 목록과 상태 표시를 초기화."""
        self.list_widget.clear()
        self.statusBar().showMessage("목록이 초기화되었습니다.")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


