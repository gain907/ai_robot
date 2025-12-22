import speech_recognition as sr

print(" 마이크 목록을 조회합니다...")
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"번호 {index}: {name}")
