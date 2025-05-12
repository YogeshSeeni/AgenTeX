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
import requests
from urllib.parse import urlparse
import agentops

load_dotenv()

agentops.init(os.getenv("AGENTOPS_API_KEY"))

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

st.set_page_config(page_title="LaTeX Image Parser", layout="wide")

st.title("LaTeX Image Parser")
st.markdown("Upload an image with mathematical content or provide an image URL to get LaTeX code.")

# Initialize session state variables
if "parsed_text" not in st.session_state:
    st.session_state.parsed_text = ""
if "latex_code" not in st.session_state:
    st.session_state.latex_code = ""
if "error" not in st.session_state:
    st.session_state.error = ""
if "vision_response" not in st.session_state:
    st.session_state.vision_response = ""

# Function to call Vision API directly
def call_vision_api(image_url):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this math problem in detailed english to later generate latex code."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.session_state.error = f"Vision API error: {str(e)}"
        raise e

# Tab 1: Upload Image
tab1, tab2, tab3 = st.tabs(["Upload Image", "Image URL", "Text Input"])

with tab1:
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Process Uploaded Image", key="process_upload"):
            st.session_state.error = ""
            with st.spinner("Processing image..."):
                try:
                    # Save the uploaded file to a temporary file with proper extension
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        # For local files, we need to create a data URL
                        with open(tmp_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                        
                        mime_type = f"image/{file_extension[1:]}"  # Remove the dot from extension
                        img_url = f"data:{mime_type};base64,{encoded_string}"
                        
                        # Call Vision API directly
                        vision_response = call_vision_api(img_url)
                        st.session_state.vision_response = vision_response
                        
                        # Show the Vision API response
                        st.subheader("Vision API Response")
                        st.text_area("Raw Vision Response", vision_response, height=150)
                        
                        # Process with agents
                        async def process_with_agents():
                            try:
                                # Use the vision response as input to latex_generator_agent
                                latex_result = await Runner.run(latex_generator_agent, vision_response)
                                st.session_state.latex_code = latex_result.final_output.latex_code
                                st.session_state.parsed_text = vision_response  # Set parsed text to the vision response
                            except Exception as e:
                                st.session_state.error = f"Agent processing error: {str(e)}"
                                raise e
                        
                        # Run the async function
                        asyncio.run(process_with_agents())
                        
                    except Exception as e:
                        st.session_state.error = f"Error during image processing: {str(e)}"
                        raise e
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    
                    if not st.session_state.error:
                        st.success("Processing complete!")
                
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.session_state.error = str(e)

# Tab 2: Image URL
with tab2:
    image_url = st.text_input("Enter image URL:")
    
    if image_url:
        try:
            # Verify the URL is valid
            parsed_url = urlparse(image_url)
            is_valid = all([parsed_url.scheme, parsed_url.netloc])
            
            if is_valid:
                st.image(image_url, caption="Image from URL", use_column_width=True)
            else:
                st.warning("Please enter a valid image URL")
        except Exception:
            st.warning("Could not load image from URL")
        
        if st.button("Process Image URL", key="process_url"):
            st.session_state.error = ""
            with st.spinner("Processing image..."):
                try:
                    # Call Vision API directly
                    vision_response = call_vision_api(image_url)
                    st.session_state.vision_response = vision_response
                    
                    # Show the Vision API response
                    st.subheader("Vision API Response")
                    st.text_area("Raw Vision Response", vision_response, height=150)
                    
                    # Process with agents
                    async def process_with_agents():
                        try:
                            # Use the vision response as input to latex_generator_agent
                            latex_result = await Runner.run(latex_generator_agent, vision_response)
                            st.session_state.latex_code = latex_result.final_output.latex_code
                            st.session_state.parsed_text = vision_response  # Set parsed text to the vision response
                        except Exception as e:
                            st.session_state.error = f"Agent processing error: {str(e)}"
                            raise e
                    
                    # Run the async function
                    asyncio.run(process_with_agents())
                    
                    if not st.session_state.error:
                        st.success("Processing complete!")
                
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.session_state.error = str(e)

# Tab 3: Direct Text Input
with tab3:
    st.markdown("Enter your mathematical expression or description directly:")
    user_text_input = st.text_area("Mathematical Text", height=150)
    
    if st.button("Generate LaTeX", key="process_text"):
        st.session_state.error = ""
        with st.spinner("Generating LaTeX..."):
            try:
                # Process with latex generator agent
                async def process_text_with_agent():
                    try:
                        # Use the user text as input to latex_generator_agent
                        latex_result = await Runner.run(latex_generator_agent, user_text_input)
                        st.session_state.latex_code = latex_result.final_output.latex_code
                        st.session_state.parsed_text = user_text_input  # Set parsed text to the user input
                    except Exception as e:
                        st.session_state.error = f"Agent processing error: {str(e)}"
                        raise e
                
                # Run the async function
                asyncio.run(process_text_with_agent())
                
                if not st.session_state.error:
                    st.success("LaTeX generation complete!")
            
            except Exception as e:
                st.error(f"Error generating LaTeX: {str(e)}")
                st.session_state.error = str(e)

# Display results
if st.session_state.error:
    st.error(f"Error: {st.session_state.error}")

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
            st.latex(st.session_state.latex_code)
            st.info("Note: Preview may not render complex LaTeX perfectly. Please use a dedicated LaTeX editor for final results.")
        except Exception as e:
            st.error(f"Could not render LaTeX preview: {str(e)}")