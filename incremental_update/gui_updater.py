# gui_updater.py - TPW 增量更新 GUI 界面 (v2.0)
# 提供 PyQt5 更新对话框，使用 QThread 后台执行更新操作
# v2.0 新增: 变更日志显示、双进度条、失败重试、更好的状态提示

import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QTextEdit, QMessageBox, QWidget, QGroupBox,
)
from PyQt5.QtGui import QFont

from .updater import IncrementalUpdater


# ── 更新工作线程 ───────────────────────────────────────────

class UpdateWorker(QThread):
    """后台线程：执行增量更新操作，通过信号与 GUI 通信"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int, str)
    file_progress_signal = pyqtSignal(int, int, str)
    version_signal = pyqtSignal(str, str, str)
    finished_signal = pyqtSignal(bool, str, int, int)
    error_signal = pyqtSignal(str)

    def __init__(self, server_url, local_dir):
        super().__init__()
        self.server_url = server_url
        self.local_dir = local_dir
        self._updater = None
        self.last_local_ver = ""
        self.last_remote_ver = ""

    def cancel(self):
        if self._updater:
            self._updater.cancel()

    def run(self):
        self.log_signal.emit("正在初始化增量更新引擎...")

        self._updater = IncrementalUpdater(
            server_url=self.server_url,
            local_dir=self.local_dir,
            progress_callback=self._on_progress,
            log_callback=lambda msg: self.log_signal.emit(msg),
        )

        try:
            result = self._updater.check_update()
            if result is None:
                self.finished_signal.emit(False, "无法连接更新服务器，请检查网络后重试", 0, 0)
                return

            local_ver = result.get("local_version", "0.0.0")
            remote_ver = result.get("remote_version", "?")
            changelog = result.get("changelog", "")
            self.last_local_ver = local_ver
            self.last_remote_ver = remote_ver
            self.version_signal.emit(local_ver, remote_ver, changelog)

            if not result["has_update"]:
                self.finished_signal.emit(True, "当前已是最新版本 ({})".format(local_ver), 0, 0)
                return

            file_list = result["need_download"]
            if not file_list:
                self._updater._save_local_manifest(result["remote_manifest"])
                self.finished_signal.emit(True, "文件比对完成，无需下载 ({})".format(remote_ver), 0, 0)
                return

            self.log_signal.emit("发现 {} 个文件需要更新".format(len(file_list)))

            success, fail = self._updater.download_files(
                file_list,
                keep_files=result.get("keep_files"),
                remote_manifest=result.get("remote_manifest"),
            )

            if success > 0:
                self._updater._save_local_manifest(result["remote_manifest"])
                if fail == 0:
                    msg = "更新成功！当前版本: {}".format(remote_ver)
                else:
                    msg = "更新完成: {} (成功 {}, 失败 {})".format(remote_ver, success, fail)
                self.finished_signal.emit(fail == 0, msg, success, fail)
            else:
                self.finished_signal.emit(False, "更新失败，所有文件下载均未成功", 0, fail)

        except Exception as e:
            self.error_signal.emit(str(e))
            self.finished_signal.emit(False, "更新出错: {}".format(e), 0, 0)

    def _on_progress(self, current, total, message):
        self.progress_signal.emit(current, total, message)
        if "下载:" in message:
            fname = message.replace("下载:", "").strip()
            self.file_progress_signal.emit(current, total, fname)


# ── 更新对话框 (v2.0 增强版) ───────────────────────────────

class UpdateDialog(QDialog):
    """增量更新对话框窗口 (v2.0)
    
    新增: 变更日志显示、失败重试按钮、回滚提示、双进度条
    """

    def __init__(self, server_url, local_dir, parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.local_dir = local_dir
        self._worker = None
        self._update_success = False
        self._local_ver = "0.0.0"
        self._remote_ver = "?"

        self._init_ui()
        self._start_check()

    def _init_ui(self):
        self.setWindowTitle("增量更新")
        self.setMinimumSize(560, 520)
        self.resize(580, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # ── 版本信息区 ──
        self.lbl_version = QLabel("正在检查版本...")
        self.lbl_version.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a6fb5; padding: 4px;"
        )
        layout.addWidget(self.lbl_version)

        # ── 变更日志区 ──
        self.grp_changelog = QGroupBox("更新内容")
        self.grp_changelog.setVisible(False)
        grp_layout = QVBoxLayout(self.grp_changelog)
        self.lbl_changelog = QLabel("")
        self.lbl_changelog.setWordWrap(True)
        self.lbl_changelog.setStyleSheet("color: #444; font-size: 11px; padding: 4px;")
        grp_layout.addWidget(self.lbl_changelog)
        layout.addWidget(self.grp_changelog)

        # ── 总进度条 ──
        self.progress_total = QProgressBar()
        self.progress_total.setRange(0, 100)
        self.progress_total.setValue(0)
        self.progress_total.setFormat("总进度: %v/%m  %p%")
        layout.addWidget(self.progress_total)

        # ── 当前操作标签 ──
        self.lbl_current_file = QLabel("准备中...")
        self.lbl_current_file.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.lbl_current_file)

        # ── 日志区域 ──
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.txt_log.setFont(font)
        self.txt_log.setStyleSheet(
            "background-color: #fafafa; border: 1px solid #ddd; padding: 6px;"
        )
        self.txt_log.setMaximumBlockCount(500)
        layout.addWidget(self.txt_log, stretch=1)

        # ── 按钮区域 ──
        btn_layout = QHBoxLayout()

        self.btn_retry = QPushButton("重试")
        self.btn_retry.clicked.connect(self._on_retry)
        self.btn_retry.setVisible(False)
        self.btn_retry.setStyleSheet(
            "QPushButton { background-color: #ff9800; color: white; padding: 6px 16px; "
            "border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #f57c00; }"
        )
        btn_layout.addWidget(self.btn_retry)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_cancel.setMinimumWidth(80)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self._on_close)
        self.btn_close.setEnabled(False)
        self.btn_close.setMinimumWidth(80)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    # ── 操作逻辑 ──

    def _start_check(self):
        self._set_ui_state("running")
        self._worker = UpdateWorker(self.server_url, self.local_dir)
        self._worker.log_signal.connect(self._on_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.file_progress_signal.connect(self._on_file_progress)
        self._worker.version_signal.connect(self._on_version_info)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.error_signal.connect(self._on_error)
        self._worker.start()

    def _set_ui_state(self, state):
        if state == "running":
            self.btn_cancel.setEnabled(True)
            self.btn_close.setEnabled(False)
            self.btn_retry.setVisible(False)
            self.progress_total.setValue(0)
        elif state == "finished":
            self.btn_cancel.setEnabled(False)
            self.btn_close.setEnabled(True)
        elif state == "failed":
            self.btn_cancel.setEnabled(False)
            self.btn_close.setEnabled(True)
            self.btn_retry.setVisible(True)

    def _on_version_info(self, local_ver, remote_ver, changelog):
        self._local_ver = local_ver
        self._remote_ver = remote_ver
        self.lbl_version.setText(
            "本地版本: {}  →  服务器版本: {}".format(local_ver, remote_ver)
        )
        if changelog:
            self.lbl_changelog.setText(changelog)
            self.grp_changelog.setVisible(True)

    def _on_log(self, message):
        self.txt_log.append(message)
        sb = self.txt_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_progress(self, current, total, message):
        self.progress_total.setMaximum(max(total, 1))
        self.progress_total.setValue(current)
        if current > 0 and total > 0 and "已比对" in message:
            self.lbl_current_file.setText(message)

    def _on_file_progress(self, current, total, filename):
        if filename:
            self.lbl_current_file.setText("正在下载: {}".format(filename))

    def _on_finished(self, success, message, downloaded, failed):
        self._update_success = success
        self.lbl_version.setText(message)

        if failed > 0 and downloaded > 0:
            self._set_ui_state("failed")
            self.lbl_current_file.setText("{} 个文件下载失败，可点击「重试」".format(failed))
            return

        self._set_ui_state("finished")

        if success:
            self.lbl_current_file.setText("更新完成！")
            reply = QMessageBox.question(
                self, "更新完成",
                "增量更新已完成 ({})。\n\n是否立即重启程序以应用更新？".format(self._remote_ver),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._update_success = True
                self.accept()
        else:
            self.lbl_current_file.setText("更新未成功")
            if "已是最新" not in message:
                QMessageBox.warning(self, "更新提示", message)

    def _on_retry(self):
        self.txt_log.clear()
        self.txt_log.append("── 正在重试更新... ──")
        self._start_check()

    def _on_error(self, error_msg):
        self.txt_log.append("[错误] {}".format(error_msg))

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            reply = QMessageBox.question(
                self, "确认取消",
                "确定要取消更新吗？\n\n已下载的文件将自动回滚到原始状态。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._worker.cancel()
                self._set_ui_state("finished")
                self.lbl_current_file.setText("更新已取消 (已回滚变更)")

    def _on_close(self):
        if self._update_success:
            self.accept()
        else:
            self.reject()

    def was_update_successful(self):
        return self._update_success


# ── 便捷函数 ───────────────────────────────────────────────

def show_update_dialog(server_url, local_dir, parent=None):
    """显示增量更新对话框，返回 True 表示更新成功且用户选择重启。"""
    dialog = UpdateDialog(server_url, local_dir, parent)
    result = dialog.exec_()
    return result == QDialog.Accepted and dialog.was_update_successful()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    SERVER = "http://localhost:8000"
    LOCAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    show_update_dialog(SERVER, LOCAL)
