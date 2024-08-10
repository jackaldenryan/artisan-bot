import anthropic


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


class ChatProcessor:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_suffix1 = """*************************************************
        To respond to this message, refer to the below information about Ava (you) and Artisan, which is the raw text scraped from the Artisan website. Note that some of this info may be irrelevant, but somewhere in here there is likely important information that you should use to respond to the user's message."""
        # Uncomment this to use the distillation for context instead.
        # self.prompt_suffix2 = read_file('./scrape/summarize/distillation.txt')
        self.prompt_suffix2 = read_file('./scrape/scraped.txt')

    def process_message(self, user_message, chat_history):
        # Prepare the messages for the API call
        messages = []

        # Add chat history
        for entry in chat_history:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["bot"]})

        # Add the new user message
        final_message = user_message + self.prompt_suffix1 + self.prompt_suffix2
        messages.append({"role": "user", "content": final_message})

        # Call the Claude API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            system="You are Ava, a chatbot created by Artisan to automate every aspect of outbound sales including outbound, finding leads, and sending personalized emails. Respond to every message as Ava. This means helping the user understand what Ava can do, what the Artisan platform can do, and helping them with any sales related requests.",
            messages=messages
        )

        # Extract the assistant's reply
        assistant_reply = response.content[0].text

        return assistant_reply
