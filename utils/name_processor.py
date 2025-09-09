"""
Name processing utilities for validation, cleaning, and duplicate detection
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter


class NameProcessor:
    """Handles name validation, cleaning, and duplicate detection"""
    
    def __init__(self):
        self.processed_names = []
        self.duplicates = {}
        self.name_counts = Counter()
    
    def process_names(self, names: List[str]) -> Dict:
        """
        Process list of names and detect duplicates
        
        Args:
            names: List of names to process
            
        Returns:
            Dictionary containing processing results
        """
        # Reset state
        self.processed_names = []
        self.duplicates = {}
        self.name_counts = Counter()
        
        # Clean and validate names
        cleaned_names = []
        invalid_names = []
        
        for name in names:
            cleaned = self._clean_name(name)
            if self._validate_name(cleaned):
                cleaned_names.append(cleaned)
            else:
                invalid_names.append(name)
        
        # Count occurrences and identify duplicates
        self.name_counts = Counter(cleaned_names)
        
        # Separate unique and duplicate names
        unique_names = []
        duplicate_groups = {}
        
        for name, count in self.name_counts.items():
            if count == 1:
                unique_names.append(name)
            else:
                # Group duplicates
                if name not in duplicate_groups:
                    duplicate_groups[name] = {
                        'name': name,
                        'count': count,
                        'indices': []
                    }
                
                # Find all indices of this duplicate name
                indices = [i for i, n in enumerate(cleaned_names) if n == name]
                duplicate_groups[name]['indices'] = indices
        
        self.duplicates = duplicate_groups
        
        return {
            'unique_names': unique_names,
            'duplicate_groups': duplicate_groups,
            'invalid_names': invalid_names,
            'total_names': len(cleaned_names),
            'unique_count': len(unique_names),
            'duplicate_count': len(duplicate_groups),
            'invalid_count': len(invalid_names),
            'all_cleaned_names': cleaned_names
        }
    
    def _clean_name(self, name: str) -> str:
        """Clean individual name"""
        if not name:
            return ""
        
        # Convert to string and strip whitespace
        name = str(name).strip()
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Remove leading/trailing punctuation (but keep internal punctuation like O'Connor)
        name = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', name)
        
        # Title case for proper names
        name = name.title()
        
        return name
    
    def _validate_name(self, name: str) -> bool:
        """Validate if string is a valid name"""
        if not name or len(name.strip()) < 1:
            return False
        
        # Check if it's only numbers
        if name.isdigit():
            return False
        
        # Check if it's only special characters
        if re.match(r'^[^\w\s]+$', name):
            return False
        
        # Check minimum length
        if len(name) < 2:
            return False
        
        # Check if it contains at least one letter
        if not re.search(r'[a-zA-Z]', name):
            return False
        
        return True
    
    def get_duplicate_summary(self) -> Dict:
        """Get summary of duplicate analysis"""
        if not self.duplicates:
            return {
                'has_duplicates': False,
                'duplicate_count': 0,
                'duplicate_names': [],
                'total_duplicate_entries': 0
            }
        
        total_entries = sum(group['count'] for group in self.duplicates.values())
        duplicate_names = list(self.duplicates.keys())
        
        return {
            'has_duplicates': True,
            'duplicate_count': len(self.duplicates),
            'duplicate_names': duplicate_names,
            'total_duplicate_entries': total_entries,
            'duplicate_groups': self.duplicates
        }
    
    def resolve_duplicates(self, resolution_choices: Dict[str, str]) -> List[str]:
        """
        Resolve duplicates based on user choices
        
        Args:
            resolution_choices: Dict mapping duplicate name to choice ('keep_one', 'keep_all', 'remove_all')
            
        Returns:
            Final list of names after duplicate resolution
        """
        final_names = []
        
        # Add all unique names (no duplicates)
        unique_names = [name for name, count in self.name_counts.items() if count == 1]
        final_names.extend(unique_names)
        
        # Process duplicate groups based on user choices
        for duplicate_name, choice in resolution_choices.items():
            if duplicate_name in self.duplicates:
                if choice == 'keep_one':
                    final_names.append(duplicate_name)
                elif choice == 'keep_all':
                    count = self.duplicates[duplicate_name]['count']
                    final_names.extend([duplicate_name] * count)
                # 'remove_all' means we don't add anything
        
        return final_names
    
    def get_name_statistics(self, names: List[str]) -> Dict:
        """Get statistics about the names"""
        if not names:
            return {}
        
        # Length statistics
        lengths = [len(name) for name in names]
        
        # Word count statistics
        word_counts = [len(name.split()) for name in names]
        
        # Character analysis
        total_chars = sum(lengths)
        avg_length = total_chars / len(names) if names else 0
        
        return {
            'total_names': len(names),
            'average_length': round(avg_length, 1),
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'single_word_names': sum(1 for wc in word_counts if wc == 1),
            'multi_word_names': sum(1 for wc in word_counts if wc > 1),
            'longest_name': max(names, key=len) if names else "",
            'shortest_name': min(names, key=len) if names else ""
        }
    
    def suggest_corrections(self, names: List[str]) -> Dict[str, List[str]]:
        """
        Suggest corrections for potentially misspelled names
        Note: This is a basic implementation. In production, you might use
        a more sophisticated spell checker or name database.
        """
        suggestions = {}
        
        # Common name patterns and corrections
        common_corrections = {
            r'\bmike\b': 'Michael',
            r'\bbob\b': 'Robert',
            r'\bjoe\b': 'Joseph',
            r'\btom\b': 'Thomas',
            r'\bbill\b': 'William',
            r'\bdave\b': 'David',
            r'\bsteve\b': 'Steven',
            r'\bchris\b': 'Christopher'
        }
        
        for name in names:
            original_name = name
            suggested_name = name.lower()
            
            # Apply common corrections
            for pattern, correction in common_corrections.items():
                if re.search(pattern, suggested_name, re.IGNORECASE):
                    suggested_name = re.sub(pattern, correction, suggested_name, flags=re.IGNORECASE)
                    suggested_name = suggested_name.title()
                    
                    if suggested_name != original_name:
                        if original_name not in suggestions:
                            suggestions[original_name] = []
                        suggestions[original_name].append(suggested_name)
        
        return suggestions