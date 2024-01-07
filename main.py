import os
import asyncio
import pyttsx3
import openai
import speech_recognition as sr
from PIL import Image
from io import BytesIO

openai_api_key = "YOUR API_KEY" 

async def get_openai_response(prompt):
    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        if hasattr(completion, 'choices') and completion.choices and len(completion.choices) > 0:
            assistant_reply = completion.choices[0].message.content

    
            if "generate image" in prompt.lower() and "image" in assistant_reply.lower():
                try:
       
                    image_url_start = assistant_reply.lower().find("image:")
                    if image_url_start != -1:
                        image_url = assistant_reply[image_url_start + len("image:"):].strip()
                        print(f"Image URL: {image_url}")

              
                        image_data = openai.File.create(url=image_url).file.read()

                        image = Image.open(BytesIO(image_data))
                        image.show()
                    else:
                        print("Image URL not found in the response.")
                except Exception as image_error:
                    print(f"Error processing image: {image_error}")

            return assistant_reply
        else:
            print("OpenAI API response does not contain valid choices.")
            print(f"OpenAI API Response: {completion}")
            return None
    
    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return None


async def process_audio(counter, said):
    if "zen" in said:
        words = said.split()
        new_string = ' '.join(words[1:])
        print(new_string)
        openai_response = await get_openai_response(new_string)

        if openai_response:
            print(f"OpenAI Response: {openai_response}")

 
            engine = pyttsx3.init()
            engine.say(openai_response)
            engine.save_to_file(openai_response, f"assistant_reply_{counter}.mp3")
            engine.runAndWait()

async def get_audio(counter):
    r = sr.Recognizer()

    try:
        with sr.Microphone(device_index=1) as source:
            print("Microphone found.")
            audio = r.listen(source)
            said = r.recognize_google(audio)
            print(f"User said: {said}")


            await asyncio.gather(
                get_openai_response(said),
                process_audio(counter, said),
            )

    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Speech Recognition request failed; {e}")
    except sr.WaitTimeoutError:
        print("Timeout waiting for speech input.")
    except sr.MicrophoneError as e:
        print(f"Error with the microphone: {e}")

async def main():
    counter = 1
    try:
        while True:
            await get_audio(counter)
            counter += 1

    except KeyboardInterrupt:
        print("Program terminated by the user.")

# Run the event loop
asyncio.run(main())
