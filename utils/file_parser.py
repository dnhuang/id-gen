"""
File parsing utilities for different file formats
"""

import pandas as pd
import io
import re
from typing import List, Tuple, Optional
from config import MAX_NAMES_COUNT


class FileParser:
    """Handles parsing of CSV, TXT, and XLSX files to extract names"""
    
    def __init__(self):
        self.supported_extensions = ['.csv', '.txt', '.xlsx']
    
    def parse_file(self, uploaded_file) -> Tuple[List[str], str]:
        """
        Parse uploaded file and extract names
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (names_list, status_message)
        """
        try:
            file_extension = self._get_file_extension(uploaded_file.name)
            
            if file_extension == '.csv':
                return self._parse_csv(uploaded_file)
            elif file_extension == '.txt':
                return self._parse_txt(uploaded_file)
            elif file_extension == '.xlsx':
                return self._parse_xlsx(uploaded_file)
            else:
                return [], f"Unsupported file format: {file_extension}"
                
        except Exception as e:
            return [], f"Error parsing file: {str(e)}"
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return '.' + filename.split('.')[-1].lower()
    
    def _parse_csv(self, uploaded_file) -> Tuple[List[str], str]:
        """Parse CSV file to extract names"""
        try:
            # Read the content as string first to determine format
            content = uploaded_file.read().decode('utf-8')
            uploaded_file.seek(0)  # Reset file pointer
            
            # Try to detect if it's comma-separated or newline-separated
            if ',' in content and '\n' in content:
                # Check which separator is more frequent
                comma_count = content.count(',')
                newline_count = content.count('\n')
                
                if comma_count > newline_count:
                    # Comma-separated
                    df = pd.read_csv(uploaded_file)
                    if len(df.columns) > 1:
                        # Multiple columns, assume first column contains names
                        names = df.iloc[:, 0].astype(str).tolist()
                    else:
                        # Single column
                        names = df.iloc[:, 0].astype(str).tolist()
                else:
                    # Newline-separated, treat as single column
                    names = [line.strip() for line in content.split('\n') if line.strip()]
            elif ',' in content:
                # Only commas, split by comma
                names = [name.strip() for name in content.split(',') if name.strip()]
            else:
                # Only newlines or single column
                names = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Clean and filter names
            names = self._clean_names(names)
            
            if len(names) > MAX_NAMES_COUNT:
                return names[:MAX_NAMES_COUNT], f"File contains {len(names)} names. Showing first {MAX_NAMES_COUNT}."
            
            return names, f"Successfully extracted {len(names)} names from CSV file."
            
        except Exception as e:
            return [], f"Error parsing CSV file: {str(e)}"
    
    def _parse_txt(self, uploaded_file) -> Tuple[List[str], str]:
        """Parse TXT file to extract names"""
        try:
            content = uploaded_file.read().decode('utf-8')
            
            # Check if content has commas or just newlines
            if ',' in content:
                # Split by commas first, then by newlines
                parts = content.split(',')
                names = []
                for part in parts:
                    names.extend([name.strip() for name in part.split('\n') if name.strip()])
            else:
                # Split by newlines only
                names = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Clean and filter names
            names = self._clean_names(names)
            
            if len(names) > MAX_NAMES_COUNT:
                return names[:MAX_NAMES_COUNT], f"File contains {len(names)} names. Showing first {MAX_NAMES_COUNT}."
            
            return names, f"Successfully extracted {len(names)} names from TXT file."
            
        except Exception as e:
            return [], f"Error parsing TXT file: {str(e)}"
    
    def _parse_xlsx(self, uploaded_file) -> Tuple[List[str], str]:
        """Parse XLSX file to extract names from Name/Subject/Trial column (in priority order)"""
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Priority order for column names (case insensitive)
            priority_columns = ['name', 'subject', 'trial']
            
            name_column = None
            # Look for columns in priority order
            for priority_col in priority_columns:
                for col in df.columns:
                    if col.lower() == priority_col:
                        name_column = col
                        break
                if name_column:
                    break
            
            if name_column is None:
                return [], "Could not find 'Name', 'Subject', or 'Trial' column in Excel file."
            
            # Extract names from the identified column
            names = df[name_column].dropna().astype(str).tolist()
            
            # Clean and filter names
            names = self._clean_names(names)
            
            if len(names) > MAX_NAMES_COUNT:
                return names[:MAX_NAMES_COUNT], f"File contains {len(names)} names. Showing first {MAX_NAMES_COUNT}."
            
            return names, f"Successfully extracted {len(names)} names from Excel file (column: {name_column})."
            
        except Exception as e:
            return [], f"Error parsing Excel file: {str(e)}"
    
    def _clean_names(self, names: List[str]) -> List[str]:
        """Clean and validate extracted names"""
        cleaned_names = []
        
        for name in names:
            # Strip whitespace
            name = name.strip()
            
            # Skip empty names
            if not name:
                continue
                
            # Skip names that are clearly not names (numbers, special chars only)
            if re.match(r'^[\d\s\W]+$', name):
                continue
                
            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name)
            
            cleaned_names.append(name)
        
        return cleaned_names
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (is_valid, message)
        """
        if uploaded_file is None:
            return False, "No file uploaded."
        
        # Check file extension
        file_extension = self._get_file_extension(uploaded_file.name)
        if file_extension not in self.supported_extensions:
            return False, f"Unsupported file type. Supported types: {', '.join(self.supported_extensions)}"
        
        # Check file size (in bytes)
        file_size_mb = uploaded_file.size / (1024 * 1024)
        from config import MAX_FILE_SIZE_MB
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB}MB)."
        
        return True, "File validation passed."