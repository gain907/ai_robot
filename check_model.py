import google.generativeai as genai

# 여기에 본인의 구글 API 키를 넣으세요
genai.configure(api_key="AIzaSyBSuz_M39FuTbw8o9YsRUbN_MwSQW5Lwc0")

print("🔍 사용 가능한 모델 목록을 조회합니다...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"오류 발생: {e}")