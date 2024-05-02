
import time
import openai
from openai import OpenAI

client = OpenAI(api_key='')

def count_words(text):
    return len(text.split())

def get_last_n_words(text, n):
    words = text.split()
    return " ".join(words[-n:])

def generate_response(messages):
    print(f"generate_response: messages:\n{'*'*70}\n{messages}\n{'*'*70}\n")
    start_time = time.time()

    # response = openai.ChatCompletion.create(
    #     model="gpt-4-turbo",
    #     messages=messages
    # )
    # response_text = response['choices'][0]['message']['content']

    response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )
    response_text = response.choices[0].message.content

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"elapsed time: {elapsed_time:.5f} seconds")
    print(f"generate_response: response_text:\n{response_text}")
    return response_text

def transcribe_full_youtube_transcript(raw_transcript):
    initial_prompt = (
        f"Format the following raw text into readable English, adding punctuation "
        f"and capitalization, without changing any words:\n\n{raw_transcript}"
    )
    messages = [{"role": "user", "content": initial_prompt}]
    
    transcribed_text = []
    remaining_text = raw_transcript
    
    while remaining_text:
        response = generate_response(messages)

        # Add assistant's response to the conversation history
        messages.append({"role": "assistant", "content": response})
        
        # Append the response to the final transcribed text
        transcribed_text.append(response)
        
        # Update remaining text (remove processed content)
        remaining_text = remaining_text[len(response):].strip()

        # Add user input message
        messages.append({"role": "user", "content": remaining_text})
        break

    return "\n".join(transcribed_text)

input_file_path = "cls.txt"
with open(input_file_path, "r", encoding="utf-8") as file:
    raw_transcript = file.read()

print(f"Word count before transcription: {count_words(raw_transcript)}")
last_50_words = get_last_n_words(raw_transcript, 50)
print(f"last_50_words:\n{last_50_words}\n")

formatted_text = transcribe_full_youtube_transcript(raw_transcript)
print(formatted_text)
