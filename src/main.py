import streamlit as st
from streamlit_feedback import streamlit_feedback
from streamlit_chat import message
from src.Assisstant import utterances_gen_azure_assistant, azure_openai_model_for_optimizations
from src.utility import (
    get_top_qids_by_question_count,
    get_questions_by_qid,
    update_qna_questions_multithreaded,
    update_json_copy_with_optimized_utterances,
    load_json_file,
    save_json_file,
    copy_json_file,
    update_conditional_sentences_with_qid_matching
)
import json
import re
import shutil
import os
import random
from dotenv import load_dotenv
load_dotenv()

def text_based(vAR_AI_application):
    if vAR_AI_application == "Optimize Utterances (All)":
        col1, col2, col3, col4 = st.columns((1, 3, 3.5, 1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        col11, col22, col33, col44 = st.columns((1, 3, 3.5, 1.5))
        m11, m22, m33 = st.columns([1, 7, 1])
        col111, col222, col333, col444 = st.columns((1, 3, 3.5, 1.5))
        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Model Provider</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input_model = st.selectbox("", ["All", "Openai(GPT)", "Google(GEMINI)", "Anthropic(Cluade)"])
        with col3:
            st.write("## ")
            if st.button("Optimize (All)"):
                with st.spinner("Wait for it..."):
                    file_path = "data/qna_uat (1).json"
                    updated_file_path = update_qna_questions_multithreaded(file_path)
                    
                    updated_file_path = update_conditional_sentences_with_qid_matching(updated_file_path)
                    # ✅ LOAD JSON FILE USING HELPER
                    updated_data = load_json_file(updated_file_path)

                    # ✅ DOWNLOAD USING JSON DUMP
                    st.download_button(
                        label="Download Updated JSON File",
                        data=json.dumps(updated_data, indent=4, ensure_ascii=False),
                        file_name="qna_uat_updated.json",
                        mime="application/json"
                    )

    elif vAR_AI_application == "Optimize Utterances":
        col1, col2, col3, col4 = st.columns((1, 3, 3.5, 1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        col11, col22, col33, col44 = st.columns((1, 3, 3.5, 1.5))
        m11, m22, m33 = st.columns([1, 7, 1])
        col111, col222, col333, col444 = st.columns((1, 3, 3.5, 1.5))
        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Model Provider</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input_model = st.selectbox("", ["All", "Openai(GPT)", "Google(GEMINI)", "Anthropic(Cluade)"])

        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Intent(Top 10)</span></p>", unsafe_allow_html=True)
        with col3:
            json_file_path = "data/qna_uat (1).json"
            top_10_intents = get_top_qids_by_question_count(json_file_path)
            top_10_intents.insert(0, "Select")
            vAR_input_intent = st.selectbox("", top_10_intents)

            if vAR_input_intent != 'Select':
                all_q_selected_intent = get_questions_by_qid(json_file_path, vAR_input_intent)
                with m2:
                    st.write("# ")
                    st.json({
                        "intent": vAR_input_intent,
                        "utterances": all_q_selected_intent
                    })

                with col33:
                    if st.button("Optimize"):
                        optimized_utterances, explainable_ai = azure_openai_model_for_optimizations(vAR_input_intent, all_q_selected_intent)
                        if len(optimized_utterances) >= 1:
                            json_text = {
                                "intent": vAR_input_intent,
                                "Optimized_Utterances": optimized_utterances
                            }
                            json_string = json.dumps(json_text, indent=4, ensure_ascii=False)
                            with m22:
                                st.code(json_string)
                                st.subheader("Explainable AI:")
                                st.success(explainable_ai)

                            # ✅ Use helper-based updated file creation
                            updated_file_path = update_json_copy_with_optimized_utterances(json_file_path, vAR_input_intent, optimized_utterances)
                            updated_data = load_json_file(updated_file_path)

                            with col333:
                                st.download_button(
                                    label="Download Updated JSON File",
                                    data=json.dumps(updated_data, indent=4, ensure_ascii=False),
                                    file_name="updated_qna.json",
                                    mime="application/json"
                                )
                        else:
                            st.warning("Something went wrong in the model response. Try again!")

    elif vAR_AI_application == "Generate Utterances":
        col1, col2, col3, col4 = st.columns((1, 3, 3.5, 1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Model Provider</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input_model = st.selectbox("", ["All", "Openai(GPT)", "Google(GEMINI)", "Anthropic(Cluade)"])

        if vAR_input_model in ["Openai(GPT)", "All"]:
            with m2:
                st.write("# ")
                if 'history' not in st.session_state:
                    st.session_state['history'] = []
                if 'generated' not in st.session_state:
                    st.session_state['generated'] = ["Greetings! I am LLMAI Live Agent. How can I help you?"]
                if 'past' not in st.session_state:
                    st.session_state['past'] = ["We are delighted to have you here in the LLMAI Live Agent Chat room!"]

                response_container = st.container()
                container = st.container()

                with container:
                    with st.form(key='my_form', clear_on_submit=True):
                        user_input = st.text_input("Prompt:", placeholder="How can I help you?", key='input')
                        submit_button = st.form_submit_button(label='Interact with LLM')

                    if submit_button and user_input:
                        vAR_response = utterances_gen_azure_assistant(user_input)
                        match = re.search(r"\{.*\}", vAR_response, re.DOTALL)

                        if match:
                            try:
                                json_text = match.group(0)
                                parsed_json = json.loads(json_text)
                                cleaned_json = {k: v for k, v in parsed_json.items() if k.lower() != "explainable ai"}

                                # ✅ Use clean file copy/load helpers
                                original_file_path = "data/qna_uat (1).json"
                                copied_file_path = "data/qna_uat_copy_for_optimization.json"
                                copy_json_file(original_file_path, copied_file_path)
                                copied_data = load_json_file(copied_file_path)

                                prefix = os.environ.get("INTENT_PREFIX_TEXT", "AUTO").upper()
                                random_number = random.randint(100, 999)
                                intent = cleaned_json.get("intent", "").strip().replace(" ", "_").replace("'", "").replace('"', "")
                                custom_qid = f"{prefix}_{random_number}_{intent}"

                                new_qna_entry = {
                                    "qid": custom_qid,
                                    "q": cleaned_json.get("new_utterances", [])
                                }
                                copied_data.get("qna", []).append(new_qna_entry)

                                updated_json_str = json.dumps(copied_data, indent=4, ensure_ascii=False)

                                st.success(f"✔ New QID added: `{custom_qid}`")
                                st.download_button(
                                    label="Download Updated JSON File",
                                    data=updated_json_str,
                                    file_name="qna_uat_updated_copy.json",
                                    mime="application/json"
                                )
                            except json.JSONDecodeError as e:
                                pass
                        else:
                            pass

                        st.session_state['past'].append(user_input)
                        st.session_state['generated'].append(vAR_response)

                if st.session_state['generated']:
                    with response_container:
                        for i in range(len(st.session_state['generated'])):
                            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                            message(st.session_state["generated"][i], key=str(i + 55), avatar_style="thumbs")
                            streamlit_feedback(
                                align="flex-start",
                                feedback_type="thumbs",
                                optional_text_label="[ Human Feedback Optional ] Please provide an explanation",
                                key=f"thumbs_{i}"
                            )