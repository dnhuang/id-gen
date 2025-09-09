"""
ID Generator - Streamlit Web Application
Converts names from CSV, TXT, or XLSX files to MD5 hash mappings
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import time

# Import utility modules
from utils.file_parser import FileParser
from utils.name_processor import NameProcessor
from utils.hash_generator import HashGenerator
from utils.export_manager import ExportManager
from config import *

# Configure Streamlit page
st.set_page_config(
    page_title="ID Generator",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'names_list' not in st.session_state:
    st.session_state.names_list = []
if 'name_id_mappings' not in st.session_state:
    st.session_state.name_id_mappings = []


def main():
    """Main application function"""
    
    # Initialize utility classes
    file_parser = FileParser()
    name_processor = NameProcessor()
    hash_generator = HashGenerator()
    export_manager = ExportManager()
    
    # Application header
    st.title("ID Generator")
    
    st.markdown("---")
    
    # Step 1: File Upload
    if st.session_state.step == 1:
        step_1_file_upload(file_parser)
    
    # Step 2: Review, Configure, and Process (Combined step)
    elif st.session_state.step == 2:
        step_2_review_configure_generate(name_processor, hash_generator)
    
    # Step 3: Download Results
    elif st.session_state.step == 3:
        step_3_download_results(export_manager)


def step_1_file_upload(file_parser: FileParser):
    """Step 1: File Upload Interface"""
    
    st.header("File Upload")
    
    # Add description of supported file types
    st.markdown("""
    **Supported file formats:**
    - **CSV files**: Names separated by commas or newlines
    - **TXT files**: Names separated by commas or newlines
    - **Excel files (.xlsx)**: Must contain a column named 'Name', 'Subject', or 'Trial' (checked in that priority order, case-insensitive)
    """)
    
    # File upload widget
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'txt', 'xlsx'],
        help="Upload your file containing names to generate unique IDs"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = file_parser.validate_file(uploaded_file)
        
        if not is_valid:
            st.error(message)
            return
        
        st.success(message)
        
        # Parse file
        with st.spinner("Parsing file..."):
            names, parse_message = file_parser.parse_file(uploaded_file)
        
        if names:
            st.success(parse_message)
            
            # Preview extracted names
            st.subheader("Preview")
            preview_df = pd.DataFrame({'Names': names[:10]})  # Show first 10
            st.dataframe(preview_df, width="stretch")
            
            if len(names) > 10:
                st.info(f"Showing first 10 names. Total extracted: {len(names)}")
            
            # Store in session state and proceed
            st.session_state.uploaded_file = uploaded_file
            st.session_state.names_list = names
        else:
            st.error(parse_message)
    
    # Always show Review & Configure button
    if st.button("Review & Configure →", width="stretch"):
        # If no file uploaded, ask for confirmation to proceed with manual configuration
        if uploaded_file is None:
            st.session_state.show_manual_confirm = True
            st.rerun()
        else:
            st.session_state.step = 2
            st.rerun()
    
    # Show confirmation dialog if needed
    if st.session_state.get('show_manual_confirm', False):
        # Auto-hide confirmation if file is uploaded
        if uploaded_file is not None:
            st.session_state.show_manual_confirm = False
            st.rerun()
        
        st.warning("⚠️ No file uploaded. Do you want to proceed with manual configuration?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", width="stretch"):
                st.session_state.show_manual_confirm = False
                st.rerun()
        with col2:
            if st.button("Manual Setup →", width="stretch"):
                st.session_state.names_list = []  # Empty list for manual entry
                st.session_state.show_manual_confirm = False
                st.session_state.step = 2
                st.rerun()


def step_2_review_configure_generate(name_processor: NameProcessor, hash_generator: HashGenerator):
    """Step 2: Combined Review, Configure, and Generate"""
    
    st.header("Review & Configure")
    
    # Process names for duplicates and validation
    if st.session_state.names_list:
        # Process uploaded names
        with st.spinner("Processing names..."):
            processed_data = name_processor.process_names(st.session_state.names_list)
        
        # Initialize editable names if not exists
        if 'editable_names' not in st.session_state:
            st.session_state.editable_names = [{'Name': name} for name in processed_data['all_cleaned_names']]
    else:
        # Manual configuration - start with empty list
        processed_data = {
            'all_cleaned_names': [],
            'invalid_count': 0,
            'duplicates': []
        }
        
        # Initialize editable names if not exists
        if 'editable_names' not in st.session_state:
            st.session_state.editable_names = [{'Name': ''}]  # Start with one empty field
    
    # Get current names and find duplicates (recalculate dynamically)
    current_names = [item['Name'].strip() for item in st.session_state.editable_names if item['Name'].strip()]
    name_counts = {}
    for name in current_names:
        name_counts[name] = name_counts.get(name, 0) + 1
    
    # Show duplicate warning at the top (dynamically updated)
    duplicate_names = [name for name, count in name_counts.items() if count > 1 and name]
    if duplicate_names:
        st.warning(f"⚠️ {len(duplicate_names)} duplicates found.")
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Names", len(current_names))
    with col2:
        st.metric("Unique Names", len(set(current_names)))
    with col3:
        st.metric("Duplicates Found", len(duplicate_names))
    with col4:
        st.metric("Invalid Names", processed_data['invalid_count'])
    
    # Names editor section
    st.subheader("Edit")
    
    # Add CSS for custom button styling
    st.markdown("""
    <style>
    /* Custom styling for buttons */
    .stButton > button {
        transition: all 0.3s ease !important;
    }
    
    /* Green hover for generate button */
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
    }
    
    /* Orange hover for back button */
    button:contains("←"):hover,
    .stButton button[title*="back"]:hover {
        background-color: #ff8c00 !important;
        color: white !important;
        border-color: #ff8c00 !important;
    }
    
    /* Try targeting by button text content */
    .stButton button:hover {
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create editable list with clean layout
    names_to_remove = []
    
    for i, name_dict in enumerate(st.session_state.editable_names):
        # Check if this name is a duplicate
        is_duplicate = name_counts.get(name_dict['Name'].strip(), 0) > 1 and name_dict['Name'].strip() != ""
        
        # Create columns: input field, delete+warning together
        col1, col2 = st.columns([4, 1])
                
        with col1:
            new_name = st.text_input(
                f"Name {i+1}",
                value=name_dict['Name'],
                key=f"name_input_{i}",
                label_visibility="collapsed",
                help="Duplicate name" if is_duplicate else None
            )
            st.session_state.editable_names[i]['Name'] = new_name
            
        with col2:
            # Create button text with warning icon and tiny space
            button_text = "🗑️ ⚠️" if is_duplicate else "🗑️"
            if st.button(button_text, key=f"remove_{i}", help="Remove this name" + (" (duplicate)" if is_duplicate else "")):
                names_to_remove.append(i)
    
    # Add Name button below all cells
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("➕", key="add_name_button", help="Add a new name"):
            st.session_state.editable_names.append({'Name': ''})
            st.rerun()
    with col2:
        st.markdown("&nbsp;", unsafe_allow_html=True)  # Empty space
    
    # Remove names that were marked for removal
    for i in reversed(names_to_remove):
        st.session_state.editable_names.pop(i)
        st.rerun()
    
    # Get final names list (filter out empty names)
    final_names = [item['Name'].strip() for item in st.session_state.editable_names if item['Name'].strip()]
    
    # Configuration section
    st.subheader("Configurations")
    
    id_type = st.selectbox(
        "ID Generation Method",
        options=['hash', 'sequential', 'uuid'],
        format_func=lambda x: {
            'hash': 'MD5 Hash (recommended)',
            'sequential': 'Sequential (ID001, ID002, ...)',
            'uuid': 'UUID (random unique)'
        }[x]
    )
    
    if id_type == 'hash':
        algorithm = st.selectbox("Hash Algorithm", options=['md5', 'sha256', 'sha1'])
        salt = ""  # Removed salt option
    
    # Generate IDs button
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", width="stretch", key="back_button"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Generate IDs →", width="stretch", key="generate_button"):
            if not final_names:
                st.error("No names to process!")
                return
            
            # Configure hash generator
            if id_type == 'hash':
                hash_generator.algorithm = algorithm
            
            # Generate IDs for ALL names (including duplicates)
            with st.spinner(f"Generating IDs for all {len(final_names)} names..."):
                progress_bar = st.progress(0)
                mappings = []
                
                for i, name in enumerate(final_names):
                    if id_type == 'hash':
                        # For duplicates, we want each instance to have the same hash
                        id_value = hash_generator.generate_hash(name)
                    elif id_type == 'sequential':
                        id_value = f"ID{i+1:03d}"
                    elif id_type == 'uuid':
                        import uuid
                        id_value = str(uuid.uuid4())
                    
                    mappings.append({
                        'Name': name,
                        'ID': id_value
                    })
                    
                    progress_bar.progress((i + 1) / len(final_names))
                
                st.session_state.name_id_mappings = mappings
            
            st.success(f"✅ Generated IDs for ALL {len(mappings)} names!")
            
            # Skip preview and go directly to next step
            st.session_state.step = 3
            st.rerun()


