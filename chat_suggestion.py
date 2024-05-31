from datetime import datetime, timedelta
from datetime import datetime,timedelta
import re
from phi3_model import model,tokenizer
import onnxruntime_genai as og

# Dummy dataset for conversation history
conversation_database = [
    {"timestamp": datetime(2024, 5, 15, 10, 30), "message": "Hi", "sender": "Alice"},
    {"timestamp": datetime(2024, 5, 15, 10, 32), "message": "Hello!", "sender": "Bob"},
    {"timestamp": datetime(2024, 5, 16, 11, 20), "message": "How are you?", "sender": "Alice"},
    {"timestamp": datetime(2024, 5, 16, 11, 22), "message": "I'm fine, thank you!", "sender": "Bob"},
    {"timestamp": datetime(2024, 5, 17, 12, 15), "message": "Need assistance?", "sender": "Alice"},
    {"timestamp": datetime(2024, 5, 17, 12, 17), "message": "Sure, what do you need help with?", "sender": "Bob"}
]

common_attributes = {
    "address": "456 Elm St, Smalltown, USA",
    "language": "Spanish",
    "ethnicity": "Hispanic",
    "eye_color": "Brown",
    "hobbies": ["Yoga"],
    "gender": "Female",
    "nationality": "Mexican"
}

tokenizer_stream = tokenizer.create_stream()
 
# Set the max length to something sensible by default,
# since otherwise it will be set to the entire context length
search_options = {}
search_options['max_length'] = 2048

def inference(prompt):
  input_tokens = tokenizer.encode(prompt)

  params = og.GeneratorParams(model)
  params.set_search_options(**search_options)
  params.input_ids = input_tokens
  generator = og.Generator(model, params)

  print("Output: ", end='', flush=True)

  try:
    while not generator.is_done():
      generator.compute_logits()
      generator.generate_next_token()

      new_token = generator.get_next_tokens()[0]
      print(tokenizer_stream.decode(new_token), end='', flush=True)
  except KeyboardInterrupt:
      print("  --control+c pressed, aborting generation--")

  print()
  del generator



def generate_next_chat_template(messages):
    """
    Generates the next three probable chat prompts based on the given messages.

    Args:
        messages (list): A list of messages to use as context for generating the next chat prompt.

    Returns:
        str: The generated chat prompts in JSON format with keys prompt1, prompt2, and prompt3.
    """
    
    prompt = f"""Given the following conversation in<>:\n <{messages}>\n
    Generate the next 3 probable chat prompt that the user can say next.
    Just give only the next prompt only to be sent by the user. 
    Just 3 responses in bulleted list. Don't need to include the name of user.
    Give in json format with keys prompt1, prompt2, prompt3. Just give one json object.
    """
    inference(prompt)

generate_next_chat_template(conversation_database)



