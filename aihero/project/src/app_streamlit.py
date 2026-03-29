import asyncio

import streamlit as st

from agent_repository_qa import build_agent, build_text_index, load_json
from logs import log_interaction_to_file


AGENT_INPUT = "_data/repository_chunks_sliding.json"
REPO_LABEL = "AltimateAI/altimate-code"


@st.cache_resource
def init_agent():
    """Initialize and cache the repository agent."""
    records = load_json(AGENT_INPUT)
    index = build_text_index(records)
    return build_agent(index)


agent = init_agent()

st.set_page_config(page_title="Repo Assistant", page_icon="🤖", layout="centered")
st.title("🤖 Repo Assistant")
st.caption(f"Ask questions about {REPO_LABEL}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = asyncio.run(agent.run(user_prompt=prompt))
            answer = result.output
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    log_interaction_to_file(agent, result.new_messages())

