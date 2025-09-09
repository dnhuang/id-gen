# ID Generator

A secure web application that converts lists of names from files into unique identifiers. Built with Streamlit and designed for data anonymization and processing workflows.

## Overview

The ID Generator processes name lists from uploaded files (CSV, TXT, XLSX) or manual entry and converts them into unique identifiers using various algorithms. The application includes user authentication, duplicate detection, and flexible export options.

## Features

- **User Authentication**: Login system
- **Multi-format File Support**: Upload CSV, TXT, or XLSX files
- **Intelligent Parsing**: Automatic detection of name columns in Excel files
- **Duplicate Detection**: Identification of duplicate entries
- **Interactive Editing**: Add, edit, and remove names before processing
- **Multiple ID Types**: MD5, SHA256, SHA1 hashes, sequential IDs, or UUIDs
- **Export Options**: Download results as CSV or Excel files

## File Format Support

### CSV and TXT Files
- Comma-separated or newline-separated names
- Automatic separator detection

### Excel Files
- Automatically detects name columns in priority order:
  1. "Name" column (case-insensitive)
  2. "Subject" column (case-insensitive)
  3. "Trial" column (case-insensitive)

## ID Generation Methods

- **Hash-based**: MD5, SHA256, or SHA1 algorithms for consistent identifiers
- **Sequential**: Human-readable format (ID001, ID002, etc.)
- **UUID**: Random unique identifiers

## Project Structure

```
id-gen/
├── app.py                    # Main application
├── config.py                # Configuration settings
├── requirements.txt          # Dependencies
├── utils/                    # Core modules
│   ├── auth.py              # Authentication
│   ├── file_parser.py       # File processing
│   ├── name_processor.py    # Name validation
│   ├── hash_generator.py    # ID generation
│   └── export_manager.py    # File export
└── test_data/               # Sample files
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Streamlit Cloud Deployment

For deployment on Streamlit Cloud, user credentials should be stored in Streamlit secrets instead of the `users_config.json` file.
