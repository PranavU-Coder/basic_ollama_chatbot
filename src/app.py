import helper as help
import streamlit as st

st.title("Ollama ChatBot At Your Assistance Today!")
st.divider()


with st.sidebar:
    st.header("Upload PDF Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to analyze"        
    )
    
    query = st.text_area(
        label="Ask a question about the PDF:",
        max_chars=200,
        key='query',
        placeholder="e.g., What is the main topic of this document?"
    )

    st.subheader("please note that large pdfs will take a lot of time generating a response")
    
    submit_button = st.button(label='Submit', type='primary')


if uploaded_file and query and submit_button:
    with open("temp_pdf.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Processing PDF and generating response..."):
        db = help.create_vector_db("temp_pdf.pdf")
        
        response = help.get_response_from_pdf(db, query=query)
    
    st.subheader("Response:")
    st.write(response)