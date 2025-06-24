import pytest
import tempfile
import os
from cli.hashutil import calculate_file_hash


def test_calculate_file_hash():
    """Test that file hash calculation works correctly."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Hello, World!")
        temp_file = f.name
    
    try:
        hash_result = calculate_file_hash(temp_file)
        assert hash_result is not None
        assert len(hash_result) == 32  # MD5 hash is 32 characters
        assert isinstance(hash_result, str)
    finally:
        os.unlink(temp_file)


def test_calculate_file_hash_nonexistent():
    """Test that hash calculation fails gracefully for nonexistent files."""
    with pytest.raises(FileNotFoundError):
        calculate_file_hash("nonexistent_file.txt")


def test_calculate_file_hash_empty():
    """Test that empty files can be hashed."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("")
        temp_file = f.name
    
    try:
        hash_result = calculate_file_hash(temp_file)
        assert hash_result is not None
        assert len(hash_result) == 32
    finally:
        os.unlink(temp_file) 