from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from lida import Manager, TextGenerationConfig, llm
import requests
from PIL import Image
from io import BytesIO
import base64
import tempfile
import uuid
import pandas as pd
import llmx.generators.text.openai_textgen
from openai import OpenAI
import openai

# === Configure page ===
st.set_page_config(
    page_title="LIDA Visualization Assistant",
    page_icon="📊",
    layout="wide"
)

# === Configure OpenAI client to use LM Studio's local server ===
# Set environment variables for OpenAI configuration
os.environ["OPENAI_API_KEY"] = "lm-studio"
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"

try:
    # Configure the OpenAI client for LIDA
    llmx.generators.text.openai_textgen.OpenAITextGenerator.client = OpenAI(
        api_key="lm-studio",
        base_url="http://127.0.0.1:1234/v1"
    )
    
    # Also configure the main openai module (legacy compatibility)
    import openai
    openai.api_key = "lm-studio"
    if hasattr(openai, 'api_base'):
        openai.api_base = "http://127.0.0.1:1234/v1"
    if hasattr(openai, 'base_url'):
        openai.base_url = "http://127.0.0.1:1234/v1"
    
    # Patch the default OpenAI client creation
    original_openai_init = OpenAI.__init__
    def patched_openai_init(self, api_key=None, base_url=None, **kwargs):
        if api_key is None:
            api_key = "lm-studio"
        if base_url is None:
            base_url = "http://127.0.0.1:1234/v1"
        return original_openai_init(self, api_key=api_key, base_url=base_url, **kwargs)
    
    OpenAI.__init__ = patched_openai_init
    
except Exception as e:
    st.error(f"Failed to configure OpenAI client: {e}")
    st.stop()

# === Check LM Studio connection and get available models ===
@st.cache_data(ttl=60)
def check_lm_studio_connection():
    try:
        resp = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        if resp.status_code == 200:
            models_data = resp.json()
            available_models = [model['id'] for model in models_data.get('data', [])]
            return True, available_models
        else:
            return False, []
    except Exception as e:
        return False, str(e)

# Check connection
connection_status, models_or_error = check_lm_studio_connection()

if connection_status:
    st.sidebar.success("LM Studio is connected ✅")
    if models_or_error:
        selected_model = st.sidebar.selectbox(
            "Select Model", 
            options=models_or_error,
            help="Choose the model loaded in LM Studio"
        )
    else:
        selected_model = "deepseek-coder-v2-lite-instruct"
        st.sidebar.success(f"Model set to: {selected_model}")
  # fallback
else:
    st.sidebar.error(f"LM Studio is unreachable: {models_or_error}")
    st.error("Please ensure LM Studio is running on http://127.0.0.1:1234")
    st.stop()

# === Initialize LIDA with error handling ===
try:
    # Initialize LIDA with simple OpenAI provider
    # The configuration is handled by environment variables and global client setting
    lida = Manager(text_gen=llm("openai"))
except Exception as e:
    st.error(f"Failed to initialize LIDA: {e}")
    st.stop()

# === Text generation configuration ===
textgen_config = TextGenerationConfig(
    n=1,
    model=selected_model,
    use_cache=True,
    temperature=0.1,  
    max_tokens=2048
)

