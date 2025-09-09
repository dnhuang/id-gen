"""
Export utilities for generating CSV and XLSX files
"""

import pandas as pd
import io
from typing import List, Dict, Optional
from config import CSV_DELIMITER, NAME_COLUMN, ID_COLUMN


class ExportManager:
    """Handles exporting name-ID mappings to various formats"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx']
    
    def prepare_data_for_export(self, name_id_mappings: List[Dict]) -> pd.DataFrame:
        """
        Prepare data for export by converting to DataFrame
        
        Args:
            name_id_mappings: List of dictionaries with Name and ID keys
            
        Returns:
            Pandas DataFrame ready for export
        """
        if not name_id_mappings:
            return pd.DataFrame(columns=[NAME_COLUMN, ID_COLUMN])
        
        df = pd.DataFrame(name_id_mappings)
        
        # Ensure column names are consistent
        if 'Name' in df.columns and 'ID' in df.columns:
            df = df.rename(columns={'Name': NAME_COLUMN, 'ID': ID_COLUMN})
        
        # Sort by name for better readability
        df = df.sort_values(by=NAME_COLUMN)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def export_to_csv(self, name_id_mappings: List[Dict], filename: Optional[str] = None) -> bytes:
        """
        Export data to CSV format
        
        Args:
            name_id_mappings: List of name-ID mappings
            filename: Optional filename (not used for bytes output)
            
        Returns:
            CSV data as bytes
        """
        df = self.prepare_data_for_export(name_id_mappings)
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False, sep=CSV_DELIMITER, encoding='utf-8')
        
        # Get CSV content as bytes
        csv_content = output.getvalue()
        output.close()
        
        return csv_content.encode('utf-8')
    
    def export_to_xlsx(self, name_id_mappings: List[Dict], filename: Optional[str] = None) -> bytes:
        """
        Export data to Excel format
        
        Args:
            name_id_mappings: List of name-ID mappings
            filename: Optional filename (not used for bytes output)
            
        Returns:
            Excel data as bytes
        """
        df = self.prepare_data_for_export(name_id_mappings)
        
        # Create Excel file in memory
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Subject Mapping", index=False)
            
            # Get the worksheet to apply formatting
            worksheet = writer.sheets["Subject Mapping"]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set column width with some padding
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format header row
            from openpyxl.styles import Font, PatternFill
            
            header_font = Font(bold=True)
            header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
        
        # Get Excel content as bytes
        output.seek(0)
        excel_content = output.getvalue()
        output.close()
        
        return excel_content
    
    def create_download_data(self, name_id_mappings: List[Dict], format_type: str) -> Dict:
        """
        Create download data for Streamlit download button
        
        Args:
            name_id_mappings: List of name-ID mappings
            format_type: 'csv' or 'xlsx'
            
        Returns:
            Dictionary with data, filename, and mime_type
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if format_type == 'csv':
            data = self.export_to_csv(name_id_mappings)
            filename = "subject_id_mapping.csv"
            mime_type = "text/csv"
        elif format_type == 'xlsx':
            data = self.export_to_xlsx(name_id_mappings)
            filename = "subject_id_mapping.xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return {
            'data': data,
            'filename': filename,
            'mime_type': mime_type
        }
    
    def create_preview_data(self, name_id_mappings: List[Dict], max_rows: int = 10) -> pd.DataFrame:
        """
        Create preview data for display in Streamlit
        
        Args:
            name_id_mappings: List of name-ID mappings
            max_rows: Maximum number of rows to preview
            
        Returns:
            DataFrame with limited rows for preview
        """
        df = self.prepare_data_for_export(name_id_mappings)
        
        if len(df) > max_rows:
            return df.head(max_rows)
        
        return df
    
    def get_export_statistics(self, name_id_mappings: List[Dict]) -> Dict:
        """
        Get statistics about the export data
        
        Args:
            name_id_mappings: List of name-ID mappings
            
        Returns:
            Dictionary with export statistics
        """
        if not name_id_mappings:
            return {
                'total_records': 0,
                'csv_size_estimate': 0,
                'xlsx_size_estimate': 0
            }
        
        df = self.prepare_data_for_export(name_id_mappings)
        
        # Estimate file sizes
        csv_data = self.export_to_csv(name_id_mappings)
        xlsx_data = self.export_to_xlsx(name_id_mappings)
        
        return {
            'total_records': len(df),
            'csv_size_bytes': len(csv_data),
            'xlsx_size_bytes': len(xlsx_data),
            'csv_size_kb': round(len(csv_data) / 1024, 1),
            'xlsx_size_kb': round(len(xlsx_data) / 1024, 1),
            'columns': list(df.columns),
            'name_column': NAME_COLUMN,
            'id_column': ID_COLUMN
        }
    
    def validate_export_data(self, name_id_mappings: List[Dict]) -> Dict:
        """
        Validate data before export
        
        Args:
            name_id_mappings: List of name-ID mappings
            
        Returns:
            Dictionary with validation results
        """
        if not name_id_mappings:
            return {
                'is_valid': False,
                'error': "No data to export"
            }
        
        # Check required fields
        required_fields = ['Name', 'ID']
        missing_fields = []
        
        for mapping in name_id_mappings:
            for field in required_fields:
                if field not in mapping:
                    missing_fields.append(field)
        
        if missing_fields:
            return {
                'is_valid': False,
                'error': f"Missing required fields: {', '.join(set(missing_fields))}"
            }
        
        # Check for empty values
        empty_names = sum(1 for mapping in name_id_mappings if not mapping.get('Name', '').strip())
        empty_ids = sum(1 for mapping in name_id_mappings if not mapping.get('ID', '').strip())
        
        if empty_names > 0 or empty_ids > 0:
            return {
                'is_valid': False,
                'error': f"Found {empty_names} empty names and {empty_ids} empty IDs"
            }
        
        return {
            'is_valid': True,
            'total_records': len(name_id_mappings)
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return self.supported_formats.copy()