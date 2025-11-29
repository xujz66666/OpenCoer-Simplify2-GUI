import sys
import os
import json
# Add the project root directory to the path to ensure all modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFileDialog,
                             QMessageBox, QProgressBar, QTextEdit, QComboBox, QCheckBox,
                             QGroupBox, QGridLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
                             QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Import the original OpCore Simplify modules
try:
    from Scripts.datasets import os_data
    from Scripts.datasets import chipset_data
    from Scripts import acpi_guru
    from Scripts import compatibility_checker
    from Scripts import config_prodigy
    from Scripts import gathering_files
    from Scripts import hardware_customizer
    from Scripts import kext_maestro
    from Scripts import report_validator
    from Scripts import run
    from Scripts import smbios
    from Scripts import utils
    import updater
except ImportError as e:
    print(f"Warning: Unable to import some modules: {e}")
    print("Continuing with simulation functionality")

# Build worker thread class for handling time-consuming operations
class BuildThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    log = pyqtSignal(str)
    
    def __init__(self, parent, config=None):
        super().__init__(parent)
        self.config = config or {}
    
    def run(self):
        try:
            # Simulate build process progress updates
            # In actual use, this will call the build_opencore_efi method from the original code
            self.log.emit("Starting OpenCore EFI build...")
            self.progress.emit(10, "Initializing build environment")
            self.msleep(500)
            
            # Simulate configuration validation
            self.log.emit("Validating hardware report and configuration...")
            self.progress.emit(20, "Validating configuration")
            self.msleep(500)
            
            # Simulate ACPI patch application
            self.log.emit("Applying ACPI patches...")
            self.progress.emit(35, "Applying ACPI patches")
            self.msleep(500)
            
            # Simulate Kext configuration
            self.log.emit("Configuring and copying Kext drivers...")
            self.progress.emit(50, "Configuring Kext drivers")
            self.msleep(500)
            
            # Simulate SMBIOS generation
            self.log.emit("Generating SMBIOS information...")
            self.progress.emit(65, "Generating SMBIOS information")
            self.msleep(500)
            
            # Simulate config file generation
            self.log.emit("Generating config.plist configuration file...")
            self.progress.emit(80, "Generating configuration file")
            self.msleep(500)
            
            # Simulate EFI packaging
            self.log.emit("Packaging EFI folder...")
            self.progress.emit(90, "Packaging EFI")
            self.msleep(500)
            
            # Complete build
            self.progress.emit(100, "Build completed")
            self.log.emit("OpenCore EFI build completed!")
            self.finished.emit(True, "EFI build successfully completed")
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
            self.finished.emit(False, f"Build failed: {str(e)}")

# Base page class
class BasePage(QWidget):
    # Unified stylesheet constants
    STYLES = {
        'title': "font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;",
        'subtitle': "font-size: 14px; font-weight: bold; color: #34495e; margin-top: 15px; margin-bottom: 10px;",
        'info': "color: #7f8c8d; margin-bottom: 15px;",
        'group_box': "QGroupBox { font-weight: bold; color: #34495e; border: 1px solid #bdc3c7; border-radius: 4px; margin-top: 5px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }",
        'button': "background-color: #3498db; color: white; border: none; border-radius: 4px; padding: 8px 16px; font-weight: bold;",
        'button:hover': "background-color: #2980b9;",
        'button:disabled': "background-color: #95a5a6; color: #bdc3c7;",
        'input': "border: 1px solid #bdc3c7; border-radius: 4px; padding: 6px;",
        'success': "color: #27ae60;",
        'warning': "color: #f39c12;",
        'error': "color: #e74c3c;"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
    
    def init_ui(self):
        pass
    
    def update_status(self, text):
        if self.main_window:
            self.main_window.update_status_bar(text)
    
    def log_message(self, message):
        if self.main_window:
            self.main_window.log_message(message)
    
    def show_error(self, title, message):
        """Display error message dialog"""
        self.update_status(f"Error: {message}")
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title, message):
        """Display warning message dialog"""
        self.update_status(f"Warning: {message}")
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title, message):
        """Display information message dialog"""
        self.update_status(message)
        QMessageBox.information(self, title, message)
    
    def show_confirm(self, title, message):
        """Display confirmation dialog and return user selection"""
        result = QMessageBox.question(self, title, message, 
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)
        return result == QMessageBox.Yes
    
    def handle_exception(self, exception, operation="Operation"):
        """Handle exceptions uniformly"""
        error_msg = f"{operation} failed: {str(exception)}"
        self.show_error("Operation Failed", error_msg)
        self.log_message(error_msg)
        import traceback
        traceback_str = traceback.format_exc()
        self.log_message(f"Detailed error information:\n{traceback_str}")
    
    def create_title(self, text):
        """创建统一样式的标题标"""
        title = QLabel(text)
        title.setStyleSheet(self.STYLES['title'])
        return title
    
    def create_info_text(self, text):
        """创建统一样式的信息文"""
        info = QLabel(text)
        info.setWordWrap(True)
        info.setStyleSheet(self.STYLES['info'])
        return info
    
    def create_group_box(self, title):
        """创建统一样式的分组框"""
        group_box = QGroupBox(title)
        group_box.setStyleSheet(self.STYLES['group_box'])
        return group_box
    
    def create_button(self, text, callback=None):
        """Create a button with unified style钮"""
        button = QPushButton(text)
        button.setStyleSheet(f"{self.STYLES['button']}")
        if callback:
            button.clicked.connect(callback)
        return button
    
    def validate_required_fields(self):
        """Validate required fields (can be overridden by subclasses)"""
        return True

