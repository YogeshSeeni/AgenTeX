# Latex_Agents

A tool for parsing images containing mathematical content and converting them to LaTeX code.

## Features

- Parse images with mathematical equations
- Convert mathematical content to LaTeX code
- Easy-to-use web interface
- Support for both image upload and URL input

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Running the Application

### Command Line Version
```
python main.py
```

### Web Interface
```
streamlit run app.py
```

## How It Works

1. Upload an image or provide an image URL
2. The app uses GPT-4o to parse the image and extract mathematical content
3. Another agent converts the extracted text to LaTeX code
4. View and copy the generated LaTeX code

## Requirements

- Python 3.8+
- OpenAI API key