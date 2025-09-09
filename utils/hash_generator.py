"""
Hash generation utilities for creating unique IDs from names
"""

import hashlib
from typing import List, Dict, Optional
import uuid
from config import HASH_ALGORITHM, SALT_ENABLED, DEFAULT_SALT


class HashGenerator:
    """Generates MD5 hashes and other unique identifiers for names"""
    
    def __init__(self, algorithm: str = HASH_ALGORITHM, salt: str = DEFAULT_SALT):
        self.algorithm = algorithm
        self.salt = salt
        self.hash_cache = {}  # Cache to ensure consistent hashing
    
    def generate_hash(self, name: str) -> str:
        """
        Generate hash for a single name
        
        Args:
            name: Name to hash
            
        Returns:
            Hexadecimal hash string
        """
        # Use cache to ensure same name always gets same hash
        if name in self.hash_cache:
            return self.hash_cache[name]
        
        # Prepare the string to hash
        hash_input = name.strip().lower()
        
        # Add salt if enabled
        if SALT_ENABLED and self.salt:
            hash_input = f"{self.salt}{hash_input}"
        
        # Generate hash
        if self.algorithm == 'md5':
            hash_obj = hashlib.md5(hash_input.encode('utf-8'))
        elif self.algorithm == 'sha256':
            hash_obj = hashlib.sha256(hash_input.encode('utf-8'))
        elif self.algorithm == 'sha1':
            hash_obj = hashlib.sha1(hash_input.encode('utf-8'))
        else:
            # Default to MD5
            hash_obj = hashlib.md5(hash_input.encode('utf-8'))
        
        hash_value = hash_obj.hexdigest()
        
        # Cache the result
        self.hash_cache[name] = hash_value
        
        return hash_value
    
    def generate_hashes_batch(self, names: List[str]) -> Dict[str, str]:
        """
        Generate hashes for a batch of names
        
        Args:
            names: List of names to hash
            
        Returns:
            Dictionary mapping names to their hashes
        """
        hashes = {}
        
        for name in names:
            hashes[name] = self.generate_hash(name)
        
        return hashes
    
    def generate_unique_hash(self, name: str, existing_hashes: set) -> str:
        """
        Generate a unique hash that doesn't conflict with existing ones
        
        Args:
            name: Name to hash
            existing_hashes: Set of existing hash values
            
        Returns:
            Unique hash string
        """
        base_hash = self.generate_hash(name)
        
        # If no conflict, return the base hash
        if base_hash not in existing_hashes:
            return base_hash
        
        # If there's a conflict, append a counter
        counter = 1
        while True:
            modified_name = f"{name}_{counter}"
            new_hash = self.generate_hash(modified_name)
            
            if new_hash not in existing_hashes:
                return new_hash
            
            counter += 1
            
            # Safety check to prevent infinite loops
            if counter > 1000:
                # Generate a random UUID as fallback
                return str(uuid.uuid4()).replace('-', '')
    
    def generate_sequential_ids(self, names: List[str], prefix: str = "ID") -> Dict[str, str]:
        """
        Generate sequential IDs instead of hashes
        
        Args:
            names: List of names
            prefix: Prefix for IDs (default: "ID")
            
        Returns:
            Dictionary mapping names to sequential IDs
        """
        ids = {}
        
        for i, name in enumerate(names, 1):
            # Format: ID001, ID002, etc.
            sequential_id = f"{prefix}{i:03d}"
            ids[name] = sequential_id
        
        return ids
    
    def create_name_id_mapping(self, names: List[str], id_type: str = "hash") -> List[Dict]:
        """
        Create complete name-to-ID mapping
        
        Args:
            names: List of names
            id_type: Type of ID to generate ("hash", "sequential", "uuid")
            
        Returns:
            List of dictionaries with name and ID pairs
        """
        mappings = []
        existing_ids = set()
        
        for name in names:
            if id_type == "hash":
                id_value = self.generate_unique_hash(name, existing_ids)
            elif id_type == "sequential":
                id_value = f"ID{len(mappings) + 1:03d}"
            elif id_type == "uuid":
                id_value = str(uuid.uuid4())
            else:
                # Default to hash
                id_value = self.generate_unique_hash(name, existing_ids)
            
            existing_ids.add(id_value)
            
            mappings.append({
                'Name': name,
                'ID': id_value
            })
        
        return mappings
    
    def verify_hash_uniqueness(self, name_hash_pairs: List[Dict]) -> Dict:
        """
        Verify that all generated hashes are unique
        
        Args:
            name_hash_pairs: List of name-hash dictionaries
            
        Returns:
            Dictionary with verification results
        """
        hash_counts = {}
        duplicates = []
        
        for pair in name_hash_pairs:
            hash_value = pair.get('ID', '')
            
            if hash_value in hash_counts:
                hash_counts[hash_value].append(pair['Name'])
                if hash_value not in [d['hash'] for d in duplicates]:
                    duplicates.append({
                        'hash': hash_value,
                        'names': hash_counts[hash_value]
                    })
            else:
                hash_counts[hash_value] = [pair['Name']]
        
        return {
            'is_unique': len(duplicates) == 0,
            'total_hashes': len(name_hash_pairs),
            'unique_hashes': len([h for h, names in hash_counts.items() if len(names) == 1]),
            'duplicate_hashes': len(duplicates),
            'duplicates': duplicates
        }
    
    def get_hash_statistics(self, hashes: List[str]) -> Dict:
        """Get statistics about generated hashes"""
        if not hashes:
            return {}
        
        hash_lengths = [len(h) for h in hashes]
        
        return {
            'total_hashes': len(hashes),
            'unique_hashes': len(set(hashes)),
            'average_length': sum(hash_lengths) / len(hash_lengths) if hashes else 0,
            'min_length': min(hash_lengths) if hash_lengths else 0,
            'max_length': max(hash_lengths) if hash_lengths else 0,
            'algorithm_used': self.algorithm,
            'salt_enabled': SALT_ENABLED
        }
    
    def clear_cache(self):
        """Clear the hash cache"""
        self.hash_cache.clear()
    
    def set_salt(self, salt: str):
        """Set a new salt and clear cache"""
        self.salt = salt
        self.clear_cache()