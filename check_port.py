import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

print("--- 현재 연결된 포트 목록 ---")
for p in ports:
    print(f"포트: {p.device} / 설명: {p.description}")
