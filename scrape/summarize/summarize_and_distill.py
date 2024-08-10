import csv
import anthropic
import time
from datetime import datetime
import os

API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=API_KEY)

# Instructions to be added to each prompt
SUMMARIZE_PROMPT = """You are an assistant that creates a summarized knowledge base of all information relating to Artisan and Ava from a given blob of text which is scraped from the Artisan website. This knowledge base will be used to simulate a copy of the Ava chatbot, which will talk as if it is Ava and refer to this knowledge base for information about Ava (itself). Your responses are always in the form of bullet points of relevant facts and information about Artisan or Ava, such as what they can do, and your responses will contain nothing else. If the text has nothing relating to Ava, respond with nothing."""


def call_claude_api(text, sys_prompt, max_tokens):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=max_tokens,
        temperature=0,
        system=sys_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ]
    )
    return message.content[0].text


def process_csv(file_path):
    output_file = "./scrape/summary_of_scrape.txt"

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile, \
            open(output_file, 'a', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text = row['Text']

            response = call_claude_api(text, SUMMARIZE_PROMPT, 1000)

            # Write to file
            outfile.write(f"{response}\n\n")
            outfile.flush()

            time.sleep(0.5)

    print(f"Outputs have been saved to {output_file}")


csv_file_path = './scrape/scraped_output.csv'
process_csv(csv_file_path)

DISTILL_PROMPT = """You are an assistant that will be given a set of bullet points, possibly with duplicate information, and you will respond with a version of the bullet points without duplicate information. You will respond only with a list of bullet points and nothing else."""

# Read out the string from "./scrape/summary_of_scrape.txt"
with open("./scrape/summary_of_scrape.txt", "r") as file:
    text = file.read()

    distillation = call_claude_api(text, DISTILL_PROMPT, 4096)

    # Save to distillation_of_summary.txt
    with open("./scrape/distillation_of_summary.txt", "w") as distillation_file:
        distillation_file.write(distillation)
