import streamlit as st
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from openai import AzureOpenAI
import base64
import re

def utterances_gen_azure_assistant(user_input):
    if "client" not in st.session_state:
        st.session_state.client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-05-01-preview",
        )
    client = st.session_state.client

    # Create a new thread if it doesn't exist
    if "thread" not in st.session_state:
        st.session_state.thread = client.beta.threads.create()

    # Add a user question to the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=user_input,
    )

    # Initiate a run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=os.environ["ASSISSTANT_ID_UTT_GEN"],
    )

    # Poll until the run completes or fails
    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id, run_id=run.id
        )

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
        print(messages)
        # Loop through messages and return content based on role
        for msg in messages.data:
            content = msg.content[0].text.value
            return content
    else:
        st.error("The assistant was unable to complete your request. Please try again.")
        return "An error occurred during the assistant's processing."


import json
import os
import re
from openai import AzureOpenAI  # Make sure this import matches your SDK version

def azure_openai_model_for_optimizations_all(intent, utterances):
    reduction_percent = 30
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = "gpt-4o"
    subscription_key = os.environ["AZURE_OPENAI_API_KEY"]

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )
    chat_prompt = [
    {
        "role": "system",
        "content": (
            "You are a Natural Language Understanding (NLU) expert. "
            "Your task is to **optimize an existing list of user utterances** for a specific intent without changing the core meaning of any utterance. "
            "Focus on improving diversity, slot coverage, and phrasing — this is an optimization task, not generation from scratch.\n\n"
            "Optimization guidelines:\n"
            "- Maintain clear intent boundaries — do NOT introduce new intents.\n"
            "- Remove redundant, duplicate, or overly similar utterances.\n"
            "- Improve diversity in vocabulary, sentence structure, and phrasing.\n"
            "- Vary slot usage positions (beginning, middle, end).\n"
            "- Include natural variations in tone (formal/informal), punctuation, and expression.\n"
            "- Adapt the size of the optimized list based on the original input size — maintain **semantic coverage**, not a fixed count.\n\n"
            "Output format: Return ONLY the optimized utterance list in plain JSON array format: [\"Utterance1\", \"Utterance2\", ...]"
        )
    },
    {
        "role": "user",
        "content": (
            f"Optimize the following utterances for the intent: '{intent}'.\n\n"
            f"Original utterance list:\n{utterances}\n\n"
            "Return only the optimized list as a plain JSON array (no comments or extra explanation)."
        )
    }
]

#     chat_prompt = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an expert language model trained to optimize and consolidate user utterances for NLU systems. "
#                 "Your task is to analyze a list of user utterances associated with a specific intent and generate a minimized, "
#                 "high-quality list of optimized utterances while preserving full intent coverage. "
#                 "Return only the list in this format: [\"Utterance1\", \"Utterance2\", ...]"
#             ),
#         },
#         {
#             "role": "user",
#             "content": f"""Optimize the following utterances for the intent: '{intent}'.

# Here is the list of input utterances:
# {utterances}

# Return the optimized utterance list in plain JSON array format only: [ ... ]""",
#         },
#     ]

    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=4096,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False,
        )

        response_text = completion.choices[0].message.content.strip()
        print(f"[Debug] Raw model response for intent '{intent}': {response_text}")

        # Extract first JSON array from response using regex
        match = re.search(r"\[[\s\S]*?\]", response_text)
        if match:
            array_text = match.group(0)
            try:
                optimized = json.loads(array_text)
                if isinstance(optimized, list) and all(isinstance(item, str) for item in optimized):
                    return optimized
                else:
                    print(f"[Warning] Extracted content is not a valid list of strings for intent: {intent}")
                    return None
            except json.JSONDecodeError:
                print(f"[Warning] Extracted array could not be parsed for intent: {intent}")
                return None
        else:
            print(f"[Warning] No JSON array found in model response for intent: {intent}")
            return None

    except Exception as e:
        print(f"[Error] Exception during processing for intent '{intent}': {str(e)}")
        return None


# def azure_openai_model_for_optimizations_all(intent, utterances):
#     endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
#     deployment = "gpt-4o"
#     subscription_key = os.environ["AZURE_OPENAI_API_KEY"]
#     client = AzureOpenAI(
#         azure_endpoint=endpoint,
#         api_key=subscription_key,
#         api_version="2024-05-01-preview",
#     )
#     chat_prompt = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an expert language model trained to optimize and consolidate user utterances for NLU systems. "
#                 "Your task is to analyze a list of user utterances associated with a specific intent and generate a minimized, "
#                 "high-quality list of optimized utterances while preserving full intent coverage. "
#                 "Return only the list in this format: [\"Utterance1\", \"Utterance2\", ...]"
#             ),
#         },
#         {
#             "role": "user",
#             "content": f"""Optimize the following utterances for the intent: '{intent}'.

# Here is the list of input utterances:
# {utterances}

# Return the optimized utterance list in plain JSON array format only: [ ... ]""",
#         },
#     ]

#     completion = client.chat.completions.create(
#         model=deployment,
#         messages=chat_prompt,
#         max_tokens=800,
#         temperature=0.7,
#         top_p=0.95,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stream=False,
#     )

#     response_text = completion.choices[0].message.content.strip()

#     # Fallback checks
#     if not response_text.startswith("[") or "warning" in response_text.lower():
#         print(f"[Warning] GPT response contains unexpected format or warning for intent: {intent}")
#         return None

#     try:
#         optimized = json.loads(response_text)

