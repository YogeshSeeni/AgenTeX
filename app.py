import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from main import image_parser_agent, latex_generator_agent, Runner, handle_image_input, handle_text_input, math_classifier_agent, solution_generator_agent, qa_agent
import tempfile
from PIL import Image
import io
import base64
import requests
from urllib.parse import urlparse
import agentops
import traceback

load_dotenv()

# Initialize AgentOps tracking conditionally if API key is present
if os.getenv("AGENTOPS_API_KEY"):
    agentops.init(os.getenv("AGENTOPS_API_KEY"))
else:
    st.warning("AgentOps API key not found. Tracking is disabled.")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

st.set_page_config(page_title="Math LaTeX Assistant", layout="wide")

st.title("Math LaTeX Assistant")
st.markdown("Upload an image with mathematical content or provide an image URL/text to get LaTeX code and step-by-step solutions.")

# Initialize session state variables
if "parsed_text" not in st.session_state:
    st.session_state.parsed_text = ""
if "latex_code" not in st.session_state:
    st.session_state.latex_code = ""
if "error" not in st.session_state:
    st.session_state.error = ""
if "vision_response" not in st.session_state:
    st.session_state.vision_response = ""
if "math_classification" not in st.session_state:
    st.session_state.math_classification = None
if "solution_steps" not in st.session_state:
    st.session_state.solution_steps = None
if "qa_issues" not in st.session_state:
    st.session_state.qa_issues = []

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
                        
                        # Process with the enhanced agent pipeline
                        async def process_with_agents():
                            try:
                                # Use the new handle_image_input function
                                result = await handle_image_input(img_url)
                                if "error" in result:
                                    st.session_state.error = result["error"]
                                    return
                                
                                # Store all the results in session state
                                st.session_state.parsed_text = result["parsed_text"]
                                st.session_state.latex_code = result["latex"]
                                st.session_state.math_classification = result["math_type"]
                                st.session_state.solution_steps = result["solution"]
                                st.session_state.qa_issues = result.get("qa_issues", [])
                                
                            except Exception as e:
                                error_msg = f"Agent processing error: {type(e).__name__}: {str(e)}"
                                st.session_state.error = error_msg
                                st.error(error_msg)
                                traceback.print_exc()  # Print the full traceback for debugging
                        
                        # Run the async function
                        asyncio.run(process_with_agents())
                        
                    except Exception as e:
                        error_msg = f"Error during image processing: {type(e).__name__}: {str(e)}"
                        st.session_state.error = error_msg
                        st.error(error_msg)
                        traceback.print_exc()  # Print the full traceback for debugging
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    
                    if not st.session_state.error:
                        st.success("Processing complete!")
                
                except Exception as e:
                    error_msg = f"Error processing image: {type(e).__name__}: {str(e)}"
                    st.error(error_msg)
                    st.session_state.error = error_msg
                    traceback.print_exc()  # Print the full traceback for debugging

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
                    # Process with the enhanced agent pipeline
                    async def process_with_agents():
                        try:
                            # Use the new handle_image_input function
                            result = await handle_image_input(image_url)
                            if "error" in result:
                                st.session_state.error = result["error"]
                                return
                                
                            # Store all the results in session state
                            st.session_state.parsed_text = result["parsed_text"]
                            st.session_state.latex_code = result["latex"]
                            st.session_state.math_classification = result["math_type"]
                            st.session_state.solution_steps = result["solution"]
                            st.session_state.qa_issues = result.get("qa_issues", [])
                            
                        except Exception as e:
                            error_msg = f"Agent processing error: {type(e).__name__}: {str(e)}"
                            st.session_state.error = error_msg
                            st.error(error_msg)
                            traceback.print_exc()  # Print the full traceback for debugging
                    
                    # Run the async function
                    asyncio.run(process_with_agents())
                    
                    if not st.session_state.error:
                        st.success("Processing complete!")
                
                except Exception as e:
                    error_msg = f"Error processing image: {type(e).__name__}: {str(e)}"
                    st.error(error_msg)
                    st.session_state.error = error_msg
                    traceback.print_exc()  # Print the full traceback for debugging

# Tab 3: Text Input
with tab3:
    text_input = st.text_area("Enter mathematical expression or problem:", height=150)
    
    if st.button("Process Text", key="process_text") and text_input:
        st.session_state.error = ""
        with st.spinner("Processing text..."):
            try:
                # Process with the enhanced agent pipeline for text
                async def process_text_with_agents():
                    try:
                        # Use the handle_text_input function
                        result = await handle_text_input(text_input)
                        if "error" in result:
                            st.session_state.error = result["error"]
                            return
                            
                        # Store all the results in session state
                        st.session_state.parsed_text = result["original_text"]
                        st.session_state.latex_code = result["latex"]
                        st.session_state.math_classification = result["math_type"]
                        st.session_state.solution_steps = result["solution"]
                        st.session_state.qa_issues = result.get("qa_issues", [])
                        
                    except Exception as e:
                        error_msg = f"Agent processing error: {type(e).__name__}: {str(e)}"
                        st.session_state.error = error_msg
                        st.error(error_msg)
                        traceback.print_exc()  # Print the full traceback for debugging
                
                # Run the async function
                asyncio.run(process_text_with_agents())
                
                if not st.session_state.error:
                    st.success("Processing complete!")
            
            except Exception as e:
                error_msg = f"Error processing text: {type(e).__name__}: {str(e)}"
                st.error(error_msg)
                st.session_state.error = error_msg
                traceback.print_exc()  # Print the full traceback for debugging

# Display results
if st.session_state.error:
    st.error(f"Error: {st.session_state.error}")

if st.session_state.parsed_text or st.session_state.latex_code:
    st.markdown("---")
    st.header("Results")
    
    # Show math classification if available
    if st.session_state.math_classification:
        st.subheader("Math Classification")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Category:** {st.session_state.math_classification.get('category', 'Unknown')}")
        with col2:
            st.markdown(f"**Difficulty:** {st.session_state.math_classification.get('difficulty', 'Unknown')}")
        
        with st.expander("Classification Reasoning"):
            st.write(st.session_state.math_classification.get('reasoning', 'No reasoning provided'))
    
    # Show solution steps if available
    if st.session_state.solution_steps:
        st.subheader("Step-by-Step Solution")
        steps = st.session_state.solution_steps.get('steps', [])
        for i, step in enumerate(steps, 1):
            st.markdown(f"**Step {i}:** {step}")
        
        st.markdown(f"**Final Answer:** {st.session_state.solution_steps.get('final_answer', 'No final answer provided')}")
    
    # Original parsed text and LaTeX code
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Content")
        st.text_area("Extracted/Entered Text", st.session_state.parsed_text, height=200)
    
    with col2:
        st.subheader("Generated LaTeX")
        st.text_area("LaTeX Code", st.session_state.latex_code, height=200)
        
    # Quality assessment issues
    if st.session_state.qa_issues:
        st.subheader("Quality Issues")
        for issue in st.session_state.qa_issues:
            st.warning(issue)
    
    # LaTeX Preview section
    st.subheader("LaTeX Preview")
    try:
        st.latex(st.session_state.latex_code)
        st.info("Note: Preview may not render complex LaTeX perfectly. Please use a dedicated LaTeX editor for final results.")
    except Exception as e:
        st.error(f"Could not render LaTeX preview: {str(e)}")
        
    # Copy button for LaTeX
    st.button("Copy LaTeX to Clipboard", 
             on_click=lambda: st.session_state.update({"clipboard": st.session_state.latex_code}))