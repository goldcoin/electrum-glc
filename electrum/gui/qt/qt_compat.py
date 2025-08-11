"""
PyQt5/PyQt6 Compatibility Layer

This module provides a compatibility layer between PyQt5 and PyQt6,
allowing the codebase to work with either version while transitioning.
"""

import sys
from typing import Any

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QUrl, QTimer
    from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QKeySequence
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QGridLayout,
        QPushButton,
        QLabel,
        QLineEdit,
        QTextEdit,
        QComboBox,
        QCheckBox,
        QRadioButton,
        QGroupBox,
        QTabWidget,
        QTreeWidget,
        QTreeWidgetItem,
        QTableWidget,
        QTableWidgetItem,
        QListWidget,
        QListWidgetItem,
        QDialog,
        QDialogButtonBox,
        QMessageBox,
        QFileDialog,
        QProgressBar,
        QSlider,
        QSpinBox,
        QMenu,
        QMenuBar,
        QToolBar,
        QStatusBar,
        QSplitter,
        QScrollArea,
        QFrame,
        QStackedWidget,
        QSystemTrayIcon,
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
    from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QUrl, QTimer
    from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QGridLayout,
        QPushButton,
        QLabel,
        QLineEdit,
        QTextEdit,
        QComboBox,
        QCheckBox,
        QRadioButton,
        QGroupBox,
        QTabWidget,
        QTreeWidget,
        QTreeWidgetItem,
        QTableWidget,
        QTableWidgetItem,
        QListWidget,
        QListWidgetItem,
        QDialog,
        QDialogButtonBox,
        QMessageBox,
        QFileDialog,
        QProgressBar,
        QSlider,
        QSpinBox,
        QMenu,
        QMenuBar,
        QToolBar,
        QStatusBar,
        QSplitter,
        QScrollArea,
        QFrame,
        QStackedWidget,
        QSystemTrayIcon,
        QAction,
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
    # Core modules
    'QtCore', 'QtGui', 'QtWidgets',
    
    # Signals and slots
    'pyqtSignal', 'pyqtSlot',
    
    # Core classes
    'Qt', 'QUrl', 'QTimer',
    'QIcon', 'QPixmap', 'QFont', 'QAction', 'QKeySequence',
    
    # Widgets
    'QApplication', 'QMainWindow', 'QWidget',
    'QVBoxLayout', 'QHBoxLayout', 'QGridLayout',
    'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit',
    'QComboBox', 'QCheckBox', 'QRadioButton', 'QGroupBox',
    'QTabWidget', 'QTreeWidget', 'QTreeWidgetItem',
    'QTableWidget', 'QTableWidgetItem',
    'QListWidget', 'QListWidgetItem',
    'QDialog', 'QDialogButtonBox', 'QMessageBox', 'QFileDialog',
    'QProgressBar', 'QSlider', 'QSpinBox',
    'QMenu', 'QMenuBar', 'QToolBar', 'QStatusBar',
    'QSplitter', 'QScrollArea', 'QFrame', 'QStackedWidget',
    'QSystemTrayIcon',
    
    # Version flags
    'PYQT5', 'PYQT6',
    
    # Compatibility functions
    'exec_dialog', 'exec_app', 'get_qt_version',
    
    # Common enum values
    'AlignLeft', 'AlignRight', 'AlignCenter',
    'AlignTop', 'AlignBottom', 'AlignVCenter', 'AlignHCenter',
    'LeftButton', 'RightButton', 'MiddleButton',
    'Key_Return', 'Key_Enter', 'Key_Escape', 'Key_Tab', 'Key_Backtab', 'Key_Space',
    'Checked', 'Unchecked', 'PartiallyChecked',
    'Horizontal', 'Vertical',
]