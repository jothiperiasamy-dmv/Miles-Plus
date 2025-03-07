import streamlit as st
from streamlit_feedback import streamlit_feedback
from streamlit_chat import message
from src.Assisstant import azure_assistant


def text_based():
    col1,col2,col3,col4 = st.columns((1,3,3.5,1.5))
    m1, m2, m3 = st.columns([1, 7, 1])
    with col2:
        st.write('# ')
        st.write(' ')
        st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Upload the JSON file</span></p>", unsafe_allow_html=True)
    with col3:
        vAR_input_JSON = st.file_uploader("",type="JSON")
    if vAR_input_JSON:
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
                    vAR_response = azure_assistant(user_input)               
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