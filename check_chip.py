import serial.tools.list_ports

def check_chip_type():
    ports = serial.tools.list_ports.comports()
    
    print(f"{'PORT':<10} {'VID:PID':<15} {'CHIP TYPE GUESS'}")
    print("-" * 50)

    found = False
    for port in ports:
        # VID와 PID가 없는 경우(가상 포트 등)는 건너뜀
        if port.vid is None or port.pid is None:
            continue
            
        found = True
        vid_hex = hex(port.vid)
        pid_hex = hex(port.pid)
        chip_name = "Unknown"

        # 1. CH340 계열 (중국 WCH사)
        if port.vid == 0x1A86: 
            chip_name = "CH340 (저가형 호환 보드)"
        
        # 2. CP210x 계열 (미국 Silicon Labs사)
        elif port.vid == 0x10C4: 
            chip_name = "CP2102 (호환 보드)"
            
        # 3. ATmega16U2 계열 (아두이노 정품/고급 호환)
        elif port.vid == 0x2341: 
            chip_name = "ATmega16U2 (정품/고급형)"
        
        # 4. FTDI 계열 (구형 또는 특수 보드)
        elif port.vid == 0x0403:
            chip_name = "FTDI (구형 보드)"

        print(f"{port.device:<10} {vid_hex}:{pid_hex:<9} {chip_name}")
        print(f"   └ Description: {port.description}")
        print("-" * 50)

    if not found:
        print("연결된 시리얼 장치를 찾을 수 없습니다.")

if __name__ == "__main__":
    check_chip_type()
