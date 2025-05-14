import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox  # QMessageBox 추가
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from serial_port_selector import SerialPortSelector
import serial

# UI 파일 경로 설정
ui_file_path = os.path.join(os.path.dirname(__file__), "res", "mainWindow.ui")

try:
    form_mainWin = uic.loadUiType(ui_file_path)[0]
except FileNotFoundError:
    print(f"Error: UI file not found at {ui_file_path}")
    sys.exit(1)

class MyWindow(QMainWindow, form_mainWin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 실행 플래그 초기화
        self.motion_ready = False

        # 버튼 메뉴 연결
        self.pushButton_6.clicked.connect(self.open_port_selector)
        self.pushButton_1.clicked.connect(lambda: self.exeHumanoidMotion(22)) # lambda 사용 하는 것은 함수의 실행을 지연 
        self.pushButton_2.clicked.connect(lambda: self.exeHumanoidMotion(24)) # 즉 씨리얼 포트가 선택 되지 않은 상태에서        
        self.pushButton_3.clicked.connect(lambda: self.exeHumanoidMotion(25)) # 버튼 클릭 시 실행되는 함수에서 생기는 문제를 방지   
        self.pushButton_4.clicked.connect(lambda: self.exeHumanoidMotion(29))
        self.pushButton_5.clicked.connect(lambda: self.exeHumanoidMotion(28))

        # 메뉴 액션 연결
        self.actionSerial_Port.triggered.connect(self.open_port_selector)

        # 이미지 로드
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "res", "humanoid.png"))
        self.label.setPixmap(pixmap)

    def exeHumanoidMotion(self, motion_id):
        if not self.motion_ready:
            QMessageBox.warning(self, "Motion Error", "Motion is not ready. Please select a port first.")
            return

        # 모션 제어 기본 패킷 생성
        packet_buff = [0xff, 0xff, 0x4c, 0x53,  # 헤더
                       0x00, 0x00, 0x00, 0x00,  # Destination ADD, Source ADD
                       0x30, 0x0c, 0x03,        # 0x30 실행 명령어 0x0c 모션실행 0x03 파라메타 길이
                       motion_id, 0x00, 0x64,   # 모션 ID, 모션 반복, 모션 속도 지정
                       0x00]                    # 체크섬

        # 체크섬 계산
        checksum = 0
        for i in range(6, 14):
            checksum += packet_buff[i]
        packet_buff[14] = checksum

        # 시리얼 포트 열기
        try:
            ser = serial.Serial(self.lblPort.text(), 115200, timeout=1)
            if ser.is_open:
                # 패킷 전송
                ser.write(packet_buff)
            else:
                raise serial.SerialException(f"Failed to open serial port {self.lblPort.text()}.")
        except serial.SerialException as e:
            # 경고 메시지 박스 표시
            QMessageBox.warning(self, "Serial Port Error", str(e))
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

    def open_port_selector(self):
        selected_port = SerialPortSelector.launch(self)
        if selected_port:
            print("선택한 포트:", selected_port)
            self.lblPort.setText(selected_port)
            # 포트가 선택되면 플래그 활성화
            self.motion_ready = True
    

# PyQt 애플리케이션 초기화
app = QApplication(sys.argv)

# 메인 윈도우 생성
window = MyWindow()
window.show()

# 애플리케이션 실행
sys.exit(app.exec_())