#         # Ensure it is a list of strings
#         if isinstance(optimized, list) and all(isinstance(item, str) for item in optimized):
#             return optimized
#         else:
#             print(f"[Warning] GPT returned invalid list structure for intent: {intent}")
#             return None
#     except json.JSONDecodeError:
#         print(f"[Warning] Failed to parse JSON for intent: {intent}")
#         return None
        
import os
import json
from openai import AzureOpenAI

def azure_openai_model_for_optimizations(intent, utterances):
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]  
    deployment = "gpt-4o"
    subscription_key = os.environ["AZURE_OPENAI_API_KEY"]

    # Initialize Azure OpenAI Service client
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",
    )

    # Chat prompt with required format
    chat_prompt = [
        {
            "role": "system",
            "content": (
                "You are an expert language model trained to optimize and consolidate user utterances for natural language understanding (NLU) systems. "
                "Your task is to analyze a list of user utterances associated with a specific intent and generate a minimized, high-quality list of optimized utterances. "
                "The optimized utterances must retain full intent coverage while removing redundancy and semantically similar phrases. "
                "In addition, provide a short explanation of the optimization strategy used.\n\n"
                "⚠️ Important: Return the result strictly in the following JSON format:\n"
                "{\n"
                '  "Optimized_utterances": ["Utterance1", "Utterance2", ...],\n'
                '  "Explainable AI": "Brief explanation of how the utterances were optimized."\n'
                "}"
            )
        },
        {
            "role": "user",
            "content": f"""Optimize the following utterances for the intent: '{intent}'.

Here is the list of input utterances:
{utterances}

Please return the result in this strict JSON format only:
{{
  "Optimized_utterances": [ ... ],
  "Explainable AI": "..."
}}"""
        }
    ]

    # Call the model
    completion = client.chat.completions.create(  
        model=deployment,
        messages=chat_prompt,
        max_tokens=4096,  
        temperature=0.7,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,
        stream=False
    )

    response_text = completion.choices[0].message.content.strip()

    # Try parsing directly first
    try:
        result = json.loads(response_text)
        optimized_utterances = result.get("Optimized_utterances", [])
        explainable_ai = result.get("Explainable AI", "")
        return optimized_utterances, explainable_ai
    except json.JSONDecodeError:
        pass  # fallback below

    # ✅ Fallback: Try to extract JSON block via regex
    try:
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            json_text = json_match.group(0)

            # Clean common errors (optional)
            json_text = json_text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

            result = json.loads(json_text)
            optimized_utterances = result.get("Optimized_utterances", [])
            explainable_ai = result.get("Explainable AI", "")
            return optimized_utterances, explainable_ai
    except Exception as e:
        print(f"[ERROR] Fallback parsing failed: {e}")

    # If all fails, return empty response
    print("[Warning] Failed to parse response for intent:", intent)
    print("Raw response:\n", response_text)
    return [], ""

# def azure_openai_model_for_optimizations(intent, utterances):
#     endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]  
#     deployment = "gpt-4o"
#     subscription_key = os.environ["AZURE_OPENAI_API_KEY"]

#     # Initialize Azure OpenAI Service client with key-based authentication    
#     client = AzureOpenAI(  
#         azure_endpoint=endpoint,  
#         api_key=subscription_key,  
#         api_version="2024-05-01-preview",
#     )

#     # Prepare the chat prompt
#     chat_prompt = [
#         {
#             "role": "system",
#             "content": "You are an expert language model trained to optimize and consolidate user utterances for natural language understanding (NLU) systems. Your task is to analyze a list of user utterances associated with a specific intent and generate a minimized, high-quality list of optimized utterances. The optimized utterances must retain full intent coverage while removing redundancy, overlapping variations, and semantically similar phrases. The final output should be structured in clean JSON format."
#         },
#         {
#             "role": "user",
#             "content": f"""Optimize the following utterances for the intent: '{intent}'.

#     Here is the list of input utterances:
#     {utterances}

#     Please analyze and consolidate the utterances while preserving the original intent. Return your response in the following format:

#     {{
#     "intent": "{intent}",
#     "optimized_utterances": [
#         // optimized utterances here
#     ]
#     }}
#     """
#         }
#     ]
        
#     # Include speech result if speech is enabled  
#     messages = chat_prompt  
        
#     # Generate the completion  
#     completion = client.chat.completions.create(  
#         model=deployment,
#         messages=messages,
#         max_tokens=800,  
#         temperature=0.7,  
#         top_p=0.95,  
#         frequency_penalty=0,  
#         presence_penalty=0,
#         stop=None,  
#         stream=False
#     )

#     return completion.choices[0].message.content



def aws_amazon_tool_llm_resposne(intent):
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]  
    deployment = "gpt-4o"
    subscription_key = os.environ["AZURE_OPENAI_API_KEY"]

    # Initialize Azure OpenAI Service client
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",
    )
    chat_prompt = [
    {
        "role": "system",
        "content": (
            "You are an advanced language model specializing in structuring unstructured text data into well-organized tables. "
            "Your task is to extract meaningful information from user-provided unstructured text and present it in a tabular format. "
            "Ensure that all relevant data points are captured while maintaining clarity and readability."
        )
    },
    {
        "role": "user",
        "content": f"""give as table {intent}"""
    }
    ]

    # Call the model
    completion = client.chat.completions.create(  
        model=deployment,
        messages=chat_prompt,
        max_tokens=4096,  
        temperature=0.7,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,
        stream=False
    )

    response_text = completion.choices[0].message.content
    
    return response_text
