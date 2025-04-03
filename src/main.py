import streamlit as st
from streamlit_feedback import streamlit_feedback
from streamlit_chat import message
from src.Assisstant import utterances_gen_azure_assistant, azure_openai_model_for_optimizations
from src.API_request import call_query_api
from src.utility import (
    get_top_qids_by_question_count,
    get_questions_by_qid,
    update_qna_questions_multithreaded,
    update_json_copy_with_optimized_utterances,
    load_json_file,
    save_json_file,
    copy_json_file,
    update_conditional_sentences_with_qid_matching,
    replace_q_values_with_actual_qid_file
)
from src.data_analysis import (compare_qna_utterances,
                               load_qna_json,
                               get_all_keys_with_descriptions,
                               get_referenced_qids,
                               get_keys_with_null_values,
                               get_keys_with_duplicate_values,
                               get_qnas_with_lambda,
                               get_qna_type_count,
                               get_qnas_with_buttons,
                               get_top_utterance_qnas,
                               get_most_reused_urls,
                               get_session_attribute_usage,
                               get_qnas_with_lambda_details,
                               get_lambda_usage_with_api_info,
                               get_all_api_calls_used,
                               get_qnas_with_conditional_chaining,
                               get_qnas_with_buttons_detailed,
                               generate_qna_analysis_excel,
                               generate_comparison_excel
                               )
import json
import re
import shutil
import os
import random
from dotenv import load_dotenv
load_dotenv()

