# AgenTeX

A sophisticated tool that uses AI agents to parse images containing mathematical content and convert them to LaTeX code, with additional features for mathematical analysis and step-by-step solutions.

## 📜 Overview

Latex_Agents is an advanced tool that leverages OpenAI's powerful GPT-4o model to:

- Parse images containing mathematical equations
- Classify mathematical content by type and difficulty
- Generate LaTeX code for mathematical expressions
- Provide step-by-step solutions to mathematical problems

The application offers both a command-line interface and a user-friendly web interface built with Streamlit.

## ✨ Features

- **Multi-modal input**:
  - Upload images containing mathematical content
  - Provide URLs to images with equations
  - Enter mathematical text directly

- **Comprehensive analysis**:
  - Mathematical content parsing from images
  - Classification of mathematical type and difficulty level
  - Step-by-step problem solutions
  - High-quality LaTeX code generation optimized for KaTeX
  - LaTeX preview right in the web interface

- **User-friendly interfaces**:
  - Simple command-line interface
  - Intuitive Streamlit web application
  - Copy-to-clipboard functionality for generated LaTeX

## 🛠️ Architecture

The system is built using a multi-agent architecture with specialized AI agents:

1. **Image Parser Agent**: Extracts mathematical content from images using GPT-4o vision capabilities
2. **Math Classifier Agent**: Categorizes the mathematical content and assesses difficulty
3. **Solution Generator Agent**: Provides step-by-step solutions to problems
4. **LaTeX Generator Agent**: Converts mathematical expressions to LaTeX code optimized for KaTeX

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- (Optional) AgentOps API key for tracking

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Latex_Agents.git
   cd Latex_Agents
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   AGENTOPS_API_KEY=your_agentops_api_key  # Optional
   ```

## 📊 Usage

### Command Line Interface

Run the command line version to process mathematical images or text:

```bash
python main.py
```

The CLI will guide you through the process of providing an image URL or mathematical text input.

### Web Interface

Run the web application for a more interactive experience:

```bash
streamlit run app.py
```

This will start a local web server and open the application in your default browser. From there you can:

1. **Upload an image**: Use the "Upload Image" tab to upload an image file containing mathematical content
2. **Provide an image URL**: Use the "Image URL" tab to enter a URL pointing to an image with mathematical content
3. **Enter text directly**: Use the "Text Input" tab to enter mathematical expressions or problems as text

The application will process your input and display:
- The parsed mathematical content
- Classification of the mathematical type and difficulty
- Step-by-step solution (if applicable)
- Generated LaTeX code with a preview
- Key concepts involved in the mathematical content

## 🧩 Dependencies

The project relies on the following key Python packages:

- `openai`: For accessing GPT-4o and vision models
- `streamlit`: For the web interface
- `python-dotenv`: For loading environment variables
- `pydantic`: For data validation and settings management
- `agentops`: For agent telemetry (optional)
- `openai-agents`: For the agent framework

## 🧪 Example Workflow

1. User uploads an image containing the quadratic formula
2. Image Parser Agent extracts the text "x = (-b ± √(b² - 4ac)) / 2a"
3. Math Classifier Agent identifies it as algebra (category) and easy (difficulty)
4. LaTeX Generator Agent converts it to `x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`
5. Solution Generator Agent provides step-by-step solution if applicable
6. The web interface displays the results with rendered LaTeX

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AgentOps for hosting this hackathon
- OpenAI for providing the GPT-4o model
- Streamlit for the web framework
- The open-source community for various libraries used in this project