def step_3_download_results(export_manager: ExportManager):
    """Step 3: Download Results"""
    
    st.header("File Download")
    
    if not st.session_state.name_id_mappings:
        st.error("No mappings to download!")
        return
    
    mappings = st.session_state.name_id_mappings
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(mappings))
    with col2:
        unique_names = len(set(m['Name'] for m in mappings))
        st.metric("Unique Names", unique_names)
    with col3:
        unique_ids = len(set(m['ID'] for m in mappings))
        st.metric("Unique IDs", unique_ids)
    
    # Download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_manager.create_download_data(mappings, 'csv')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data['data'],
            file_name=csv_data['filename'],
            mime=csv_data['mime_type'],
            type="primary",
            width="stretch"
        )
    
    with col2:
        xlsx_data = export_manager.create_download_data(mappings, 'xlsx')
        st.download_button(
            label="⬇️ Download Excel",
            data=xlsx_data['data'],
            file_name=xlsx_data['filename'],
            mime=xlsx_data['mime_type'],
            type="primary",
            width="stretch"
        )
    
    # Full results preview
    st.subheader("Preview")
    full_df = pd.DataFrame(mappings)
    st.dataframe(full_df, width="stretch", height=400)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", width="stretch"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Start Over 🔄", width="stretch"):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key != 'step':
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()


if __name__ == "__main__":
    main()