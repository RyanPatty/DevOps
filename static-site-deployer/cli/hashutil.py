"""
Hash utility functions for file comparison.
"""

import hashlib
import os
from typing import Optional


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash as a hex string
    """
    hash_md5 = hashlib.md5()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def get_s3_etag(file_path: str) -> str:
    """
    Calculate the ETag that S3 would use for this file.
    For files smaller than 5GB, this is the same as MD5.
    For larger files, it's the MD5 of the concatenated part MD5s.
    
    Args:
        file_path: Path to the file
        
    Returns:
        ETag string (quoted for multipart uploads)
    """
    file_size = os.path.getsize(file_path)
    
    # For files smaller than 5GB, ETag is just the MD5
    if file_size < 5 * 1024 * 1024 * 1024:  # 5GB
        return f'"{calculate_file_hash(file_path)}"'
    
    # For larger files, we'd need to implement multipart logic
    # For now, just return the MD5 (this is a simplified version)
    return f'"{calculate_file_hash(file_path)}"'


def files_have_same_content(local_path: str, s3_etag: str) -> bool:
    """
    Compare local file hash with S3 ETag.
    
    Args:
        local_path: Path to local file
        s3_etag: ETag from S3 object
        
    Returns:
        True if files have same content, False otherwise
    """
    local_etag = get_s3_etag(local_path)
    return local_etag == s3_etag 