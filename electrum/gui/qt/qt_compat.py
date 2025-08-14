"""
PyQt5/PyQt6 Compatibility Layer

This module provides a compatibility layer between PyQt5 and PyQt6,
allowing the codebase to work with either version while transitioning.
"""

from typing import Any

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, pyqtSlot
    from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence, QPixmap
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QStackedWidget,
        QStatusBar,
        QSystemTrayIcon,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYQT6 = True
    PYQT5 = False

    # PyQt6 specific adjustments
    def exec_dialog(dialog: Any) -> int:
        """Execute a dialog (PyQt6 uses exec() instead of exec_())"""
        return dialog.exec()

    def exec_app(app: Any) -> int:
        """Execute application (PyQt6 uses exec() instead of exec_())"""
        return app.exec()

except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import QFont, QIcon, QKeySequence, QPixmap
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QStackedWidget,
        QStatusBar,
        QSystemTrayIcon,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYQT6 = False
    PYQT5 = True

    # PyQt5 specific adjustments
    def exec_dialog(dialog: Any) -> int:
        """Execute a dialog (PyQt5 uses exec_())"""
        return dialog.exec_()

    def exec_app(app: Any) -> int:
        """Execute application (PyQt5 uses exec_())"""
        return app.exec_()


# Common compatibility functions
def get_qt_version() -> str:
    """Return the Qt version string"""
    if PYQT6:
        return f"PyQt6 {QtCore.PYQT_VERSION_STR}"
    else:
        return f"PyQt5 {QtCore.PYQT_VERSION_STR}"


# Enum compatibility
if PYQT6:
    # PyQt6 uses scoped enums
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    AlignTop = Qt.AlignmentFlag.AlignTop
    AlignBottom = Qt.AlignmentFlag.AlignBottom
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    AlignHCenter = Qt.AlignmentFlag.AlignHCenter

    LeftButton = Qt.MouseButton.LeftButton
    RightButton = Qt.MouseButton.RightButton
    MiddleButton = Qt.MouseButton.MiddleButton

    Key_Return = Qt.Key.Key_Return
    Key_Enter = Qt.Key.Key_Enter
    Key_Escape = Qt.Key.Key_Escape
    Key_Tab = Qt.Key.Key_Tab
    Key_Backtab = Qt.Key.Key_Backtab
    Key_Space = Qt.Key.Key_Space

    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    PartiallyChecked = Qt.CheckState.PartiallyChecked

    Horizontal = Qt.Orientation.Horizontal
    Vertical = Qt.Orientation.Vertical
else:
    # PyQt5 uses direct enum access
    AlignLeft = Qt.AlignLeft
    AlignRight = Qt.AlignRight
    AlignCenter = Qt.AlignCenter
    AlignTop = Qt.AlignTop
    AlignBottom = Qt.AlignBottom
    AlignVCenter = Qt.AlignVCenter
    AlignHCenter = Qt.AlignHCenter

    LeftButton = Qt.LeftButton
    RightButton = Qt.RightButton
    MiddleButton = Qt.MiddleButton

    Key_Return = Qt.Key_Return
    Key_Enter = Qt.Key_Enter
    Key_Escape = Qt.Key_Escape
    Key_Tab = Qt.Key_Tab
    Key_Backtab = Qt.Key_Backtab
    Key_Space = Qt.Key_Space

    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    PartiallyChecked = Qt.PartiallyChecked

    Horizontal = Qt.Horizontal
    Vertical = Qt.Vertical


# Export all for convenience
__all__ = [
    # Version flags
    "PYQT5",
    "PYQT6",
    "AlignBottom",
    "AlignCenter",
    "AlignHCenter",
    # Common enum values
    "AlignLeft",
    "AlignRight",
    "AlignTop",
    "AlignVCenter",
    "Checked",
    "Horizontal",
    "Key_Backtab",
    "Key_Enter",
    "Key_Escape",
    "Key_Return",
    "Key_Space",
    "Key_Tab",
    "LeftButton",
    "MiddleButton",
    "PartiallyChecked",
    "QAction",
    # Widgets
    "QApplication",
    "QCheckBox",
    "QComboBox",
    "QDialog",
    "QDialogButtonBox",
    "QFileDialog",
    "QFont",
    "QFrame",
    "QGridLayout",
    "QGroupBox",
    "QHBoxLayout",
    "QIcon",
    "QKeySequence",
    "QLabel",
    "QLineEdit",
    "QListWidget",
    "QListWidgetItem",
    "QMainWindow",
    "QMenu",
    "QMenuBar",
    "QMessageBox",
    "QPixmap",
    "QProgressBar",
    "QPushButton",
    "QRadioButton",
    "QScrollArea",
    "QSlider",
    "QSpinBox",
    "QSplitter",
    "QStackedWidget",
    "QStatusBar",
    "QSystemTrayIcon",
    "QTabWidget",
    "QTableWidget",
    "QTableWidgetItem",
    "QTextEdit",
    "QTimer",
    "QToolBar",
    "QTreeWidget",
    "QTreeWidgetItem",
    "QUrl",
    "QVBoxLayout",
    "QWidget",
    # Core classes
    "Qt",
    # Core modules
    "QtCore",
    "QtGui",
    "QtWidgets",
    "RightButton",
    "Unchecked",
    "Vertical",
    "exec_app",
    # Compatibility functions
    "exec_dialog",
    "get_qt_version",
    # Signals and slots
    "pyqtSignal",
    "pyqtSlot",
]
