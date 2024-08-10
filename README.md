This is a FastAPI app with a /chat endpoint that you can chat with programmatically or via a chat UI. The chatbot is essentially Claude Sonnet 3.5 augmented (via prompt injection/suffixing) with context about Ava scraped from Artisan's website. 

## Repo contents:
* **scrape** contains python scripts for scraping all urls at the artisan.co domain and compiling into a text file. It also contains (currently unused) code for summarizing the text
* **main.py** contains the route/endpoint definitions, and initializes the ChatProcessor
* **chat_processor.py** defines the ChatProcessor to act like Claude 3.5 Sonnet but with a system prompt telling Claude to act like Ava, and with a prompt suffix that gives context about Ava and Artisan
* **static and templates** contain the html and css for the UI

## Deployment
* The app is deployed here: https://artisan-bot-089345b068ca.herokuapp.com/ but a username and password are required.