import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from main import image_parser_agent, latex_generator_agent, Runner
import tempfile
from PIL import Image
import io
import base64

load_dotenv()

st.set_page_config(page_title="LaTeX Image Parser", layout="wide")

st.title("LaTeX Image Parser")
st.markdown("Upload an image with mathematical content or provide an image URL to get LaTeX code.")

# Initialize session state variables
if "parsed_text" not in st.session_state:
    st.session_state.parsed_text = ""
if "latex_code" not in st.session_state:
    st.session_state.latex_code = ""

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Image", "Image URL"])

# Tab 1: Upload Image
with tab1:
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Process Uploaded Image", key="process_upload"):
            with st.spinner("Processing image..."):
                # Save the uploaded file to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Create a data URL for the image
                img_bytes = uploaded_file.getvalue()
                encoded = base64.b64encode(img_bytes).decode()
                mime_type = uploaded_file.type
                img_url = f"data:{mime_type};base64,{encoded}"
                
                # Process the image
                async def process_image():
                    parsed_result = await Runner.run(image_parser_agent, img_url)
                    st.session_state.parsed_text = parsed_result.final_output.text
                    
                    latex_result = await Runner.run(latex_generator_agent, st.session_state.parsed_text)
                    st.session_state.latex_code = latex_result.final_output.latex_code
                
                # Run the async function
                asyncio.run(process_image())
                
                # Clean up temporary file
                os.unlink(tmp_path)
                
                st.success("Processing complete!")

# Tab 2: Image URL
with tab2:
    image_url = st.text_input("Enter image URL:")
    
    if image_url:
        st.image(image_url, caption="Image from URL", use_column_width=True)
        
        if st.button("Process Image URL", key="process_url"):
            with st.spinner("Processing image..."):
                # Process the image
                async def process_image_url():
                    parsed_result = await Runner.run(image_parser_agent, image_url)
                    st.session_state.parsed_text = parsed_result.final_output.text
                    
                    latex_result = await Runner.run(latex_generator_agent, st.session_state.parsed_text)
                    st.session_state.latex_code = latex_result.final_output.latex_code
                
                # Run the async function
                asyncio.run(process_image_url())
                
                st.success("Processing complete!")

# Display results
if st.session_state.parsed_text or st.session_state.latex_code:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parsed Text")
        st.text_area("Extracted Text", st.session_state.parsed_text, height=300)
    
    with col2:
        st.subheader("Generated LaTeX")
        st.text_area("LaTeX Code", st.session_state.latex_code, height=300)
        
        # Add a button to copy LaTeX code to clipboard
        st.code(st.session_state.latex_code, language="latex")
        st.button("Copy LaTeX to Clipboard", 
                 on_click=lambda: st.session_state.update({"clipboard": st.session_state.latex_code}))
        
        # LaTeX Preview section
        st.subheader("LaTeX Preview")
        try:
            st.markdown(f"$${st.session_state.latex_code}$$")
            st.info("Note: Preview may not render complex LaTeX perfectly. Please use a dedicated LaTeX editor for final results.")
        except Exception as e:
            st.error(f"Could not render LaTeX preview: {str(e)}")

# Add information about how to run the app
st.markdown("---")
st.markdown("### How to run this app")
st.code("streamlit run app.py", language="bash") 