# === Utility functions ===
def base64_to_image(base64_string):
    """Convert base64 string to PIL Image with error handling"""
    try:
        byte_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(byte_data))
    except Exception as e:
        st.error(f"Failed to decode image: {e}")
        return None

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location"""
    try:
        # Create temporary file with unique name
        temp_file = tempfile.NamedTemporaryFile(
            mode='wb', 
            suffix='.csv', 
            delete=False
        )
        temp_file.write(uploaded_file.getvalue())
        temp_file.close()
        return temp_file.name
    except Exception as e:
        st.error(f"Failed to save uploaded file: {e}")
        return None

def validate_csv_file(file_path):
    """Validate that the file is a proper CSV"""
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            st.warning("The uploaded CSV file is empty")
            return False
        return True
    except Exception as e:
        st.error(f"Invalid CSV file: {e}")
        return False

def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        st.warning(f"Could not clean up temporary file: {e}")

# === Main UI ===
st.title("📊 LIDA Visualization Assistant")

# Sidebar configuration
st.sidebar.header("Configuration")
visualization_library = st.sidebar.selectbox(
    "Visualization Library",
    ["seaborn", "matplotlib", "plotly"],
    help="Choose the library for generating charts"
)

menu = st.sidebar.selectbox("Choose an option", ["Summarize", "Question based graph"])

# === File upload section ===
st.header("📁 Upload Your Data")
file_uploader = st.file_uploader(
    "Upload a CSV file", 
    type="csv",
    help="Upload a CSV file to analyze and visualize"
)

if not file_uploader:
    st.info("👆 Please upload a CSV file to get started")
    st.stop()

# Validate file size
if file_uploader.size > 10 * 1024 * 1024:  # 10MB limit
    st.error("File size too large. Please upload a file smaller than 10MB.")
    st.stop()

# Save and validate file
temp_file_path = save_uploaded_file(file_uploader)
if not temp_file_path:
    st.stop()

if not validate_csv_file(temp_file_path):
    cleanup_temp_file(temp_file_path)
    st.stop()

# Show file info
try:
    df_preview = pd.read_csv(temp_file_path)
    st.success(f"✅ File uploaded successfully! Shape: {df_preview.shape}")
    
    with st.expander("📋 Data Preview"):
        st.dataframe(df_preview.head())
        
    with st.expander("📊 Data Info"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Columns:**")
            st.write(list(df_preview.columns))
        with col2:
            st.write("**Data Types:**")
            st.write(df_preview.dtypes.to_dict())
            
except Exception as e:
    st.error(f"Error reading file: {e}")
    cleanup_temp_file(temp_file_path)
    st.stop()

# === Main functionality ===
if menu == "Summarize":
    st.header("🔎 Data Summary and Visualization Goals")
    
    if st.button("🚀 Generate Analysis", type="primary"):
        with st.spinner("Analyzing your data..."):
            try:
                # Generate summary
                summary = lida.summarize(
                    temp_file_path, 
                    summary_method='default', 
                    textgen_config=textgen_config
                )
                
                if not summary:
                    st.error("Failed to generate data summary")
                    cleanup_temp_file(temp_file_path)
                    st.stop()
                
                st.subheader("📋 Data Summary")
                st.write(summary)
                
                # Generate goals
                with st.spinner("Generating visualization goals..."):
                    goals = lida.goals(summary=summary, textgen_config=textgen_config)
                    
                if not goals:
                    st.warning("No visualization goals were generated")
                else:
                    st.subheader("🎯 Suggested Visualizations")
                    if isinstance(goals, list):
                        for i, goal in enumerate(goals, 1):
                            if isinstance(goal, dict):
                                # If goal is a dict, extract the question or description
                                goal_text = goal.get('question', goal.get('visualization', goal.get('goal', str(goal))))
                            else:
                                goal_text = str(goal)
                            st.write(f"**{i}.** {goal_text}")
                    else:
                        st.write(f"**1.** {goals}")
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
            finally:
                cleanup_temp_file(temp_file_path)
elif menu == "Question based graph":
    st.header("🧠 Custom Question-Based Visualization")
    
    query = st.text_area(
        "Enter your question or goal to generate a specific graph",
        height=100,
        placeholder="Enter your query",
        help="Be specific about what you want to visualize"
    )
    
    if st.button("🎨 Generate Custom Graph", type="primary", disabled=not query.strip()):
        if query.strip():
            st.info(f"**Your query:** {query}")
            
            with st.spinner("Processing your request..."):
                try:
                    # Generate summary first
                    summary = lida.summarize(
                        temp_file_path, 
                        summary_method='default', 
                        textgen_config=textgen_config
                    )
                    
                    if not summary:
                        st.error("Failed to generate data summary")
                        cleanup_temp_file(temp_file_path)
                        st.stop()
                    
                    # Generate visualization based on query
                    charts = lida.visualize(
                        summary=summary, 
                        goal=query, 
                        textgen_config=textgen_config, 
                        library=visualization_library
                    )
                    
                    if charts and len(charts) > 0:
                        st.subheader("📊 Your Custom Visualization")
                        
                        chart = charts[0]  # Take the first chart
                        if hasattr(chart, 'raster') and chart.raster:
                            img = base64_to_image(chart.raster)
                            if img:
                                st.image(img)
                                
                                # Show the generated code
                                if hasattr(chart, 'code'):
                                    with st.expander("📝 Generated Code"):
                                        st.code(chart.code, language='python')
                                        
                                    # Option to download the code
                                    st.download_button(
                                        label="💾 Download Code",
                                        data=chart.code,
                                        file_name=f"visualization_{uuid.uuid4().hex[:8]}.py",
                                        mime="text/plain"
                                    )
                            else:
                                st.error("Failed to render the visualization")
                        else:
                            st.warning("No visualization could be generated for your query")
                    else:
                        st.warning("No charts were generated. Try rephrasing your question.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    cleanup_temp_file(temp_file_path)
        else:
            st.warning("Please enter a question or goal for visualization")

# === Footer ===
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>LIDA Visualization Assistant</small>
    </div>
    """, 
    unsafe_allow_html=True
)


