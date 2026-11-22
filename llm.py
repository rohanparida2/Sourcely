import os
from collections.abc import Iterator

from dotenv import load_dotenv
from google import genai
from google.genai import types

from search import search_web

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"
SYSTEM_PROMPT = (
    "Answer using the provided sources, cite URLs, and say so if the sources "
    "don't contain the answer."
)
SEARCH_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="web_search",
            description=(
                "Search the web for current information or facts that benefit "
                "from web sources. Do not use for greetings or general chat."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="A focused web search query.",
                    )
                },
                required=["query"],
            ),
        )
    ]
)


class LLMError(Exception):
    """Raised when Gemini cannot generate an answer."""


def get_answer(
    messages: list[dict[str, str]],
) -> tuple[Iterator[str], list[dict[str, str]]]:
    """Let Gemini choose whether to search, then return a stream and sources."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError(
            "Gemini is not configured. Add GEMINI_API_KEY to your .env file."
        )

    client = genai.Client(api_key=api_key)
    contents = [
        types.Content(
            role="model" if message["role"] == "assistant" else "user",
            parts=[types.Part(text=message["content"])],
        )
        for message in messages
        if message["role"] in ("user", "assistant")
    ]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[SEARCH_TOOL],
    )

    try:
        decision = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
    except Exception as error:
        client.close()
        detail = str(error).replace(api_key, "[REDACTED]")
        print(f"Gemini API error: {detail}")
        raise LLMError(f"Gemini could not answer: {detail}") from error

    function_call = next(
        (
            part.function_call
            for candidate in (decision.candidates or [])
            for part in (candidate.content.parts or [])
            if part.function_call
        ),
        None,
    )

    if not function_call:
        client.close()
        answer = decision.text or "I couldn't generate a response. Please try again."
        return iter([answer]), []

    try:
        query = function_call.args.get("query", "")
        sources = search_web(query)
    except Exception:
        client.close()
        raise

    contents.extend(
        [
            decision.candidates[0].content,
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"results": sources},
                    )
                ],
            ),
        ]
    )

    def stream_answer() -> Iterator[str]:
        try:
            for chunk in client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as error:
            detail = str(error).replace(api_key, "[REDACTED]")
            print(f"Gemini streaming error: {detail}")
            raise LLMError(f"Gemini could not finish the answer: {detail}") from error
        finally:
            client.close()

    return stream_answer(), sources
