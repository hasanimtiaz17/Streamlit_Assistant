import openai
import streamlit as st
import time
from openai import OpenAI

assistant_id = "asst_sdtn3vIO0vF44IzTlgWh3zZ6"
client = OpenAI(api_key="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")

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="USF Student Health Services", page_icon=":speech_balloon:")

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("USF Student Health Services")
st.write("Hey! How can I help you")

if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Meow Meow?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
            # ,
            # instructions="Please answer the queries with meows you are a cat. Just MEOW a lot! MEOW ONLY, you are only allowed 4 english words and rest of answer must be various MEOW only"
        )

        with st.spinner("Wait... Generating response..."):  # Spinner starts here
            while run.status != 'completed':
                print(run.status)
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages 
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)
        # Spinner ends here
else:
    st.write("Click 'Start Chat' to begin.")