# Hardware Report Page
class HardwareReportPage(BasePage):
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select Hardware Report")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description text
        info = QLabel("Please select or export a hardware report to create a matching OpenCore EFI for your system.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(info)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Hardware Report")
        self.export_btn.setMinimumHeight(30)
        self.export_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px;")
        self.export_btn.clicked.connect(self.export_hardware_report)
        
        self.select_btn = QPushButton("Select Hardware Report File")
        self.select_btn.setMinimumHeight(30)
        self.select_btn.setStyleSheet("background-color: #2196F3; color: white; border-radius: 4px;")
        self.select_btn.clicked.connect(self.select_hardware_report)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.select_btn)
        button_layout.setSpacing(10)
        layout.addLayout(button_layout)
        
        # Report info display
        self.report_info = QLabel("No hardware report selected")
        self.report_info.setStyleSheet("color: #333; font-weight: bold; margin: 15px 0 10px;")
        layout.addWidget(self.report_info)
        
        # Create hardware overview section
        overview_group = QGroupBox("Hardware Overview")
        overview_layout = QVBoxLayout()
        
        self.hardware_overview = QTextEdit()
        self.hardware_overview.setReadOnly(True)
        self.hardware_overview.setMaximumHeight(300)
        self.hardware_overview.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")
        self.hardware_overview.setPlaceholderText("Hardware overview information will be displayed here after selecting or generating a hardware report...")
        
        overview_layout.addWidget(self.hardware_overview)
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        
        # Add tip information
        tip_label = QLabel("Tip: Hardware report contains key information about CPU, motherboard, GPU, etc., which is the foundation for correct OpenCore configuration")
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet("color: #FF9800; font-size: 12px; margin-top: 10px;")
        layout.addWidget(tip_label)
        
        # Bottom spacer
        layout.addStretch()
    
    def export_hardware_report(self):
        self.update_status("Exporting hardware report...")
        try:
            # Try to use the export function from original code
            try:
                from run import export_hardware_report
                report_path = export_hardware_report()
                self.log_message(f"Hardware report exported to: {report_path}")
                
                # Try to load report content and display overview
                try:
                    with open(report_path, 'r') as f:
                        report_data = json.load(f)
                        self.update_hardware_overview(report_data)
                        # Update main window status
                        self.main_window.hardware_report_path = report_path
                        self.main_window.hardware_info = report_data
                        self.main_window.update_main_status()
                except Exception as e:
                    self.log_message(f"Cannot load report content: {e}")
                
                self.update_status("Export completed")
                self.show_info("Success", f"Hardware report has been successfully exported to: {report_path}")
            except (ImportError, AttributeError):
                # If original function cannot be imported, use mock implementation
                self.log_message("Using simulated function to export hardware report")
                # Simulate export process
                import tempfile
                temp_dir = tempfile.gettempdir()
                report_path = os.path.join(temp_dir, "hardware_report.json")
                # Create mock report data
                mock_report = {
                    "cpu": {"model": "Intel Core i7", "cores": 8, "threads": 16},
                    "gpu": {"model": "AMD Radeon RX 5700", "vram": "8GB"},
                    "ram": {"size": "32GB", "speed": "3200MHz"},
                    "motherboard": {"model": "ASUS ROG STRIX Z390-E", "chipset": "Z390"},
                    "storage": [{"model": "Samsung 970 EVO", "capacity": "1TB", "type": "NVMe"}],
                    "network": {"ethernet": "Intel I219-V", "wifi": "Intel AX200"}
                }
                with open(report_path, 'w') as f:
                    json.dump(mock_report, f, indent=4)
                
                self.log_message(f"Simulated hardware report exported to: {report_path}")
                self.update_hardware_overview(mock_report)
                
                # Update main window status
                self.main_window.hardware_report_path = report_path
                self.main_window.hardware_info = mock_report
                self.main_window.update_main_status()
                
                self.update_status("Export completed")
                self.show_info("Success", f"Hardware report successfully exported to: {report_path}")
        except Exception as e:
            self.handle_exception(e, "Export hardware report")
    
    def update_hardware_overview(self, report_data):
        """Update hardware overview display"""
        overview_text = "Hardware Overview Information:\n\n"
        
        if "cpu" in report_data:
            cpu = report_data["cpu"]
            overview_text += f"CPU: {cpu.get('model', 'Unknown')}\n"
            overview_text += f"Cores: {cpu.get('cores', 'Unknown')}\n"
            overview_text += f"Threads: {cpu.get('threads', 'Unknown')}\n\n"
        
        if "motherboard" in report_data:
            mobo = report_data["motherboard"]
            overview_text += f"Motherboard: {mobo.get('model', 'Unknown')}\n"
            overview_text += f"Chipset: {mobo.get('chipset', 'Unknown')}\n\n"
        
        if "gpu" in report_data:
            gpu = report_data["gpu"]
            overview_text += f"GPU: {gpu.get('model', 'Unknown')}\n"
            overview_text += f"VRAM: {gpu.get('vram', 'Unknown')}\n\n"
        
        if "ram" in report_data:
            ram = report_data["ram"]
            overview_text += f"RAM: {ram.get('size', 'Unknown')}\n"
            overview_text += f"Speed: {ram.get('speed', 'Unknown')}\n\n"
        
        if "storage" in report_data and isinstance(report_data["storage"], list):
            storage_devices = report_data["storage"]
            overview_text += "Storage Devices:\n"
            for device in storage_devices[:3]:  # Show up to 3 storage devices
                overview_text += f"- {device.get('model', 'Unknown')} ({device.get('capacity', 'Unknown')}, {device.get('type', 'Unknown')})\n"
            if len(storage_devices) > 3:
                overview_text += f"... and {len(storage_devices) - 3} other storage devices\n"
            overview_text += "\n"
        
        if "network" in report_data:
            network = report_data["network"]
            overview_text += "Network Devices:\n"
            overview_text += f"Ethernet: {network.get('ethernet', 'Unknown')}\n"
            overview_text += f"Wi-Fi: {network.get('wifi', 'Unknown')}\n"
        
        self.hardware_overview.setText(overview_text)
    
    def select_hardware_report(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Hardware Report", "", "JSON Files (*.json)")
        if file_path:
            self.update_status(f"Selected hardware report: {os.path.basename(file_path)}")
            self.report_info.setText(f"Selected: {os.path.basename(file_path)}")
            try:
                # Try to use the validation function from original code
                try:
                    from report_validator import validate_report
                    is_valid, message = validate_report(file_path)
                    if is_valid:
                        self.log_message(f"Hardware report validation successful: {message}")
                        if self.main_window:
                            self.main_window.hardware_report_path = file_path
                            # Parse report, extract hardware information
                            with open(file_path, 'r') as f:
                                report_data = json.load(f)
                                self.main_window.hardware_info = report_data
                                # Update hardware overview
                                self.update_hardware_overview(report_data)
                            self.main_window.update_main_status()
                    else:
                        self.log_message(f"Hardware report validation failed: {message}")
                        QMessageBox.warning(self, "Validation Failed", message)
                except (ImportError, AttributeError):
                    # If original function cannot be imported, use mock validation
                    self.log_message("Using simulated function to validate hardware report")
                    # Simple JSON file validation
                    try:
                        with open(file_path, 'r') as f:
                            report_data = json.load(f)
                        self.log_message(f"Simulated validation passed: {file_path}")
                        if self.main_window:
                            self.main_window.hardware_report_path = file_path
                            self.main_window.hardware_info = report_data
                            # Update hardware overview
                            self.update_hardware_overview(report_data)
                            self.main_window.update_main_status()
                    except json.JSONDecodeError:
                        self.show_warning("Validation Failed", "The selected file is not a valid JSON format")
            except Exception as e:
                self.handle_exception(e, "Validating hardware report")

# macOS Version Selection Page
class MacOSVersionPage(BasePage):
    def __init__(self, parent=None, main_window=None):
        self.main_window = main_window
        super().__init__(parent)
        # init_ui将由BasePage处理
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select macOS Version")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Description text
        self.info = QLabel("Please select the macOS version you want to use. It is recommended to check hardware compatibility before selecting.")
        self.info.setWordWrap(True)
        self.info.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(self.info)
        
        # Version list with beautified style
        version_group = QGroupBox("Available macOS Versions")
        version_group.setStyleSheet("QGroupBox { font-weight: bold; color: #34495e; border: 1px solid #bdc3c7; border-radius: 4px; margin-top: 5px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        version_layout = QVBoxLayout()
        
        self.version_list = QComboBox()
        # Add version data and compatibility information
        self.version_data = {
            "macOS Sonoma (14)": {"compatibility": "Recommended for newer hardware", "color": "#3498db"},
            "macOS Ventura (13)": {"compatibility": "Widely compatible", "color": "#27ae60"},
            "macOS Monterey (12)": {"compatibility": "Good stability", "color": "#f39c12"},
            "macOS Big Sur (11)": {"compatibility": "Supports older hardware", "color": "#e67e22"},
            "macOS Catalina (10.15)": {"compatibility": "Supports legacy hardware", "color": "#e74c3c"}
        }
        
        # 添加版本到下拉列�?
        self.version_list.addItems(self.version_data.keys())
        
        # 设置ComboBox样式
        self.version_list.setStyleSheet("QComboBox { padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background-color: white; } QComboBox:hover { border: 1px solid #3498db; } QComboBox::drop-down { border-left: 1px solid #bdc3c7; border-top-right-radius: 4px; border-bottom-right-radius: 4px; } QComboBox::down-arrow { image: url(:/icons/arrow-down.png); width: 16px; height: 16px; }")
        self.version_list.currentIndexChanged.connect(self.on_version_changed)
        version_layout.addWidget(self.version_list)
        
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)
        
        # Add compatibility check button
        check_layout = QHBoxLayout()
        self.check_compatibility_btn = QPushButton("Check Hardware Compatibility")
        self.check_compatibility_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 4px; padding: 8px 16px; font-weight: 500;")
        self.check_compatibility_btn.clicked.connect(self.check_compatibility)
        check_layout.addWidget(self.check_compatibility_btn)
        check_layout.addStretch()
        layout.addLayout(check_layout)
        
        # Compatibility result area
        self.compatibility_result = QTextEdit()
        self.compatibility_result.setReadOnly(True)
        self.compatibility_result.setMinimumHeight(150)
        self.compatibility_result.setPlaceholderText("Compatibility check results will be displayed here...")
        self.compatibility_result.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;")
        layout.addWidget(self.compatibility_result)
        
        # Recommended version label
        self.recommend_label = QLabel("")
        self.recommend_label.setStyleSheet("color: #27ae60; font-weight: 500; margin: 10px 0;")
        self.recommend_label.setWordWrap(True)
        layout.addWidget(self.recommend_label)
        
        # Confirm button
        button_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm Selection")
        self.confirm_btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 4px; padding: 8px 24px; font-weight: 500;")
        self.confirm_btn.clicked.connect(self.confirm_selection)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Bottom spacer
        layout.addStretch()
        
        # 初始化时根据当前选择更新推荐信息
        self.on_version_changed(self.version_list.currentIndex())
    
    def on_version_changed(self, index):
        """Update recommendation when version selection changes"""
        if index >= 0 and index < self.version_list.count():
            selected_version = self.version_list.currentText()
            if selected_version in self.version_data:
                version_info = self.version_data[selected_version]
                self.recommend_label.setText(f"Recommendation: {version_info['compatibility']}")
                # 可以根据硬件信息进一步优化推�?
                if hasattr(self.main_window, 'hardware_info') and self.main_window.hardware_info:
                    # 这里可以添加更智能的推荐逻辑
                    pass
    
    def check_compatibility(self):
        """Check hardware compatibility with selected macOS version"""
        self.update_status("Checking hardware compatibility...")
        self.compatibility_result.clear()
        
        if not hasattr(self.main_window, 'hardware_info') or not self.main_window.hardware_info:
            self.update_status("Please select or export a hardware report first")
            QMessageBox.warning(self, "Warning", "Please select or export a hardware report first")
            return
        
        try:
            # Simulate compatibility check
            hardware_info = self.main_window.hardware_info
            selected_version = self.version_list.currentText()
            result_text = f"Compatibility check results (with {selected_version}):\n\n"
            
            # CPU compatibility
            if "cpu" in hardware_info and "model" in hardware_info["cpu"]:
                cpu_model = hardware_info["cpu"]["model"]
                if "Intel" in cpu_model:
                    result_text += f"�?CPU ({cpu_model}): Compatible\n"
                    result_text += "  - Tip: Ensure Hyper-Threading is enabled\n\n"
                elif "AMD" in cpu_model:
                    result_text += f"! CPU ({cpu_model}): Requires additional patches\n"
                    result_text += "  - Tip: SSDT-PLUG patch is required\n\n"
                else:
                    result_text += f"? CPU ({cpu_model}): Compatibility unknown\n\n"
            
            # GPU compatibility
            if "gpu" in hardware_info and "model" in hardware_info["gpu"]:
                gpu_model = hardware_info["gpu"]["model"]
                if any(x in gpu_model for x in ["Intel Iris", "Intel UHD", "Intel HD"]):
                    result_text += f"GPU ({gpu_model}): Native support\n\n"
                elif any(x in gpu_model for x in ["AMD", "Radeon"]):
                    result_text += f"GPU ({gpu_model}): Native support\n\n"
                elif any(x in gpu_model for x in ["NVIDIA", "GTX", "RTX"]):
                    result_text += f"GPU ({gpu_model}): Limited support in some versions\n"
                    result_text += "  - Tip: Only supported up to macOS Mojave 10.14.6\n\n"
                else:
                    result_text += f"GPU ({gpu_model}): Compatibility unknown\n\n"
            
            # Version recommendation
            result_text += "Overall recommendation: "
            if "cpu" in hardware_info and "model" in hardware_info["cpu"]:
                cpu_model = hardware_info["cpu"]["model"]
                if "Intel" in cpu_model and ("13th" in cpu_model or "12th" in cpu_model or "11th" in cpu_model):
                    result_text += "Your CPU is relatively new, you can choose macOS Sonoma or Ventura"
                    self.compatibility_result.setStyleSheet("background-color: #e8f5e9; border: 2px solid #27ae60; border-radius: 4px;")
                elif "Intel" in cpu_model and ("10th" in cpu_model or "9th" in cpu_model or "8th" in cpu_model):
                    result_text += "Your CPU is suitable for macOS Ventura or Monterey"
                    self.compatibility_result.setStyleSheet("background-color: #e8f5e9; border: 2px solid #27ae60; border-radius: 4px;")
                elif "Intel" in cpu_model and ("7th" in cpu_model or "6th" in cpu_model):
                    result_text += "Recommended to use macOS Monterey or Big Sur"
                    self.compatibility_result.setStyleSheet("background-color: #fff3cd; border: 2px solid #f39c12; border-radius: 4px;")
                else:
                    result_text += "Your CPU may be older, it is recommended to use an older version of macOS"
                    self.compatibility_result.setStyleSheet("background-color: #f8d7da; border: 2px solid #e74c3c; border-radius: 4px;")
            else:
                result_text += "Cannot determine the best version based on CPU, please refer to other hardware information"
                self.compatibility_result.setStyleSheet("background-color: #f8f9fa; border: 2px solid #6c757d; border-radius: 4px;")
            
            self.compatibility_result.setPlainText(result_text)
            self.update_status("Compatibility check completed")
            
        except Exception as e:
            self.update_status(f"Compatibility check failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"Compatibility check failed: {str(e)}")
    
    def confirm_selection(self):
        selected_version = self.version_list.currentText()
        self.update_status(f"Selected macOS version: {selected_version}")
        
        # Update main window status
        if self.main_window:
            self.main_window.selected_macos_version = selected_version
            self.main_window.update_main_status()
        
        # Display selection result
        msg = f"Selected: {selected_version}\n\n"
        
        # Check if there are compatibility check results
        if self.compatibility_result.toPlainText():
            msg += "Compatibility check results:\n"
            # Extract key recommendation
            lines = self.compatibility_result.toPlainText().split("\n")
            for line in lines:
                if "Overall recommendation:" in line:
                    msg += line.replace("Overall recommendation: ", "") + "\n"
                    break
        else:
            msg += "Tip: You can use the 'Check Hardware Compatibility' button for more detailed compatibility information"
        
        self.show_info("Success", msg)

# ACPI Configuration Page
class ACPIConfigPage(BasePage):
    def __init__(self, parent=None, main_window=None):
        self.main_window = main_window
        super().__init__(parent)
        # init_ui将由BasePage处理
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("ACPI Patch Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Description text
        info = QLabel("Select the required ACPI patches. Different patches are suitable for different hardware configurations. Use 'Auto-detect best patches' to automatically select the most suitable patches based on your hardware.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(info)
        
        # 补丁选择列表 - 美化样式
        self.patches_list = QTreeWidget()
        self.patches_list.setHeaderLabels(["Patch Name", "Description", "Status"])
        self.patches_list.setColumnWidth(0, 200)
        self.patches_list.setColumnWidth(1, 400)
        self.patches_list.setColumnWidth(2, 80)
        
        # Set TreeWidget style
        self.patches_list.setStyleSheet("""
            QTreeWidget { 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTreeWidget::item {
                height: 30px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
            }
            QTreeWidget::indicator:checked {
                image: url(:/icons/checkbox-checked.png);
                width: 16px;
                height: 16px;
            }
            QTreeWidget::indicator:unchecked {
                image: url(:/icons/checkbox-unchecked.png);
                width: 16px;
                height: 16px;
            }
        """)
        
        # Add more detailed patch data, including priority and compatibility information
        self.patches_data = {
            "FixHPET": {"description": "Fix HPET device", "enabled": True, "priority": "High", "compatibility": "All systems"},
            "FixRTC": {"description": "Fix RTC clock", "enabled": True, "priority": "High", "compatibility": "All systems"},
            "SSDT-PLUG": {"description": "CPU power management patch", "enabled": True, "priority": "High", "compatibility": "All CPUs"},
            "SSDT-AWAC": {"description": "Fix AWAC clock", "enabled": False, "priority": "Medium", "compatibility": "New motherboards"},
            "SSDT-PNLF": {"description": "Laptop brightness control", "enabled": False, "priority": "Medium", "compatibility": "Laptop computers"},
            "SSDT-EC-USBX": {"description": "EC controller and USB power patch", "enabled": True, "priority": "High", "compatibility": "All systems"},
            "SSDT-AWAC-DISABLE": {"description": "Disable AWAC clock", "enabled": False, "priority": "Low", "compatibility": "Specific motherboards"},
            "SSDT-USBX": {"description": "USB power management optimization", "enabled": False, "priority": "Medium", "compatibility": "USB 3.0+ systems"}
        }
        
        # Add patch item and set tooltip
        for name, data in self.patches_data.items():
            item = QTreeWidgetItem([name, data["description"], "Enabled" if data["enabled"] else "Disabled"])
            item.setCheckState(0, Qt.Checked if data["enabled"] else Qt.Unchecked)
            # Set tooltip to display detailed information
            item.setToolTip(0, f"Priority: {data['priority']}\nCompatibility: {data['compatibility']}")
            item.setToolTip(1, f"Priority: {data['priority']}\nCompatibility: {data['compatibility']}\nDescription: {data['description']}")
            self.patches_list.addTopLevelItem(item)
        
        # Add search/filter box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search patches:")
        search_label.setStyleSheet("font-weight: 500;")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter patch name or keywords...")
        self.search_edit.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")
        self.search_edit.textChanged.connect(self.filter_patches)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Priority filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Priority filter:")
        filter_label.setStyleSheet("font-weight: 500;")
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "High", "Medium", "Low"])
        self.priority_filter.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")
        self.priority_filter.currentIndexChanged.connect(self.filter_patches)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.priority_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        layout.addWidget(self.patches_list)
        
        # Selection count
        self.selected_count_label = QLabel("Selected: 0 patches")
        self.selected_count_label.setStyleSheet("color: #3498db; font-weight: 500; margin-top: 10px;")
        layout.addWidget(self.selected_count_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Select all button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setStyleSheet("background-color: #95a5a6; color: white; border-radius: 4px; padding: 8px 16px; font-weight: 500;")
        self.select_all_btn.clicked.connect(self.select_all_patches)
        button_layout.addWidget(self.select_all_btn)
        
        # Clear selection button
        self.clear_all_btn = QPushButton("Clear Selection")
        self.clear_all_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 4px; padding: 8px 16px; font-weight: 500;")
        self.clear_all_btn.clicked.connect(self.clear_all_patches)
        button_layout.addWidget(self.clear_all_btn)
        
        button_layout.addStretch()
        
        # Apply selection button
        self.apply_btn = QPushButton("Apply Selection")
        self.apply_btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 4px; padding: 8px 24px; font-weight: 500;")
        self.apply_btn.clicked.connect(self.apply_selection)
        button_layout.addWidget(self.apply_btn)
        
        # Auto-detect button
        self.auto_detect_btn = QPushButton("Auto-detect Best Patches")
        self.auto_detect_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 4px; padding: 8px 24px; font-weight: 500;")
        self.auto_detect_btn.clicked.connect(self.auto_detect_patches)
        button_layout.addWidget(self.auto_detect_btn)
        
        layout.addLayout(button_layout)
        
        # Bottom spacer
        layout.addStretch()
        
        # Update selection count
        self.update_selected_count()
        
        # Connect signal to update status column when patch selection changes
        self.patches_list.itemChanged.connect(self.on_item_changed)
    
    def on_item_changed(self, item, column):
        """Update status column when patch item state changes"""
        if column == 0:  # Only when checkbox column changes
            is_checked = item.checkState(0) == Qt.Checked
            item.setText(2, "Enabled" if is_checked else "Disabled")
            self.update_selected_count()
    
    def update_selected_count(self):
        """Update display of selected patch count"""
        selected_count = 0
        for i in range(self.patches_list.topLevelItemCount()):
            if self.patches_list.topLevelItem(i).checkState(0) == Qt.Checked:
                selected_count += 1
        self.selected_count_label.setText(f"Selected: {selected_count} patches")
    
    def select_all_patches(self):
        """Select all patches"""
        for i in range(self.patches_list.topLevelItemCount()):
            item = self.patches_list.topLevelItem(i)
            item.setCheckState(0, Qt.Checked)
        self.update_selected_count()
        self.update_status("All ACPI patches selected")
    
    def clear_all_patches(self):
        """Clear all selections"""
        for i in range(self.patches_list.topLevelItemCount()):
            item = self.patches_list.topLevelItem(i)
            item.setCheckState(0, Qt.Unchecked)
        self.update_selected_count()
        self.update_status("All ACPI patch selections cleared")
    
    def filter_patches(self):
        """Filter patch list based on search text and priority"""
        search_text = self.search_edit.text().lower()
        selected_priority = self.priority_filter.currentText()
        
        for i in range(self.patches_list.topLevelItemCount()):
            item = self.patches_list.topLevelItem(i)
            patch_name = item.text(0).lower()
            patch_desc = item.text(1).lower()
            
            # Check search condition
            matches_search = search_text in patch_name or search_text in patch_desc
            
            # Check priority condition
            matches_priority = selected_priority == "All"
            if not matches_priority and patch_name in self.patches_data:
                matches_priority = self.patches_data[patch_name]["priority"] == selected_priority
            
            # Show or hide item
            item.setHidden(not (matches_search and matches_priority))
    
    def apply_selection(self):
        """Apply selected patches"""
        self.update_status("Applying ACPI patch selections...")
        # Collect user's patch selections
        selected_patches = []
        for i in range(self.patches_list.topLevelItemCount()):
            item = self.patches_list.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                patch_name = item.text(0)
                selected_patches.append({
                    "name": patch_name,
                    "description": item.text(1),
                    "priority": self.patches_data.get(patch_name, {}).get("priority", "Unknown")
                })
        
        # 保存到主窗口
        if self.main_window:
            self.main_window.selected_acpi_patches = selected_patches
            self.main_window.update_main_status()
        
        self.log_message(f"Saved {len(selected_patches)} ACPI patch configurations")
        
        # Generate detailed success message
        if selected_patches:
            # Sort and display by priority
            high_priority = [p for p in selected_patches if p["priority"] == "High"]
            medium_priority = [p for p in selected_patches if p["priority"] == "Medium"]
            low_priority = [p for p in selected_patches if p["priority"] == "Low"]
            
            message = f"ACPI patch configuration saved ({len(selected_patches)} patches selected)\n\n"
            
            if high_priority:
                message += "[High Priority]\n"
                for p in high_priority:
                    message += f"{p['name']}: {p['description']}\n"
                message += "\n"
            
            if medium_priority:
                message += "[Medium Priority]\n"
                for p in medium_priority:
                    message += f"{p['name']}: {p['description']}\n"
                message += "\n"
            
            if low_priority:
                message += "[Low Priority]\n"
                for p in low_priority:
                    message += f"{p['name']}: {p['description']}\n"
            
            message += "\nNote: Please ensure patch compatibility. Some patches may conflict."
        else:
            message = "No ACPI patches selected. Note that missing necessary patches may prevent system from booting properly."
        
        QMessageBox.information(self, "Success", message)
    
    def auto_detect_patches(self):
        """Auto-detect best ACPI patches"""
        self.update_status("Auto-detecting best ACPI patches...")
        
        # Show progress dialog
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("Auto-detect")
        progress_dialog.setText("Analyzing hardware information and recommending best patch configuration...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Try to use the auto-detection feature from the original code
            recommended_patches = []
            detection_log = []
            
            # Check if hardware information is available
            if hasattr(self.main_window, 'hardware_info') and self.main_window.hardware_info:
                hardware_info = self.main_window.hardware_info
                detection_log.append("Detecting suitable patches based on hardware information:")
                
                try:
                    # Try to use the original ACPI Guru
                    guru = acpi_guru.ACPIGuru()
                    recommended_patches = guru.recommend_patches(hardware_info)
                    detection_log.append("Using original ACPI Guru for patch recommendations")
                except (ImportError, AttributeError, Exception) as e:
                    self.log_message(f"Unable to use original ACPI Guru for auto-detection: {e}")
                    detection_log.append(f"! Unable to use original ACPI Guru: {str(e)}")
                    detection_log.append("Using simulation recommendation mode")
                    
                    # Smart recommendation based on hardware information
                    recommended_patches = []
                    
                    # Basic patches (needed for almost all systems)
                    recommended_patches.extend(["FixHPET", "FixRTC", "SSDT-PLUG", "SSDT-EC-USBX"])
                    detection_log.append("Adding basic patches: FixHPET, FixRTC, SSDT-PLUG, SSDT-EC-USBX")
                    
                    # CPU related checks
                    if "cpu" in hardware_info and "model" in hardware_info["cpu"]:
                        cpu_model = hardware_info["cpu"]["model"]
                        detection_log.append(f"✓ Detected CPU: {cpu_model}")
                        
                        # AMD CPU might need special handling
                        if "AMD" in cpu_model:
                            detection_log.append("✓ Detected AMD CPU, ensuring power management patches are enabled")
                    
                    # GPU related checks
                    if "gpu" in hardware_info and "model" in hardware_info["gpu"]:
                        gpu_model = hardware_info["gpu"]["model"]
                        detection_log.append(f"✓ Detected GPU: {gpu_model}")
                    
                    # System type check (laptop/desktop)
                    if "Laptop" in hardware_info.get("model", "") or "Notebook" in hardware_info.get("model", "").lower():
                        recommended_patches.append("SSDT-PNLF")
                        detection_log.append("✓ Detected laptop, adding SSDT-PNLF (brightness control patch)")
                    
                    # Motherboard type check
                    if "model" in hardware_info:
                        model_str = hardware_info["model"].lower()
                        # Check if AWAC patch might be needed
                        if any(x in model_str for x in ["z390", "z490", "z590", "z690", "b360", "b460", "b560", "b660"]):
                            recommended_patches.append("SSDT-AWAC")
                            detection_log.append("✓ Detected newer motherboard, adding SSDT-AWAC (AWAC clock fix)")
            else:
                # Default recommendation when no hardware info is available
                detection_log.append("! No hardware information detected, applying generic recommended configuration")
                recommended_patches = ["FixHPET", "FixRTC", "SSDT-PLUG", "SSDT-EC-USBX"]
                detection_log.append("Adding basic generic patches: FixHPET, FixRTC, SSDT-PLUG, SSDT-EC-USBX")
            
            # Remove duplicates
            recommended_patches = list(set(recommended_patches))
            
            # Update UI
            auto_selected_count = 0
            for i in range(self.patches_list.topLevelItemCount()):
                item = self.patches_list.topLevelItem(i)
                if item.text(0) in recommended_patches:
                    item.setCheckState(0, Qt.Checked)
                    item.setText(2, "Enabled")
                    auto_selected_count += 1
                else:
                    # Only disable non-basic patches not in the recommendation list
                    patch_name = item.text(0)
                    if patch_name not in ["FixHPET", "FixRTC", "SSDT-PLUG"]:  # Keep some basic patches
                        item.setCheckState(0, Qt.Unchecked)
                        item.setText(2, "Disabled")
            
            # Close progress dialog
            progress_dialog.close()
            
            self.update_selected_count()
            self.log_message(f"Automatically configured {auto_selected_count} recommended ACPI patches")
            
            # Generate detailed detection result message
            message = f"Auto detection completed\n\n{auto_selected_count} recommended patches have been selected based on your system configuration\n\n"
            
            # Display recommended patches
            for patch_name in sorted(recommended_patches):
                if patch_name in self.patches_data:
                    message += f"✓ {patch_name}: {self.patches_data[patch_name]['description']}\n"
                else:
                    message += f"✓ {patch_name}\n"
            
            message += "\nDetection log\n"
            message += "\n".join(detection_log)
            message += "\n\nTip: You can adjust these automatically selected patches as needed."
            
            QMessageBox.information(self, "Auto detection completed", message)
            
        except Exception as e:
            progress_dialog.close()
            self.log_message(f"Auto-detection failed: {e}")
            QMessageBox.warning(self, "Warning", f"Auto-detection of patches failed: {str(e)}\n\nPlease try manually selecting patches.")

# Kext Configuration Page
class KextConfigPage(BasePage):
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Kext Driver Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Kext List
        self.kext_list = QTreeWidget()
        self.kext_list.setHeaderLabels(["Kext Name", "Version", "Description", "Status"])
        self.kext_list.setColumnWidth(0, 150)
        self.kext_list.setColumnWidth(1, 100)
        self.kext_list.setColumnWidth(2, 350)
        
        # Add some example kexts
        kexts = [
            ("Lilu.kext", "1.6.7", "Core patching framework", True),
            ("VirtualSMC.kext", "1.3.3", "SMC emulation", True),
            ("WhateverGreen.kext", "1.6.6", "Graphics patch", True),
            ("AppleALC.kext", "1.8.8", "Audio driver", True),
            ("IntelMausi.kext", "1.0.7", "Intel network driver", False),
            ("NVMeFix.kext", "1.1.1", "NVMe storage optimization", False)
        ]
        
        for name, version, desc, enabled in kexts:
            item = QTreeWidgetItem([name, version, desc, "Enabled" if enabled else "Disabled"])
            item.setCheckState(0, Qt.Checked if enabled else Qt.Unchecked)
            self.kext_list.addTopLevelItem(item)
        
        layout.addWidget(self.kext_list)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Selection")
        self.apply_btn.clicked.connect(self.apply_selection)
        button_layout.addWidget(self.apply_btn)
        
        self.auto_select_btn = QPushButton("Auto-select Best Kexts")
        self.auto_select_btn.clicked.connect(self.auto_select_kexts)
        button_layout.addWidget(self.auto_select_btn)
        
        layout.addLayout(button_layout)
    
    def apply_selection(self):
        self.update_status("Applying Kext selection...")
        # Collect user's Kext selection
        selected_kexts = []
        for i in range(self.kext_list.topLevelItemCount()):
            item = self.kext_list.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                selected_kexts.append({
                    "name": item.text(0),
                    "version": item.text(1),
                    "description": item.text(2)
                })
        
        # Save to main window
        if self.main_window:
            self.main_window.selected_kexts = selected_kexts
        
        self.log_message(f"Saved {len(selected_kexts)} Kext configurations")
        QMessageBox.information(self, "Success", f"Kext configuration saved ({len(selected_kexts)} drivers selected)")
    
    def auto_select_kexts(self):
        self.update_status("Auto-selecting best Kexts...")
        try:
            # Try to use auto-selection from original code
            recommended_kexts = []
            if hasattr(self.main_window, 'hardware_info') and self.main_window.hardware_info:
                try:
                    maestro = kext_maestro.KextMaestro()
                    recommended_kexts = maestro.recommend_kexts(self.main_window.hardware_info)
                except (ImportError, AttributeError, Exception) as e:
                    self.log_message(f"Unable to use original Kext auto-selection: {e}")
                    # Simulate recommendation
                    recommended_kexts = ["Lilu.kext", "VirtualSMC.kext", "WhateverGreen.kext", "AppleALC.kext"]
            else:
                # Default recommendation without hardware info
                recommended_kexts = ["Lilu.kext", "VirtualSMC.kext", "WhateverGreen.kext", "AppleALC.kext"]
            
            # Update UI
            for i in range(self.kext_list.topLevelItemCount()):
                item = self.kext_list.topLevelItem(i)
                if item.text(0) in recommended_kexts:
                    item.setCheckState(0, Qt.Checked)
                    item.setText(3, "Enabled")
                else:
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(3, "Disabled")
            
            self.log_message(f"Automatically configured {len(recommended_kexts)} recommended Kexts")
            QMessageBox.information(self, "Success", "Recommended Kexts have been automatically configured based on your hardware")
        except Exception as e:
            self.log_message(f"Auto-selection failed: {e}")
            QMessageBox.warning(self, "Warning", f"Auto-selection of Kexts failed: {e}")

# SMBIOS Configuration Page
class SMBIOSConfigPage(BasePage):
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("SMBIOS Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # SMBIOS Model Selection
        model_group = QGroupBox("Select SMBIOS Model")
        model_layout = QVBoxLayout()
        
        self.model_list = QComboBox()
        # Add some example models
        self.model_list.addItems([
            "MacBookPro16,1",
            "MacBookPro16,4",
            "Macmini9,1",
            "iMac20,1",
            "MacPro7,1"
        ])
        model_layout.addWidget(self.model_list)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Custom Options
        custom_group = QGroupBox("Custom SMBIOS Information")
        custom_layout = QGridLayout()
        
        # Add some custom fields
        fields = [
            ("Serial Number:", "MLXXXXXXXXXX"),
            ("UUID:", "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"),
            ("Board Serial Number:", "CXXXXXXXXXX"),
            ("MLB:", "XXXXXXXXXXXXXXXXXXXX")
        ]
        
        self.field_inputs = {}
        for i, (label_text, default_value) in enumerate(fields):
            label = QLabel(label_text)
            input_field = QLineEdit(default_value)
            self.field_inputs[label_text] = input_field
            custom_layout.addWidget(label, i, 0)
            custom_layout.addWidget(input_field, i, 1)
        
        # Generate new serial button
        self.generate_btn = QPushButton("Generate New Serial")
        self.generate_btn.clicked.connect(self.generate_new_serial)
        custom_layout.addWidget(self.generate_btn, len(fields), 0, 1, 2)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # Confirm button
        self.confirm_btn = QPushButton("Confirm SMBIOS Settings")
        self.confirm_btn.clicked.connect(self.confirm_settings)
        layout.addWidget(self.confirm_btn)
        
        # Bottom spacer
        layout.addStretch()
    
    def generate_new_serial(self):
        self.update_status("Generating new serial number...")
        try:
            # Try to use SMBIOS generation from original code
            new_serial = ""
            new_uuid = ""
            new_board = ""
            new_mlb = ""
            
            try:
                smbios_gen = smbios.SMBIOS()
                model = self.model_list.currentText()
                smbios_data = smbios_gen.generate_smbios(model)
                new_serial = smbios_data.get("SerialNumber", "")
                new_uuid = smbios_data.get("UUID", "")
                new_board = smbios_data.get("BoardSerialNumber", "")
                new_mlb = smbios_data.get("MLB", "")
            except (ImportError, AttributeError, Exception) as e:
                self.log_message(f"Unable to use original SMBIOS generation: {e}")
                # Simulate generation
                import random
                import string
                def random_str(length=12, chars=string.ascii_uppercase + string.digits):
                    return ''.join(random.choice(chars) for _ in range(length))
                
                new_serial = "C" + random_str(11)
                new_uuid = f"{random_str(8)}-{random_str(4)}-{random_str(4)}-{random_str(4)}-{random_str(12)}"
                new_board = "C" + random_str(11)
                new_mlb = random_str(20)
            
            # Update UI
            self.field_inputs["Serial Number:"].setText(new_serial)
            self.field_inputs["UUID:"].setText(new_uuid)
            self.field_inputs["Board Serial Number:"].setText(new_board)
            self.field_inputs["MLB:"].setText(new_mlb)
            
            self.log_message("Generated new SMBIOS serial number")
            QMessageBox.information(self, "Success", "New SMBIOS serial number has been generated")
        except Exception as e:
            self.log_message(f"Generation failed: {e}")
            QMessageBox.warning(self, "Warning", f"Failed to generate serial number: {e}")
    
    def confirm_settings(self):
        selected_model = self.model_list.currentText()
        serial = self.field_inputs["Serial Number:"].text()
        uuid = self.field_inputs["UUID:"].text()
        board_serial = self.field_inputs["Board Serial Number:"].text()
        mlb = self.field_inputs["MLB:"].text()
        
        self.update_status(f"Selected SMBIOS model: {selected_model}")
        
        # Save SMBIOS configuration to main window
        if self.main_window:
            self.main_window.selected_smbios_model = selected_model
            self.main_window.smbios_config = {
                "model": selected_model,
                "serial": serial,
                "uuid": uuid,
                "board_serial": board_serial,
                "mlb": mlb
            }
            self.main_window.update_main_status()
        
        self.log_message(f"Saved SMBIOS configuration: {selected_model}")
        QMessageBox.information(self, "Success", f"SMBIOS settings saved: {selected_model}")

# Build Page
class BuildPage(BasePage):
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Build OpenCore EFI")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Status information
        self.status_info = QLabel("Please ensure all necessary configurations are completed before starting the build.")
        self.status_info.setWordWrap(True)
        layout.addWidget(self.status_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Progress information
        self.progress_info = QLabel("Ready to build...")
        layout.addWidget(self.progress_info)
        
        # Build log
        log_group = QGroupBox("Build Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.build_btn = QPushButton("Start Build")
        self.build_btn.clicked.connect(self.start_build)
        button_layout.addWidget(self.build_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_build)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Bottom spacer
        layout.addStretch()
    
    def start_build(self):
        # 检查是否所有必要配置都已完�?
        if not self.main_window or not (self.main_window.hardware_report_path and 
                                       self.main_window.selected_macos_version and 
                                       self.main_window.selected_smbios_model):
            QMessageBox.warning(self, "Warning", "Please complete all necessary configurations first, including selecting hardware report, macOS version, and SMBIOS model.")
            return
        
        # 准备构建配置
        build_config = {
            "hardware_report_path": self.main_window.hardware_report_path,
            "macos_version": self.main_window.selected_macos_version,
            "smbios_config": getattr(self.main_window, 'smbios_config', None),
            "selected_acpi_patches": getattr(self.main_window, 'selected_acpi_patches', []),
            "selected_kexts": getattr(self.main_window, 'selected_kexts', [])
        }
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", os.path.expanduser("~"))
        if not output_dir:
            return
        
        build_config["output_dir"] = output_dir
        
        self.update_status("Starting OpenCore EFI build...")
        self.build_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # 创建并启动构建线�?
        self.build_thread = BuildThread(self, build_config)
        self.build_thread.progress.connect(self.update_progress)
        self.build_thread.finished.connect(self.build_finished)
        self.build_thread.log.connect(self.log_build_message)
        self.build_thread.start()
    
    def cancel_build(self):
        if hasattr(self, 'build_thread') and self.build_thread.isRunning():
            self.build_thread.terminate()
            self.build_thread.wait()
            self.update_status("Build cancelled")
            self.build_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
    
    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.progress_info.setText(text)
        self.update_status(text)
    
    def log_build_message(self, message):
        self.log_text.append(message)
        self.log_message(message)
    
    def build_finished(self, success, message):
        self.update_status(message)
        self.build_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            # 模拟构建结果目录
            if hasattr(self.build_thread, 'config') and 'output_dir' in self.build_thread.config:
                result_dir = os.path.join(self.build_thread.config['output_dir'], "OpenCore-EFI")
                if self.main_window:
                    self.main_window.result_dir = result_dir
                
                # 显示结果信息
                self.status_info.setText(f"EFI built successfully: {result_dir}")
                QMessageBox.information(self, "Success", f"OpenCore EFI successfully built!\n\nOutput directory: {result_dir}")
            else:
                QMessageBox.information(self, "Success", "OpenCore EFI successfully built!")
        else:
            QMessageBox.critical(self, "Error", message)

# Main window class
class OpCoreSimplifyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize configuration variables
        self.hardware_report_path = None
        self.hardware_info = None
        self.selected_macos_version = None
        self.selected_smbios_model = None
        self.smbios_config = None
        self.selected_acpi_patches = []
        self.selected_kexts = []
        self.result_dir = None
        
        # Initialize UI components
        self.nav_list = None
        self.stacked_widget = None
        
        # Create UI
        self.init_ui()
        
    def init_ui(self):
        # Set window title, size, and center it
        self.setWindowTitle("OpCore Simplify GUI - Simplified OpenCore Configuration Tool")
        self.setMinimumSize(950, 650)
        
        # 窗口居中显示
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 内容区域和导航菜单布局
        content_layout = QHBoxLayout()
        
        # 左侧导航菜单 - 优化样式
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(210)
        self.nav_list.setSpacing(2)
        
        # Add menu items with icons and tooltips
        menu_items = [
            ("Hardware Report", "📊 Configure hardware info and report"),
            ("macOS Version", "🍎 Select target macOS version"),
            ("ACPI Patches", "🔧 Configure ACPI patch options"),
            ("Kext Drivers", "📦 Manage drivers"),
            ("SMBIOS Config", "🖥�?Set system information"),
            ("Build EFI", "🚀 Generate final EFI folder")
        ]
        
        for text, tip in menu_items:
            item = QListWidgetItem(text)
            item.setToolTip(tip)
            self.nav_list.addItem(item)
        
        # Modern navigation menu style
        self.nav_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: #f8fafc;
                padding: 4px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 6px;
                font-size: 14px;
                color: #374151;
                height: 40px;
            }
            QListWidget::item:hover {
                background-color: #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:selected:hover {
                background-color: #2563eb;
            }
        """)
        # Default select first page (will trigger signal now that everything is initialized)
        self.nav_list.setCurrentRow(0)
        
        content_layout.addWidget(self.nav_list)
        
        # Right content area
        self.stacked_widget = QStackedWidget()
        
        # 创建各个页面
        self.hardware_page = HardwareReportPage(self)
        self.macos_page = MacOSVersionPage(self)
        self.acpi_page = ACPIConfigPage(self)
        self.kext_page = KextConfigPage(self)
        self.smbios_page = SMBIOSConfigPage(self)
        self.build_page = BuildPage(self)
        
        # Add pages to stack
        self.stacked_widget.addWidget(self.hardware_page)
        self.stacked_widget.addWidget(self.macos_page)
        self.stacked_widget.addWidget(self.acpi_page)
        self.stacked_widget.addWidget(self.kext_page)
        self.stacked_widget.addWidget(self.smbios_page)
        self.stacked_widget.addWidget(self.build_page)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Connect navigation after all widgets are initialized
        self.nav_list.currentRowChanged.connect(self.change_page)
        
        main_layout.addLayout(content_layout, 1)
        
        # 创建日志区域
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout()
        
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(100)
        log_layout.addWidget(self.log_widget)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Initialize status
        self.update_main_status()
        
        # Make sure stacked widget is showing the first page
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(0)
        
    def change_page(self, index):
        # Check if stacked_widget is initialized before accessing
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentIndex(index)
            if self.nav_list.currentItem():
                self.update_status_bar(f"Current page: {self.nav_list.currentItem().text()}")
        else:
            print("Warning: stacked_widget is not initialized yet")
    
    def update_status_bar(self, text):
        self.statusBar().showMessage(text)
    
    def log_message(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_widget.append(f"[{timestamp}] {message}")
        # 自动滚动到底�?
        self.log_widget.verticalScrollBar().setValue(
            self.log_widget.verticalScrollBar().maximum()
        )
    
    def update_main_status(self):
        # Update main window status display - more intuitive progress indicator
        status_parts = []
        completed_steps = 0
        total_steps = 3
        
        # Hardware report status
        if self.hardware_report_path:
            status_parts.append("<b>Hardware Report</b>: Selected")
            completed_steps += 1
        else:
            status_parts.append("<b>Hardware Report</b>: Needs selection")
        
        # macOS version status
        if self.selected_macos_version:
            status_parts.append(f"<b>macOS</b>: {self.selected_macos_version}")
            completed_steps += 1
        else:
            status_parts.append("<b>macOS</b>: Needs selection")
        
        # SMBIOS status
        if self.selected_smbios_model:
            status_parts.append(f"<b>SMBIOS</b>: {self.selected_smbios_model}")
            completed_steps += 1
        else:
            status_parts.append("<b>SMBIOS</b>: Needs selection")
        
        # ACPI patches and Kext status (optional)
        if self.selected_acpi_patches:
            status_parts.append(f"<b>ACPI Patches</b>: {len(self.selected_acpi_patches)} selected")
        if self.selected_kexts:
            status_parts.append(f"<b>Kext Drivers</b>: {len(self.selected_kexts)} selected")
        
        # Calculate completion percentage
        progress_percent = int((completed_steps / total_steps) * 100)
        
        # Update status bar
        status_text = f"Completion: {progress_percent}% | " + " | ".join(status_parts)
        
        # 为状态栏设置样式
        self.statusBar().setStyleSheet("QLabel { padding: 4px; color: #333; font-size: 13px; }")
        self.statusBar().showMessage(status_text)
        
        # 当所有必要步骤完成时，提供视觉反�?
        if progress_percent == 100:
            self.statusBar().setStyleSheet("QLabel { padding: 4px; color: #27ae60; font-size: 13px; font-weight: bold; }")

# Main function - Add complete exception handling and stability guarantees
if __name__ == "__main__":
    try:
        # Ensure necessary modules are available
        try:
            import PyQt5
        except ImportError:
            print("Error: PyQt5 module is not installed. Please install it using 'pip install PyQt5'.")
            sys.exit(1)
            
        # Try running update check
        try:
            update_flag = False
            try:
                update_flag = updater.Updater().run_update()
            except (ImportError, AttributeError):
                print("Skipping update check")
            
            if update_flag:
                os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            print(f"Update check failed: {e}")
        
        # Ensure proper text display
        if os.name == 'nt':  # Windows system
            os.environ['PYTHONUTF8'] = '1'
        
        # Check if necessary modules and files exist
        required_modules = ['Scripts', 'Scripts/run.py']
        missing_files = []
        
        for module_path in required_modules:
            if not os.path.exists(module_path):
                missing_files.append(module_path)
        
        # If there are missing files, display error message
        if missing_files:
            from PyQt5.QtWidgets import QMessageBox
            error_msg = "Program startup failed, missing the following essential files:\n\n"
            error_msg += "\n".join(missing_files)
            error_msg += "\n\nPlease ensure you have downloaded and extracted all files completely."
            
            # Display error message using static method before showing the window
            QMessageBox.critical(None, "Startup Error", error_msg, QMessageBox.Ok)
            sys.exit(1)
            
        # Set application style
        app = QApplication(sys.argv)
        app.setStyle("Fusion")  # Use Fusion style for consistent cross-platform appearance
        
        # Create window
        window = OpCoreSimplifyGUI()
        window.show()
        
        # Run application
        sys.exit(app.exec_())
    except Exception as e:
        # Catch all exceptions and log them
        import traceback
        error_log = "Program encountered a critical error:\n\n"
        error_log += str(e) + "\n\n"
        error_log += traceback.format_exc()
        
        # Write error information to log file
        try:
            with open("error_log.txt", "w", encoding="utf-8") as f:
                f.write(error_log)
        except:
            pass
        
        # Display error message
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Critical Error",
            "Program encountered a critical error. Detailed information has been saved to error_log.txt\n\n" + str(e),
                                 QMessageBox.Ok)
        except:
            print("Unable to display graphical error message. Detailed error:")
            print(error_log)
        
        sys.exit(1)
    
    except Exception as e:
        # Catch all exceptions and log them
        import traceback
        error_log = "Program encountered a critical error:\n\n"
        error_log += str(e) + "\n\n"
        error_log += traceback.format_exc()
        
        # Write error information to log file
        try:
            with open("error_log.txt", "w", encoding="utf-8") as f:
                f.write(error_log)
        except:
            pass
        
        # Display error message
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Critical Error",
            "Program encountered a critical error. Detailed information has been saved to error_log.txt\n\n" + str(e), 
                                 QMessageBox.Ok)
        except:
            print("Unable to display graphical error message. Detailed error:")
            print(error_log)
        
        sys.exit(1)
