# ------------------- Import Libraries -------------------

import io
import json
import os
from typing import Literal

import google.generativeai as genai
import pygame
import speech_recognition as sr
from openai import OpenAI

# [API 키 설정]
# 1. 구글 Gemini API 키 (지능 담당)
genai.configure(api_key="여기에_GEMINI_API_키를_넣으세요")

# 2. OpenAI API 키 (목소리 담당 - 유료)
client = OpenAI(api_key="여기에_OPENAI_API_키를_넣으세요")

# File to store memory
MEMORY_FILE = "nova-memory.json"

# ------------------- AI Prompt -------------------
NOVA_PROMPT = (
    """
    Act as my personal AI assistant named Nova, designed to interact with me in a concise and informative manner.
    Guidelines:    
    1- Identify yourself as Nova, my personal AI assistant when asked.
    2- Respond politely, concisely and to the point information, avoiding lengthy explanations.
    3- Maintain context and avoid indicating memory lapses.
    4- Address the user as 'Dear [Name]' at start if known, otherwise use a respectful general greeting.
    5- For each user interaction, classify the information as 'Important' or 'Not Important' based on these rules:
    Important: Relates to personal data (names, birthdays, location, Hobbies), urgent/critical matters, or contains 
    keywords like 'urgent', 'critical', 'schedule 'or emotionally intense expressions.
    Not Important: Casual chatter, trivia, low-priority topics, or non-actionable information.
    Format your response as:    [Status, Response]
    Example:
    [Important, I have noted this critical task Mr. Jon.]
    [Not Important, That's fine! Thank you for sharing.]
    """
)


# Speech-to-Text Function
def speech_to_text():
    recognizer = sr.Recognizer()
    microphone_index = 2  # Change this to the correct index
    try:
        with sr.Microphone(device_index=microphone_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
    except (sr.UnknownValueError, sr.RequestError) as exp:
        print(f"Could not process audio: {exp}")
    except Exception as exp:
        print(f"An error occurred: {exp}")


# AI Model Response Function
def ai_model_response(u_input, conversation):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    full_prompt = f"{NOVA_PROMPT}\nConversation History:\n{conversation}\nUser: {u_input}"
    response = model.generate_content(full_prompt)
    return response.text.strip()


# Text-to-Speech Function using OpenAI
def text_to_speech(text):
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "echo"
    response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
    play_audio(response.read())


def play_audio(audio_bytes):
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# Load Conversation Memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {"Important": [], "Not Important": []}  # Initialize memory structure if absent


# Save Conversation Memory
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


# Label and Update Memory
def update_memory(u_input, nova_response, flag):
    memory = load_memory()

    # Ensure memory is initialized correctly
    if not isinstance(memory, dict):
        memory = {"Important": [], "Not Important": []}

    entry = {"user_input": u_input, "ai_response": nova_response}

    if flag == "Important":
        memory["Important"].append(entry)
    else:
        memory["Not Important"].append(entry)

    # Save the updated memory
    save_memory(memory)


# Generate Conversation History
def get_conversation_history():
    memory = load_memory()

    # Ensure memory is a dictionary with expected keys
    if not isinstance(memory, dict) or "Important" not in memory or "Not Important" not in memory:
        return ""

    history = "\n".join(
        f"[User: {entry['user_input']} AI: {entry['ai_response']}]"
        for key in ["Important", "Not Important"]
        for entry in memory[key]
    )
    return history


# Check Memory Percentage
def check_memory_percentage():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            data = json.load(file)

        json_string = json.dumps(data)
        full_length = len(json_string)

        max_length = 10000  # Set a limit for memory
        percentage = (full_length / max_length) * 100

        return percentage, full_length

    return 0, 0


# Delete Not Important Memory
def delete_not_important_memory():
    memory = load_memory()

    if "Not Important" in memory and memory["Not Important"]:
        memory["Not Important"] = []  # Clear the "Not Important" list
        save_memory(memory)
        print("All 'Not Important' entries have been deleted.")
    else:
        print("'Not Important' section is already empty.")


# Main Program Execution
if __name__ == "__main__":
    pygame.init()
    text_to_speech("Hello, How Can I help You Today?")

    try:
        while True:
            try:
                user_input = speech_to_text()
                if user_input:
                    conversation_history = get_conversation_history()
                    ai_response = ai_model_response(user_input, conversation_history)

                    # Ensure AI response is in the expected format
                    if ai_response.startswith("[") and ai_response.endswith("]"):
                        # Attempt to parse the response
                        status, req_response = ai_response.strip('[]').split(", ", 1)
                    else:
                        status = "Not Important"
                        req_response = ai_response  # Use the full response if not formatted correctly

                    update_memory(user_input, req_response, status)
                    print(f"AI Response: {req_response}")
                    text_to_speech(req_response)

            except KeyboardInterrupt:
                print("Exiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    finally:
        # Display memory usage percentage at the end of the program
        percentage, _ = check_memory_percentage()
        print(f"Memory usage till now: {percentage:.2f}%")

        # Delete "Not Important" memory if usage exceeds 10%
        if percentage > 10:
            print("Memory usage exceeds the limit. Deleting 'Not Important' memory...")
            delete_not_important_memory()
            # Recheck memory usage after deletion
            percentage, _ = check_memory_percentage()
            print(f"Updated memory usage: {percentage:.2f}%")