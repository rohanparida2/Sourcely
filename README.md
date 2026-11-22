# Web Search Chatbot

A small Streamlit chatbot that uses Gemini to decide when to search the web.
For search requests, it retrieves up to five Tavily results and asks Gemini to
answer from those sources with URL citations. Conversation history is kept for
follow-up questions during the session.

## Setup

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment in PowerShell:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your API keys:
   - Get a Tavily key at [app.tavily.com](https://app.tavily.com/).
   - Get a Gemini key at [Google AI Studio](https://aistudio.google.com/apikey).

   ```dotenv
   TAVILY_API_KEY=your_tavily_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Run

With the virtual environment activated, run:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit. Greetings and general chat are handled
without a web search; search-based answers show their sources below the answer.
