import streamlit as st
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PyPDF2 import PdfReader
import tiktoken
import os

# Set API token for HuggingFace
API_TOKEN = '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'  # Replace with your actual token

# Set up the page configuration
st.set_page_config(page_title='Constitution of India Q&A')

# Custom CSS for styling
page_bg_img = '''
<style>
h1 {
color: black;
font-weight: bold;
font-size: 48px;  
text-align: center;
margin-top: 50px;  
}
label {
color: black;
font-weight: bold;
font-size: 24px;  
margin-top: 20px;  
}
textarea {
border: 2px solid black;
}
button {
color: black;
font-weight: bold;
font-size: 18px;
border: 2px solid black;
background-color: white;
}
button:hover {
background-color: black;
color: white;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# App title
st.title('Constitution of India Q&A')

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Load the Constitution of India PDF text
pdf_path = r'C:\Users\Dell\LLM Projects\Query COI Project\Constitution of India.pdf'

# Ensure the file exists and extract text
if not os.path.isfile(pdf_path):
    st.error(f"File not found: {pdf_path}")
else:
    constitution_text = extract_text_from_pdf(pdf_path)

# Tokenizer for token counting
def count_tokens(text):
    tokenizer = tiktoken.get_encoding("gpt2")
    return len(tokenizer.encode(text))

# Function to truncate text to fit within token limits
def truncate_text(text, max_tokens):
    tokenizer = tiktoken.get_encoding("gpt2")
    tokens = tokenizer.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return tokenizer.decode(tokens)

# Function to generate response from LLM chain
def generate_response(input_text):
    max_input_tokens = 8192 - 100  # Adjusting for max_new_tokens
    truncated_text = truncate_text(constitution_text, max_input_tokens)
    
    falcon_llm = HuggingFaceEndpoint(
        api_key=API_TOKEN,
        repo_id='tiiuae/falcon-7b',
        temperature=0.6,
        max_new_tokens=100
    )
    template = '''Based on the following text, answer the question clearly and concisely: {context}

    Question: {question}

    Answer:'''
    prompt = PromptTemplate(template=template, input_variables=['context', 'question'])
    falcon_chain = LLMChain(prompt=prompt, llm=falcon_llm, verbose=True)
    
    try:
        output = falcon_chain.run(context=truncated_text, question=input_text)
        return output
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Error generating response"

# Form to accept user's text input
with st.form('question_form'):
    txt_input = st.text_area('Enter your question', '', height=100)
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('AI is Thinking...'):
            response = generate_response(txt_input)
            st.info(response)