def text_based(vAR_AI_application):
    if vAR_AI_application == "Data Analysis":
        file_path = "data/03-21-vrstatus-fix-qna.json"
        qna_items = load_qna_json(file_path)
        col1, col2, col3, col4 = st.columns((1, 3, 3.5, 1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        col11, col22, col33, col44 = st.columns((1, 3, 3.5, 1.5))
        m11, m22, m33 = st.columns([1, 7, 1])
        col111, col222, col333, col444 = st.columns((1, 3, 3.5, 1.5))
        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Analysis</span></p>", unsafe_allow_html=True)
        with col3:
            analysis_titles = [
    "Select",
    "Pre - Processing",
    "Post - Processing",
    "Comparison - Report",
    "All Keys Used",
    "High Utterance QnAs (Over 50)",
    "Keys with Duplicate Values",
    "Keys with Null Values",
    "QnAs with Lambda Details",
    "All API Calls Used",
    "Lambda Usage with API Info",
    "Most Reused URLs (args)",
    "QnA Type Count",
    "QnAs with Buttons",
    "QnAs with Buttons (Detailed)",
    "QnAs with Conditional Chaining",
    "Referenced QIDs",
    "Session Attribute Usage"
]

            vAR_input_analysis = st.selectbox("", analysis_titles)
            if vAR_input_analysis == "All Keys Used":
                with m2:
                    st.write("## All Keys Used")
                    st.write("Displays all unique JSON keys used across QnA items. Helps understand the structure and completeness of each entry.")
                    df = get_all_keys_with_descriptions(qna_items)
                    st.dataframe(df)
                    
            elif vAR_input_analysis == "QnAs with Conditional Chaining":
                with m2:
                    st.write("## QnAs with Conditional Chaining")
                    st.write("Lists all QnAs using conditionalChaining logic for intelligent follow-ups.")
                    df = get_qnas_with_conditional_chaining(qna_items)
                    st.dataframe(df)
            elif vAR_input_analysis == "QnAs with Buttons (Detailed)":
                with m2:
                    st.write("## QnAs with Buttons (Detailed)")
                    st.write("Displays QnAs that present buttons to users, including button text and target values.")
                    df = get_qnas_with_buttons_detailed(qna_items)
                    st.dataframe(df)
                    
            elif vAR_input_analysis == "All API Calls Used":
                with m2:
                    st.write("## All API Calls Used by Lambda Functions")
                    st.write("Lists all unique API endpoints or method calls associated with Lambda functions referenced by QnAs.")
                    df = get_all_api_calls_used(qna_items)
                    st.dataframe(df)
            
            elif vAR_input_analysis == "Lambda Usage with API Info":
                with m2:
                    st.write("## Lambda Usage with API Info")
                    st.write("Shows which Lambda functions are used in QnAs and the API calls or logic tied to each.")
                    df = get_lambda_usage_with_api_info(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "QnAs with Lambda Details":
                with m2:
                    st.write("## QnAs with Lambda Functions")
                    st.write("Displays all QnAs that invoke a Lambda function. Useful for identifying where dynamic or API-based logic is used.")
                    df = get_qnas_with_lambda_details(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "Referenced QIDs":
                with m2:
                    st.write("## Referenced QIDs")
                    st.write("Lists all QIDs that are referenced by other QnAs through buttons or redirects. Useful for tracking cross-references in your flows.")
                    df = get_referenced_qids(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "Keys with Null Values":
                with m2:
                    st.write("## Keys with Null Values")
                    st.write("Shows which keys contain null values in any QnA item. Helps identify missing or incomplete data.")
                    df = get_keys_with_null_values(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "Keys with Duplicate Values":
                with m2:
                    st.write("## Keys with Duplicate Values")
                    st.write("Identifies keys where the same value appears in multiple QnAs. Useful for detecting copy-paste content or reusable templates.")
                    df = get_keys_with_duplicate_values(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "QnA Type Count":
                with m2:
                    st.write("## QnA Type Count")
                    st.write("Breaks down how many QnAs exist per type (e.g., 'qna', 'chaining'). Useful for understanding your content distribution.")
                    df = get_qna_type_count(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "QnAs with Buttons":
                with m2:
                    st.write("## QnAs with Buttons")
                    st.write("Shows how many QnAs have UI response buttons for guided navigation. Useful for improving user interaction.")
                    df = get_qnas_with_buttons(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "High Utterance QnAs (Over 50)":
                with m2:
                    st.write("## High Utterance QnAs (Over 50)")
                    st.write("Displays the top 50 QnAs that contain the most user utterances. These represent the most diverse or complex topics users ask about.")
                    df = get_top_utterance_qnas(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "Most Reused URLs (args)":
                with m2:
                    st.write("## Most Reused URLs")
                    st.write("Displays the most frequently referenced external links. Helps maintain consistency and check for broken links.")
                    df = get_most_reused_urls(qna_items)
                    st.dataframe(df)

            elif vAR_input_analysis == "Session Attribute Usage":
                with m2:
                    st.write("## Session Attribute Usage")
                    st.write("Lists all session attributes used and how often. Useful for routing logic, personalization, or integrations like Amazon Connect.")
                    df = get_session_attribute_usage(qna_items)
                    st.dataframe(df)
            
            elif vAR_input_analysis == "Pre - Processing":
                with col3:
                    st.write("# ")
                    original_file_path = "data/03-21-vrstatus-fix-qna.json"
                    updated_file_path = generate_qna_analysis_excel(original_file_path)
                    with open(updated_file_path, "rb") as f:
                        st.download_button(
                            label="Download Excel Report",
                            data=f,
                            file_name="Pre - Processing_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            
            elif vAR_input_analysis == "Post - Processing":
                with col3:
                    st.write("# ")
                    original_file_path = "data/03-21-vrstatus-fix-qna_updated_fully_updated_qreplaced.json"
                    updated_file_path = generate_qna_analysis_excel(original_file_path)
                    with open(updated_file_path, "rb") as f:
                        st.download_button(
                            label="Download Excel Report",
                            data=f,
                            file_name="Post - Processing_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            elif vAR_input_analysis == "Comparison - Report":
                with col3:
                    st.write("# ")
                    original_file_path = "data/03-21-vrstatus-fix-qna.json"
                    updated_file_path = "data/03-21-vrstatus-fix-qna_updated_fully_updated_qreplaced.json"
                    updated_file_path = generate_comparison_excel(original_file_path, updated_file_path)
                    with open(updated_file_path, "rb") as f:
                        st.download_button(
                            label="Download Excel Report",
                            data=f,
                            file_name="Comparison - Report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

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
                    file_path = "data/03-21-vrstatus-fix-qna.json"
                    updated_file_path = update_qna_questions_multithreaded(file_path)
                    
                    updated_file_path = update_conditional_sentences_with_qid_matching(updated_file_path)
                    
                    updated_file_path = replace_q_values_with_actual_qid_file(updated_file_path)
                    
                    df = compare_qna_utterances(file_path, updated_file_path)
                    with m2:
                        st.dataframe(df)
                    # ✅ LOAD JSON FILE USING HELPER
                    updated_data = load_json_file(updated_file_path)
                    with col33:
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
                            
    elif vAR_AI_application == "Utterances Testing":
        col1, col2, col3, col4 = st.columns((1, 3, 3.5, 1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        with col2:
            st.write('# ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Give Input Utterance</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input = st.text_input(" ")
            if vAR_input:
                
                vAR_response = call_query_api(vAR_input)
                with m2:
                    st.write("# ")
                    st.dataframe(vAR_response.iloc[:, :-1])
                