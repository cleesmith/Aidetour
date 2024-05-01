import time
import anthropic


client = anthropic.Client(api_key="")

def generate_response(client, messages):
    print(f"generate_response: messages:\n{'*'*70}\n{messages}\n{'*'*70}\n")
    start_time = time.time()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        messages=messages
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"elapsed time: {elapsed_time:.5f} seconds")
    response_text = response.content[0].text
    # print(f"generate_response: response_text:\n{response_text}")
    print(f"generate_response: response.headers:\n{response.headers}\n")
    return response_text

def count_words(text):
    return len(text.split())

def get_last_n_words(text, n):
    words = text.split()
    return " ".join(words[-n:])

def transcribe_full_youtube_transcript(raw_transcript):
    # initialize conversation with an instruction prompt
    initial_prompt = f"Format the following raw text into readable English, adding punctuation and capitalization, without changing any words:\n\n{raw_transcript}"
    messages = [{"role": "user", "content": initial_prompt}]
    
    transcribed_text = []
    remaining_text = raw_transcript

    # cls: quick test:
    # response = generate_response(client, messages)
    # print(f"transcribe_full_youtube_transcript: response={response}")
    # transcribed_text.append(response)

    while remaining_text:
        response = generate_response(client, messages)
        sys.exit(1)
        
        # Add assistant's response to the conversation history
        messages.append({"role": "assistant", "content": response})
        
        # Append the response to the final transcribed text
        transcribed_text.append(response)
        
        # Update remaining text (remove processed content)
        remaining_text = remaining_text[len(response):].strip()

        # Add user input message
        messages.append({"role": "user", "content": remaining_text})
    
    formatted_text = " ".join(transcribed_text)
    
    post_count = count_words(formatted_text)
    print(f"Word count after transcription: {post_count}")
    
    return formatted_text

input_file_path = "cls.txt"
with open(input_file_path, "r", encoding="utf-8") as file:
    raw_transcript = file.read()

print(f"Word count before transcription: {count_words(raw_transcript)}")
last_50_words = get_last_n_words(raw_transcript, 50)
print(f"last_50_words:\n{last_50_words}\n")

formatted_text = transcribe_full_youtube_transcript(raw_transcript)
print(formatted_text)
