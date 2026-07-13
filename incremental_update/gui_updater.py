# gui_updater.py - TPW 增量更新 GUI 界面
# 提供 PyQt5 更新对话框，使用 QThread 后台执行更新操作

import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QTextEdit, QMessageBox, QWidget,
)
from PyQt5.QtGui import QFont

from .updater import IncrementalUpdater


# ── 更新工作线程 ───────────────────────────────────────────

class UpdateWorker(QThread):
    """后台线程：执行增量更新操作，通过信号与 GUI 通信"""

    # 信号定义
    log_signal = pyqtSignal(str)                       # 日志消息
    progress_signal = pyqtSignal(int, int, str)        # 总进度: current, total, message
    file_progress_signal = pyqtSignal(int, int)        # 单文件下载进度: downloaded, total (暂未使用)
    version_signal = pyqtSignal(str, str, bool)        # local_ver, remote_ver, has_update
    finished_signal = pyqtSignal(bool, str)            # success, message
    error_signal = pyqtSignal(str)                     # 错误消息

    def __init__(self, server_url, local_dir):
        super().__init__()
        self.server_url = server_url
        self.local_dir = local_dir
        self._updater = None

    def cancel(self):
        """取消更新"""
        if self._updater:
            self._updater.cancel()

    def run(self):
        self.log_signal.emit("初始化增量更新引擎...")

        self._updater = IncrementalUpdater(
            server_url=self.server_url,
            local_dir=self.local_dir,
            progress_callback=self._on_progress,
            log_callback=lambda msg: self.log_signal.emit(msg),
        )

        try:
            success = self._updater.apply_update()
            local_ver = self._updater.get_local_version()
            if success:
                self.finished_signal.emit(True, f"更新成功！当前版本: {local_ver}")
            else:
                self.finished_signal.emit(False, "更新未完全成功，请查看日志")
        except Exception as e:
            self.error_signal.emit(str(e))
            self.finished_signal.emit(False, f"更新出错: {e}")

    def _on_progress(self, current, total, message):
        self.progress_signal.emit(current, total, message)


# ── 更新对话框 ─────────────────────────────────────────────

class UpdateDialog(QDialog):
    """增量更新对话框窗口"""

    def __init__(self, server_url, local_dir, parent=None):
        """
        Args:
            server_url: 更新服务器基础 URL
            local_dir: 本地安装目录
            parent: 父窗口
        """
        super().__init__(parent)
        self.server_url = server_url
        self.local_dir = local_dir
        self._worker = None
        self._update_success = False

        self._init_ui()
        self._start_check()

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("增量更新")
        self.setMinimumSize(520, 420)
        self.resize(550, 460)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ── 版本信息 ──
        ver_layout = QHBoxLayout()
        self.lbl_version = QLabel("正在检查版本...")
        self.lbl_version.setStyleSheet("font-size: 13px; font-weight: bold; color: #005500;")
        ver_layout.addWidget(self.lbl_version)
        ver_layout.addStretch()
        layout.addLayout(ver_layout)

        # ── 总进度条 ──
        self.progress_total = QProgressBar()
        self.progress_total.setRange(0, 100)
        self.progress_total.setValue(0)
        self.progress_total.setFormat("%v/%m 文件  %p%")
        layout.addWidget(self.progress_total)

        # ── 当前文件进度标签 ──
        self.lbl_current_file = QLabel("")
        self.lbl_current_file.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.lbl_current_file)

        # ── 日志区域 ──
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.txt_log.setFont(font)
        self.txt_log.setStyleSheet(
            "background-color: #f5f5f5; border: 1px solid #ccc; padding: 4px;"
        )
        layout.addWidget(self.txt_log, stretch=1)

        # ── 按钮区域 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self._on_close)
        self.btn_close.setEnabled(False)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    # ── 操作逻辑 ──

    def _start_check(self):
        """启动后台检查线程"""
        self._worker = UpdateWorker(self.server_url, self.local_dir)
        self._worker.log_signal.connect(self._on_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.file_progress_signal.connect(self._on_file_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.error_signal.connect(self._on_error)
        self._worker.start()

    def _on_log(self, message):
        self.txt_log.append(message)
        # 自动滚动到底部
        sb = self.txt_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_progress(self, current, total, message):
        self.progress_total.setMaximum(total)
        self.progress_total.setValue(current)
        self.lbl_current_file.setText(message)

        # 更新版本标签
        if self._worker and self._worker._updater:
            local = self._worker._updater.get_local_version()

    def _on_file_progress(self, downloaded, total):
        pass  # 预留：单文件下载进度

    def _on_finished(self, success, message):
        self._update_success = success
        self.btn_cancel.setEnabled(False)
        self.btn_close.setEnabled(True)
        self.lbl_version.setText(message)

        if success:
            reply = QMessageBox.question(
                self, "更新完成",
                "增量更新已完成。\n\n是否立即重启程序以应用更新？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._update_success = True
                self.accept()
        else:
            QMessageBox.warning(self, "更新提示", message)

    def _on_error(self, error_msg):
        self.txt_log.append(f"[错误] {error_msg}")

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            reply = QMessageBox.question(
                self, "确认取消",
                "确定要取消更新吗？已完成的部分不会回滚。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._worker.cancel()
                self.btn_cancel.setEnabled(False)
                self.btn_close.setEnabled(True)

    def _on_close(self):
        if self._update_success:
            self.accept()
        else:
            self.reject()

    def was_update_successful(self):
        """返回更新是否成功"""
        return self._update_success


# ── 便捷函数 ───────────────────────────────────────────────

def show_update_dialog(server_url, local_dir, parent=None):
    """
    显示增量更新对话框，返回 True 表示更新成功且用户选择重启。

    Args:
        server_url: 更新服务器基础 URL
        local_dir: 本地安装目录
        parent: 父窗口

    Returns:
        bool: 更新成功，且用户选择重启
    """
    dialog = UpdateDialog(server_url, local_dir, parent)
    result = dialog.exec_()
    return result == QDialog.Accepted and dialog.was_update_successful()


if __name__ == "__main__":
    # 独立测试
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    SERVER = "http://localhost:8000"
    LOCAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    show_update_dialog(SERVER, LOCAL)
