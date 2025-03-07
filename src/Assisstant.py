import streamlit as st
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

# # Function to download the file from OpenAI
# def download_file(file_id, file_name):
#     response = st.session_state.client.files.content(file_id)
#     file_path = f"downloads/{file_name}"
    
#     # Ensure download directory exists
#     os.makedirs("downloads", exist_ok=True)

#     # Save file locally
#     with open(file_path, "wb") as f:
#         f.write(response.content)

#     return file_path

# # Azure Assistant Function (Handles Text & File Outputs)
# def azure_assistant(user_input):
#     if 'client' not in st.session_state:
#         st.session_state.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
#         st.session_state.thread = st.session_state.client.beta.threads.create()
    
#     # Send user input to the Assistant
#     message = st.session_state.client.beta.threads.messages.create(
#         thread_id=st.session_state.thread.id, 
#         role="user", 
#         content=user_input
#     )
    
#     # Run Assistant
#     run = st.session_state.client.beta.threads.runs.create_and_poll(
#         thread_id=st.session_state.thread.id,
#         assistant_id=os.environ["ASSISSTANT_ID"]
#     )

#     # Polling until completion
#     a = 0
#     while True:
#         run = st.session_state.client.beta.threads.runs.retrieve(
#             thread_id=st.session_state.thread.id, 
#             run_id=run.id
#         )
#         time.sleep(2)
#         print(run.status)
#         a += 1
#         print(a)
#         if run.status == "completed":
#             break
#         elif run.status == "failed":
#             st.error(f"Assistant run failed. Error: {run.last_error}")
#             return None

#     # Retrieve messages
#     messages = st.session_state.client.beta.threads.messages.list(
#         thread_id=st.session_state.thread.id
#     )
#     latest_message = messages.data[0]

#     # **Handle Text & File Responses**
#     response_text = ""

#     for content in latest_message.content:
#         if hasattr(content, "text"):  # If text response
#             response_text += content.text.value + "\n"

#         elif hasattr(content, "file_path"):  # If a file is generated
#             file_id = content.file_path.file_id
#             file_name = content.text.split("/")[-1]

#             # Download file
#             file_path = download_file(file_id, file_name)

#             # **Provide an embedded download link (no button)**
#             file_url = f"/{file_path}"  # Generate direct file path
#             st.markdown(f"📂 **File generated:** [Click here to download {file_name}]({file_url})")

#             response_text += f"\n📂 File ready for download: [{file_name}]({file_url})"

#     return response_text or "No valid response received."



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
