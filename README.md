# OCR MCQ Processor

A Python-based tool that extracts Multiple Choice Questions (MCQs) from PDF documents using OCR technology and processes them with Google's Gemini AI for intelligent analysis and answer generation.

## Features

- **PDF Text Extraction**: Uses OCR to extract text from PDF documents
- **MCQ Processing**: Automatically identifies and formats multiple choice questions
- **AI-Powered Analysis**: Leverages Gemini AI for intelligent question processing
- **Answer Generation**: Generates answers and explanations for MCQs
- **Question Refinement**: Refines and improves question formatting

## Requirements

- Python 3.7+
- Google Gemini API key
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ocr-mcq-processor.git
cd ocr-mcq-processor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Gemini API key:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

## Usage

### Basic OCR Processing
```bash
python ocr.py
```

### MCQ Processing with Gemini
```bash
python mcq_processor_gemini.py
```

## Output Files

- `output.txt`: Formatted MCQs extracted from PDF
- `mcq_answers.txt`: Generated answers and explanations
- `mcq_refined.txt`: Refined questions with original choices

## Project Structure

```
ocr-mcq-processor/
├── ocr.py                    # Main OCR processing script
├── mcq_processor_gemini.py  # MCQ processing with Gemini AI
├── test.pdf                 # Sample PDF for testing
├── output.txt               # Formatted MCQ output
├── mcq_answers.txt          # Generated answers
├── mcq_refined.txt          # Refined questions
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini AI for intelligent MCQ processing
- OCR libraries for PDF text extraction
- Open source community for various dependencies
