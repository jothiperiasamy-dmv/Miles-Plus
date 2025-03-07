import streamlit as st
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

# Data Driven (Q&A)
def azure_assistant(user_input):
    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        st.session_state.thread = st.session_state.client.beta.threads.create()
    message = st.session_state.client.beta.threads.messages.create(thread_id=st.session_state.thread.id,role="user",content=user_input)
    
    run = st.session_state.client.beta.threads.runs.create_and_poll(thread_id=st.session_state.thread.id,assistant_id=os.environ["ASSISSTANT_ID"])
    # run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id,run_id=run.id)
    a = 0
    while True:
        run = st.session_state.client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=run.id)
        time.sleep(2)
        print(run.status)
        a = a+1
        print(a)
        if run.status=="completed":
            messages = st.session_state.client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            return text
        
        
# from openai import AzureOpenAI
   
# def azure_assistant(user_input):
#     # try:
#     # Initialize the Azure OpenAI client
#     if "client" not in st.session_state:
#         st.session_state.client = AzureOpenAI(
#             azure_endpoint="https://elp-dev.openai.azure.com/",
#             api_key="c31daf6dcf8541308af9ddac93360aeb",
#             api_version="2024-05-01-preview",
#         )
#     client = st.session_state.client

#     # Create a new thread if it doesn't exist
#     if "thread" not in st.session_state:
#         st.session_state.thread = client.beta.threads.create()

#     # Add a user question to the thread
#     client.beta.threads.messages.create(
#         thread_id=st.session_state.thread.id,
#         role="user",
#         content=user_input,
#     )

#     # Initiate a run
#     run = client.beta.threads.runs.create(
#         thread_id=st.session_state.thread.id,
#         assistant_id='asst_hPriMvcYgDfEsusTl1SKxlhl',
#     )

#     # Poll until the run completes or fails
#     while run.status in ["queued", "in_progress", "cancelling"]:
#         time.sleep(1)
#         run = client.beta.threads.runs.retrieve(
#             thread_id=st.session_state.thread.id, run_id=run.id
#         )

#     if run.status == "completed":
#         messages = client.beta.threads.messages.list(thread_id=st.session_state.thread.id)

#         # Loop through messages and return content based on role
#         for msg in messages.data:
#             content = msg.content[0].text.value
#             return content
#     else:
#         st.error("The assistant was unable to complete your request. Please try again.")
#         return "An error occurred during the assistant's processing."

#     # except Exception as e:
#     #     st.error(f"An error occurred: {str(e)}")
#     #     return "The assistant encountered an error. Please try again later."
