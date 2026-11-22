import streamlit as st
from dotenv import load_dotenv

from llm import LLMError, get_answer
from search import SearchError

load_dotenv()

st.set_page_config(page_title="Web Search Chatbot", page_icon="🔎")
st.title("Web Search Chatbot")
st.caption("Ask a question. Gemini will search the web when it needs current information.")

if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(sources):
    if sources:
        with st.expander("Sources"):
            for source in sources:
                st.markdown(f"- [{source['title']}]({source['url']})")
    else:
        st.caption("No web sources were found for this answer.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            show_sources(message.get("sources", []))

if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer_stream, sources = get_answer(st.session_state.messages)
            answer = st.write_stream(answer_stream)
            show_sources(sources)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except (LLMError, SearchError) as error:
            st.error(str(error))
            st.session_state.messages.append(
                {"role": "assistant", "content": str(error)}
            )
