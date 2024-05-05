from groq import Groq
import re
import time
import traceback


client = Groq(
    api_key="",
    timeout=120.0,
    max_retries=0
)

total_start_time = time.time()

def transcribe_text(text, chunk_size=1000, overlap_size=150):
    transcribed_text = ""
    remaining_text = text
    text_loop = 1

    while remaining_text:
        words = remaining_text.split()
        # process in chunks with overlap
        chunk_end = min(len(words), chunk_size)
        overlap_end = min(len(words), chunk_end + overlap_size)
        prompt_words = " ".join(words[:overlap_end])

        prompt = (
"""
Transcribe the following raw text verbatim, preserving all words and their order. 
Add appropriate capitalization, punctuation, and sentence boundaries as needed for 
proper English, but do not add, remove, or modify any words. Please provide only 
the transcribed text that was sent to you. 
Please enclose and surround your responses with these tags: <TheEnd></TheEnd>.
"""
)
        prompt += f"\nThe raw text to be transcribed:\n\n{prompt_words}"

        try:
            # print(f"\n#{text_loop}: prompt to API:\n{prompt}\n")

            start_time = time.time()
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                # model="llama3-70b-8192", # Groq
                messages=[
                    {"role": "system", 
                        "content": 
                        "You are a helpful assistant and an experienced expert at transcribing raw text which must be verbatim(exact same words) but as a final human readable transcription that may be used during trials in a count of law as evidence."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0,
                stream=False
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"#{text_loop}: transcribe_text: elapsed time: {elapsed_time:.5f} seconds")

            # print(f"#{text_loop}: response:\n{response.choices[0].message}")

            processed_chunk = response.choices[0].message.content.strip()
            transcribed_text += processed_chunk

            # calculate remaining text by checking processed words directly
            processed_words_count = len(prompt_words.split())
            remaining_text = " ".join(words[processed_words_count:])
            text_loop += 1
            time.sleep(2) # slow down to avoid rate limit
        except Exception as e:
            print(f"\n{'*'*60}\nError: except Exception as e:\n{e}\n{'*'*60}\n")
            traceback.print_exc()  # Prints the full stack trace with line numbers
            return ""

    # post-process to ensure no duplicates and improve sentence reconstruction
    sentences = re.split(r'(?<=[.?!…])\s+(?=[A-Z])', transcribed_text)
    unique_sentences = []
    prev_sentence = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and (sentence != prev_sentence or len(sentence) > 10):
            unique_sentences.append(sentence)
            prev_sentence = sentence

    return " ".join(unique_sentences)

with open('cls.txt', 'r', encoding='utf-8') as file:
    raw_text = file.read()
    raw_text = re.sub(r'\s+', ' ', raw_text).strip()

# print(f"\nraw_text:\n{raw_text}\n")

formatted_text = transcribe_text(raw_text)
# print(f"\n\nformatted_text:\n{formatted_text}\n")

with open('cls_groq_capPunc.txt', 'w', encoding='utf-8') as f:
    f.write(formatted_text)

# how long did all this take:
total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"The End: elapsed time: {total_elapsed_time:.5f} seconds")
total_seconds = int(total_elapsed_time)
minutes = total_seconds // 60
seconds = total_seconds % 60
fractional_seconds = total_elapsed_time % 1  # Remaining fraction
if minutes > 0:
    print(f"The End: elapsed time: {minutes} minutes, {seconds:02d}.{int(fractional_seconds * 1_000_000):05d} seconds")
else:
    print(f"The End: elapsed time: {seconds}.{int(fractional_seconds * 1_000_000):05d} seconds")

