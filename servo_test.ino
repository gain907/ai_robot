#include <Servo.h>

// 서보 객체 선언
Servo LServo;  // 왼쪽
Servo RServo;  // 오른쪽
Servo HServo;  // 가운데

// 핀 번호 설정
const int LS_pin = 8;
const int RS_pin = 9;
const int HS_pin = 10;

// ★ 기본 각도 (복귀 위치) ★
const int L_Default = 180;
const int R_Default = 0;
const int H_Default = 90;

void setup() {
  // 1. 시리얼 통신 시작 (키보드 입력을 위해 필수)
  Serial.begin(9600); 

  // 2. 서보모터 연결
  LServo.attach(LS_pin);
  RServo.attach(RS_pin);
  HServo.attach(HS_pin);

  // 3. 초기 위치로 이동
  resetPosition();
  
  Serial.println("System Ready!");
  Serial.println("Press 1: Left Arm, 2: Right Arm, 3: Head Turn, 4: Reset All");
}

void loop() {
  // 컴퓨터로부터 데이터가 들어왔는지 확인
  if (Serial.available() > 0) {
    char cmd = Serial.read(); // 키보드 입력값 읽기

    // --- 1번: 왼쪽 모터 동작 (90도로 이동 후 유지) ---
    if (cmd == '1') {
      LServo.write(90);
      Serial.println("Left Servo Moved");
    }
    
    // --- 2번: 오른쪽 모터 동작 (90도로 이동 후 유지) ---
    else if (cmd == '2') {
      RServo.write(90);
      Serial.println("Right Servo Moved");
    }
    
    // --- 3번: 가운데 모터 동작 (고개를 옆으로 돌림) ---
    else if (cmd == '3') {
      HServo.write(0); // 0도 방향으로 회전 (필요시 180으로 변경 가능)
      Serial.println("Head Servo Moved");
    }
    
    // --- 4번: 모든 모터 원위치 (복귀) ---
    else if (cmd == '4') {
      resetPosition(); // 초기화 함수 호출
      Serial.println("All Reset to Default");
    }
  }
}

// 모든 모터를 기본 각도로 되돌리는 함수
void resetPosition() {
  LServo.write(L_Default); // 180
  RServo.write(R_Default); // 0
  HServo.write(H_Default); // 90
}