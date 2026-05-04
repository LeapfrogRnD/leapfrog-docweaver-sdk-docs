# OCR Medical Device Extraction Pipeline

A Python application that extracts medical device information from prescription documents using Azure Document Intelligence for OCR and AWS Bedrock (Claude) for intelligent text processing.

## Features

- **OCR Processing**: Uses Azure Document Intelligence to extract text from PDF prescription documents
- **AI-Powered Extraction**: Leverages AWS Bedrock's Claude model to intelligently parse and extract medical device information
- **Medical Device Focus**: Specifically designed to identify medical devices (inhalers, braces, glucose monitors, etc.) while excluding regular medications
- **Structured Output**: Returns extracted data in a standardized JSON format

## Project Structure

```
├── main.py                 # Main application entry point
├── ocr_pipeline.py         # Azure Document Intelligence OCR processing
├── process_ocr_result.py   # AWS Bedrock-powered text extraction
├── settings.py             # Configuration management using Pydantic
├── utils.py                # Utility functions for Azure and AWS clients
├── requirements.txt        # Python dependencies
├── .env.sample            # Environment variables template
└── samples/               # Sample prescription documents
    ├── patient_1.pdf
    ├── patient_2.pdf
    └── patient_3.pdf
```

## Prerequisites

- Python 3.8+
- Azure Document Intelligence service
- AWS account with Bedrock access
- Valid credentials for both services

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OCR-AZURE-EBS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.sample .env
   ```
   
   Edit `.env` with your actual credentials:
   ```bash
   AZURE_ENDPOINT="your-azure-document-intelligence-endpoint"
   AZURE_KEY="your-azure-key"
   SAMPLE_DOCUMENT_PATH="samples/patient_1.pdf"
   AWS_ACCESS_KEY_ID="your-aws-access-key"
   AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
   AWS_SESSION_TOKEN="your-aws-session-token"  # Optional
   AWS_REGION="us-east-1"
   ```

## Usage

### Basic Usage

Run the main pipeline on a sample document:

```bash
python main.py
```

This will:
1. Process the document specified in `SAMPLE_DOCUMENT_PATH`
2. Extract text using Azure OCR
3. Parse medical device information using Claude
4. Output structured JSON data

### Using Individual Components

**OCR Processing Only:**
```python
from ocr_pipeline import Analyser

analyser = Analyser()
result = analyser.start_analysis("path/to/document.pdf")
print(result['content'])
```

**Medical Device Extraction Only:**
```python
from process_ocr_result import MedicationExtractor

extractor = MedicationExtractor()
devices = extractor.extract_medications(ocr_text)
print(devices)
```

## Output Format

The application returns a JSON object with the following structure:

```json
{
  "patient_name": "John Doe",
  "practitioner_name": "Dr. Jane Smith",
  "prescribed_date": "2023-10-15",
  "insurance_compAny": "Health Insurance Co.",
  "Devices Prescribed": [
    {
      "name": "Blood Glucose Monitor",
      "quantity": "1"
    },
    {
      "name": "Insulin Pen",
      "quantity": "2"
    }
  ]
}
```

## Configuration

The application uses Pydantic Settings for configuration management. All settings are defined in `settings.py` and can be overridden using environment variables.

### Available Settings

- `AZURE_ENDPOINT`: Azure Document Intelligence service endpoint
- `AZURE_KEY`: Azure service key
- `SAMPLE_DOCUMENT_PATH`: Path to the document to process
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_SESSION_TOKEN`: AWS session token (optional)
- `AWS_REGION`: AWS region (default: us-east-1)

## Key Components

### OCR Pipeline (`ocr_pipeline.py`)
- **Analyser Class**: Handles document analysis using Azure Document Intelligence
- Uses the "prebuilt-read" model for text extraction
- Processes PDF documents and returns structured text content

### Medical Device Extractor (`process_ocr_result.py`)
- **MedicationExtractor Class**: Uses AWS Bedrock's Claude model
- Specifically trained to identify medical devices vs. medications
- Returns structured JSON with patient and device information

### Utilities (`utils.py`)
- Client factory functions for Azure and AWS services
- Centralized credential management

## Medical Device Focus

This application is specifically designed to extract **medical devices and equipment** such as:
- Inhalers and nebulizers
- Blood glucose monitors
- Medical braces and supports
- Oxygen equipment
- Wheelchairs and mobility aids
- Medical testing devices

**Note**: Regular medications (tablets, capsules, syrups, injections) are intentionally excluded from the extraction results.

## Error Handling

The application includes basic error handling for:
- File reading operations
- Azure API calls
- AWS Bedrock invocations
- JSON parsing

## Dependencies

- `azure-ai-documentintelligence`: Azure Document Intelligence SDK
- `boto3`: AWS SDK for Python
- `pydantic-settings`: Configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the existing issues in the repository
2. Create a new issue with detailed information about the problem
3. Include sample documents (with sensitive information removed) if applicable

## Security Notes

- Never commit actual credentials to the repository
- Use environment variables for all sensitive configuration
- Ensure proper IAM permissions for AWS services
- Follow Azure security best practices for API keys