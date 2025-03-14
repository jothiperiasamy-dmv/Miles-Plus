import streamlit as st
from streamlit_feedback import streamlit_feedback
from streamlit_chat import message
from src.Assisstant import utterances_gen_azure_assistant, azure_openai_model_for_optimizations
from src.utility import get_top_qids_by_question_count, get_questions_by_qid, update_qna_questions_with_backup
import json
import re

def text_based(vAR_AI_application):
    if vAR_AI_application == "Optimize Utterances (All)":
        st.warning("Under Development")
        
            
    elif vAR_AI_application == "Optimize Utterances":
        col1,col2,col3,col4 = st.columns((1,3,3.5,1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        col11,col22,col33,col44 = st.columns((1,3,3.5,1.5))
        m11, m22, m33 = st.columns([1, 7, 1])
        col111,col222,col333,col444 = st.columns((1,3,3.5,1.5))
        with col2:
            st.write('# ')
            # st.write(' ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Model Provider</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input_model = st.selectbox("",["All","Openai(GPT)","Google(GEMINI)", "Anthropic(Cluade)"])
        
        with col2:
            st.write('# ')
            # st.write(' ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Intent</span></p>", unsafe_allow_html=True)
        with col3:
            json_file_path = "data/qna_uat (1).json"
            top_10_intents = get_top_qids_by_question_count(json_file_path)
            top_10_intents.insert(0, "Select")
            vAR_input_intent = st.selectbox("",top_10_intents)
            if vAR_input_intent != 'Select':
                all_q_selected_intent = get_questions_by_qid(json_file_path,vAR_input_intent)
                with m2:
                    st.write("# ")
                    st.json({
                        "intent": vAR_input_intent,
                        "utterances": all_q_selected_intent
                    })
                with col33:
                    if st.button("Optimize"):
                        optimized_utterances, explainable_ai = azure_openai_model_for_optimizations(vAR_input_intent, all_q_selected_intent)
                        json_text = {
                            "intent": vAR_input_intent,
                            "Optimized_Utterances": optimized_utterances
                        }
                        json_string = json.dumps(json_text, indent=4, ensure_ascii=False)
                        with m22:
                            st.code(json_string)
                            # explainable_ai = 'Explainable AI: ',explainable_ai
                            st.subheader("Explainable AI:")
                            st.success(explainable_ai)
                        with col333:    
                            # Provide a download button
                            st.download_button(
                                label="Download JSON File",
                                data=json_string,
                                file_name="updated_file.json",
                                mime="application/json"
                            )

    elif vAR_AI_application == "Generate Utterances":
        col1,col2,col3,col4 = st.columns((1,3,3.5,1.5))
        m1, m2, m3 = st.columns([1, 7, 1])
        with col2:
            st.write('# ')
            # st.write(' ')
            st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Select Model Provider</span></p>", unsafe_allow_html=True)
        with col3:
            vAR_input_model = st.selectbox("",["All","Openai(GPT)","Google(GEMINI)", "Anthropic(Cluade)"])

        if vAR_input_model == "Openai(GPT)" or vAR_input_model == "All":
            with m2:
                st.write("# ")
                ########################################### chatbot UI###############################################
                if 'history' not in st.session_state:
                    st.session_state['history'] = []

                if 'generated' not in st.session_state:
                    st.session_state['generated'] = ["Greetings! I am LLMAI Live Agent. How can I help you?"]

                if 'past' not in st.session_state:
                    st.session_state['past'] = ["We are delighted to have you here in the LLMAI Live Agent Chat room!"]

                # container for the chat history
                response_container = st.container()

                # container for the user's text input
                container = st.container()
                with container:
                    with st.form(key='my_form', clear_on_submit=True):
                        user_input = st.text_input("Prompt:", placeholder="How can I help you?", key='input')
                        submit_button = st.form_submit_button(label='Interact with LLM')
                        
                    if submit_button and user_input:
                        # if vAR_input_model == "Openai(GPT)" and vAR_input_model == "All":
                        vAR_response = utterances_gen_azure_assistant(user_input)
                        
                        # 1. Try to extract JSON part (first valid {...} block)
                        match = re.search(r"\{.*\}", vAR_response, re.DOTALL)
                        if match:
                            try:
                                json_text = match.group(0)
                                parsed_json = json.loads(json_text)

                                # 2. Remove 'Explainable AI' key if it exists
                                cleaned_json = {k: v for k, v in parsed_json.items() if k != "Explainable AI"}

                                # 3. Convert cleaned JSON to string
                                final_json_str = json.dumps(cleaned_json, indent=4)

                                # 4. Dynamic filename
                                intent = cleaned_json.get("intent", "output").strip().replace(" ", "_")
                                filename = f"intent_{intent}.json"

                                st.download_button(
                                    label="Download JSON File",
                                    data=final_json_str,
                                    file_name=filename,
                                    mime="application/json"
                                )

                            except json.JSONDecodeError as e:
                                # st.error(f"❌ JSON decode failed: {e}")
                                pass
                        else:
                            # st.warning("⚠ No JSON object found in the model response. Displaying raw response:")
                            pass
                        
                        st.session_state['past'].append(user_input)
                        st.session_state['generated'].append(vAR_response)
                if st.session_state['generated']:
                    with response_container:
                        for i in range(len(st.session_state['generated'])):
                            # Display user message
                            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                            
                            # Display AI response with feedback
                            message(st.session_state["generated"][i], key=str(i + 55), avatar_style="thumbs")
                            feedback_ = streamlit_feedback(
                                align="flex-start",
                                feedback_type="thumbs",
                                optional_text_label="[ Human Feedback Optional ] Please provide an explanation",
                                key=f"thumbs_{i}"  # Unique key for each feedback element
                            )
