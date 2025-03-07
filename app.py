import streamlit as st
from PIL import Image
import os
from src.main import text_based
# from src.APR_QA import text_based
# Set page config
st.set_page_config(layout="wide")

# Add custom CSS to set the zoom level to 90%
st.markdown(
    """
    <style>
        body {
            zoom: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# Adding (css)stye to application
with open('style/final.css') as f:
    st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    

# Adding company logo
# imcol1, imcol2, imcol3, imcol4, imcol5 = st.columns((3,4,.5,4,3))
imcol1, imcol2, imcol5 = st.columns((5,5,5))

with imcol2:
    st.write("# ")
    # st.image('image/llmatscale_logo.png')
    st.image('image/dmv.png')   

# with imcol4:
#     st.write("# ")
#     st.write("# ")

st.markdown("<p style='text-align: center; color: black; font-size:25px;'><span style='font-weight: bold'></span>Miles JSON File Agent</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: blue;margin-top: -10px ;font-size:20px;'><span style='font-weight: bold'></span>Save time, increase accuracy, and avoid mistakes when entering data.</p>", unsafe_allow_html=True)
st.markdown("<hr style=height:2.5px;margin-top:0px;width:100%;background-color:gray;>",unsafe_allow_html=True)

    
#---------Side bar-------#
with st.sidebar:
    st.markdown("<p style='text-align: center; color: white; font-size:25px;'><span style='font-weight: bold; font-family: century-gothic';></span>Solutions Scope</p>", unsafe_allow_html=True)
    vAR_AI_application = st.selectbox("",['Select Application',"Miles Demo"],key='application')
    # selected = st.selectbox("",['User',"Logout"],key='text')
    vAR_LLM_model = st.selectbox("",['GEN AI Models',"gpt-3.5-turbo-16k-0613","gpt-4-0314","gpt-3.5-turbo-16k","gpt-3.5-turbo-1106","gpt-4-0613","gpt-4-0314"],key='text_llmmodel')
    vAR_LLM_framework = st.selectbox("",['Framework',"Langchain"],key='text_framework')

    # vAR_Library = st.selectbox("",["Library Used","Streamlit","Image","Pandas","openAI"],key='text1')
    vAR_Gcp_cloud = st.selectbox("",
                    ["Cloud Services","VM Instance","Computer Engine","Cloud Storage"],key='text2')
    st.markdown("#### ")
    href = """<form action="#">
            <input type="submit" value="Clear/Reset"/>
            </form>"""
    st.sidebar.markdown(href, unsafe_allow_html=True)
    st.markdown("# ")
    st.markdown("<p style='text-align: center; color: White; font-size:20px;'>Build & Deployed on<span style='font-weight: bold'></span></p>", unsafe_allow_html=True)
    s1,s2,s3,s4=st.columns((4,4,4,4))
    with s1:
        st.markdown("### ")
        st.image('image/image.png')
    with s2:    
        st.markdown("### ")
        st.image("image/oie_png.png")
    with s3:
        st.markdown("### ")
        st.image('image/aws.png')
    with s4:    
        st.markdown("### ")
        st.image("image/AzureCloud_img.png")


if vAR_AI_application == "Miles Demo":
    text_based()
