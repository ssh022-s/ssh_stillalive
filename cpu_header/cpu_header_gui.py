import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget,
                           QScrollArea, QFormLayout, QGroupBox, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import binascii
from datetime import datetime
import os

def cpu_pkt_field_len():
    fromcpuhder_len = {
        'isRep': 1, 'destMap': 12, 'headerHash': 18, 'hwFwd': 1, 
        'ingressTsNs': 30, 'reserve0': 2, 'opCode': 3,
        'nextHopId': 14, 'ptpProfileId': 4, 'ptpEn': 1, 
        'priority': 6, 'learningDisable': 1,
        'forceDestination': 1, 'criticalPacket': 1, 'forbidEdit': 1, 
        'reserve1': 24
    }
    return fromcpuhder_len

def cpu_pkt_field():
    """default field"""
    From_cpuHeader_field = {
        'isRep': '0',  # 1bit 0
        'destMap': '000000000000',  # 12bit   12:1
        'headerHash': '000000000000000000',  # 18bit    30:13
        'hwFwd': '0',  # 1bit     31
        'ingressTsNs': '000000000000000000000000000000',  # 30bit 29:0
        'reserve0': '00',  # 3bit 29:31
        'opCode': '000',  # 3bit 2:0
        'nextHopId': '00000000000000',  # 14bit    16:3
        'ptpProfileId': '0000',  # 4bit 20:17
        'ptpEn': '0',  # 1bit 21
        'priorityT': '000000',  # 6bit 27:22
        'learningDisable': '0',  # 1bit 28
        'forceDestination': '0',  # 1bit 29
        'criticalPacket': '0',  # 1bit 30
        'forbidEdit': '0',  # 1bit 31
        'reserve1': '000000000000000000000000'  # 24bit 24:0
    }
    return From_cpuHeader_field

def cal_crc(data):
    crc = data
    poly = 0x07
    for i in range(8, 0, -1):
        if ((crc & 0x80) >> 7) == 1:
            crc = (crc << 1) ^ poly
        else:
            crc = (crc << 1)
    return crc & 0xFF

def cal_crc8(datas):
    length = len(datas)
    crc = 0x00
    for i in range(length):
        if i == 0:
            crc = cal_crc(datas[0])
        else:
            crc = (crc ^ datas[i]) & 0xFF
            crc = cal_crc(crc)
    return crc & 0xFF

class CPUHeaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Header Tool")
        self.setMinimumSize(1000, 800)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set the style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget {
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #ddd;
                border-bottom: none;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: Consolas, Monaco, monospace;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 24px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Create tabs
        self.create_decode_tab(tabs)
        self.create_encode_tab(tabs)

    def create_decode_tab(self, tabs):
        decode_tab = QWidget()
        layout = QVBoxLayout(decode_tab)

        # Input section
        input_group = QGroupBox("Input CPU Header (hex format)")
        input_layout = QVBoxLayout()
        
        self.header_input = QLineEdit()
        self.header_input.setPlaceholderText("Enter CPU header hex string (space-separated)")
        input_layout.addWidget(self.header_input)

        decode_btn = QPushButton("Decode Header")
        decode_btn.clicked.connect(self.decode_header)
        input_layout.addWidget(decode_btn)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Output section
        output_group = QGroupBox("Decoded Fields")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        tabs.addTab(decode_tab, "Decode CPU Header")

    def create_encode_tab(self, tabs):
        encode_tab = QWidget()
        
        # Create a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(encode_tab)
        
        layout = QVBoxLayout(encode_tab)
        
        # Create form layout for fields
        form_layout = QFormLayout()
        self.field_inputs = {}
        
        # Add all fields except CRC
        field_lengths = cpu_pkt_field_len()
        for field, length in field_lengths.items():
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter {field} value (max {2**length-1})")
            self.field_inputs[field] = line_edit
            form_layout.addRow(f"{field} ({length} bits):", line_edit)
        
        layout.addLayout(form_layout)

        # Add encode button
        encode_btn = QPushButton("Generate Header")
        encode_btn.clicked.connect(self.encode_header)
        layout.addWidget(encode_btn)

        # Add output field
        self.encode_output = QTextEdit()
        self.encode_output.setReadOnly(True)
        layout.addWidget(QLabel("Generated Header (hex):"))
        layout.addWidget(self.encode_output)

        tabs.addTab(scroll, "Generate CPU Header")

    def decode_header(self):
        try:
            header_hex = self.header_input.text().strip()
            cpuHeader = header_hex.replace(' ', '')
            
            # 检查输入长度 - CPU Header 应该是 24 字节 (48 十六进制字符)
            expected_length = 48  # 24 字节 × 2 字符/字节
            if len(cpuHeader) != expected_length:
                self.output_text.setText(f"错误: 输入的 CPU Header 长度不正确。\n"
                                       f"预期长度: {expected_length} 个十六进制字符 (24 字节)\n"
                                       f"实际长度: {len(cpuHeader)} 个十六进制字符")
                # 显示错误对话框
                QMessageBox.warning(self, "输入错误", 
                                  f"CPU Header 长度不正确。\n预期: {expected_length} 个字符 (24 字节)\n实际: {len(cpuHeader)} 个字符",
                                  QMessageBox.Ok)
                return
                
            # 检查是否都是有效的十六进制字符
            try:
                int(cpuHeader, 16)
            except ValueError:
                self.output_text.setText("错误: 输入包含无效的十六进制字符。")
                QMessageBox.warning(self, "输入错误", "输入包含无效的十六进制字符。", QMessageBox.Ok)
                return
                
            temp = bin(int(cpuHeader, 16))[2:]
            
            # 确保二进制字符串长度正确
            while len(temp) < 192:
                temp = '0' + temp
                
            tempS = temp[-8:] + temp[-16:-8] + temp[-24:-16] + temp[-32:-24]
            crcs = int(tempS[-32:-24], 2)
            reserve4 = int(tempS[-24:-1], 2)

            tempS = temp[-40:-32] + temp[-48:-40] + temp[-56:-48] + temp[-64:-56]
            packetLength = int(tempS[-13:], 2)
            reserve3 = int(tempS[-32:-14], 2)

            tempS = temp[-72:-64] + temp[-80:-72] + temp[-88:-80] + temp[-96:-88]
            outerIsCvlan = int(tempS[-1:], 2)
            srcVlanId = int(tempS[-12:-1], 2)
            srcTagCfi = int(tempS[-13:-12], 2)
            srcTagCos = int(tempS[-16:-14], 2)
            exceptionEn = int(tempS[-17:-16], 2)
            exceptionIndex = int(tempS[-25:-18], 2)
            reserve2 = int(tempS[-32:-26], 2)

            tempS = temp[-104:-96] + temp[-112:-104] + temp[-120:-112] + temp[-128:-120]
            srcPort = int(tempS[-5:], 2)
            truncated = int(tempS[-6:-5], 2)
            priority = int(tempS[-12:-6], 2)
            reserve1 = int(tempS[-20:-12], 2)
            fid = int(tempS[-32:-20], 2)

            tempS = int(temp[-136:-128] + temp[-144:-136] + temp[-152:-144] + temp[-160:-152], 2)
            timestampS = datetime.fromtimestamp(tempS)

            timestampNs = int(temp[-166:-160] + temp[-176:-168] + temp[-184:-176] + temp[-192:-184], 2)
            reserve0 = int(temp[-168:-166], 2)

            # Format output
            output = "Decoded CPU Header Fields:\n\n"
            fields = {
                'Timestamp (ns)': timestampNs,
                'Reserve0': reserve0,
                'Timestamp': f"{timestampS} ({tempS})",
                'Source Port': srcPort,
                'Truncated': truncated,
                'Priority': priority,
                'Reserve1': reserve1,
                'FID': fid,
                'Outer Is CVLAN': outerIsCvlan,
                'Source VLAN ID': srcVlanId,
                'Source Tag CFI': srcTagCfi,
                'Source Tag CoS': srcTagCos,
                'Exception Enable': exceptionEn,
                'Exception Index': exceptionIndex,
                'Reserve2': reserve2,
                'Packet Length': packetLength,
                'Reserve3': reserve3,
                'Reserve4': reserve4,
                'CRC': crcs
            }

            for field, value in fields.items():
                output += f"{field}: {value}\n"
            
            self.output_text.setText(output)
        except Exception as e:
            self.output_text.setText(f"Error: {str(e)}")

    def encode_header(self):
        try:
            # Collect values from input fields
            FromCPUHeader_dicts = {}
            for field, input_widget in self.field_inputs.items():
                value = input_widget.text().strip()
                if value:  # Only add non-empty values
                    FromCPUHeader_dicts[field] = int(value)

            if bool(FromCPUHeader_dicts):
                cpu_pkt = cpu_pkt_field()
                fromCpuHerder_length = cpu_pkt_field_len()
                _from_cpu_dict = {}

                # Process input fields
                for k, v in FromCPUHeader_dicts.items():
                    input_field = bin(v)[2:]
                    if k in fromCpuHerder_length:
                        if len(input_field) < fromCpuHerder_length[k]:
                            realLength = fromCpuHerder_length[k] - len(input_field)
                            _final_input_field = '0' * realLength + input_field
                            _from_cpu_dict.update({k: _final_input_field})
                        elif len(input_field) == fromCpuHerder_length[k]:
                            _from_cpu_dict.update({k: input_field})
                        else:
                            raise ValueError(f"{k}: {v} length error")
                    else:
                        raise ValueError(f"{k}: {v} key error")

                # Build binary string
                new_str = ""
                for ks, vs in cpu_pkt.items():
                    new_str += _from_cpu_dict.get(ks, cpu_pkt[ks])[::-1]

                # Convert to bytes and calculate CRC
                b_list = []
                groups = [new_str[i:i+8] for i in range(0, len(new_str), 8)]
                reversed_groups = [group[::-1] for group in groups]
                hex_str = ""
                
                for binary_string in reversed_groups:
                    tmp = f'{int(binary_string, 2):02x}'
                    b_list.append(int(tmp, 16))
                    hex_str += tmp

                final_str = hex_str + hex(cal_crc8(b_list))[2:].zfill(2)
                formatted_result = ' '.join(final_str[i:i+2] for i in range(0, len(final_str), 2))
                self.encode_output.setText(formatted_result.upper())
            else:
                self.encode_output.setText("Error: No values provided")
            
        except Exception as e:
            self.encode_output.setText(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CPUHeaderGUI()
    window.show()
    sys.exit(app.exec_()) 