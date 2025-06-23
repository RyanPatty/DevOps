"""
S3 upload logic for delta uploads.
"""

import os
from pathlib import Path
from typing import List, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tqdm import tqdm
import colorama
from colorama import Fore, Style

from .hashutil import files_have_same_content

# Initialize colorama for cross-platform colored output
colorama.init()


class S3Uploader:
    """Handles S3 uploads with delta detection."""
    
    def __init__(self, bucket_name: str, aws_profile: str = None):
        """
        Initialize the uploader.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_profile: AWS profile to use (optional)
        """
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            self.s3_client = session.client('s3')
        else:
            self.s3_client = boto3.client('s3')
    
    def get_s3_object_etag(self, key: str) -> str:
        """
        Get ETag of an S3 object.
        
        Args:
            key: S3 object key
            
        Returns:
            ETag string, or None if object doesn't exist
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return response['ETag']
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise
    
    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3 if it has changed.
        
        Args:
            local_path: Path to local file
            s3_key: S3 object key
            
        Returns:
            True if file was uploaded, False if skipped
        """
        try:
            # Get S3 object ETag
            s3_etag = self.get_s3_object_etag(s3_key)
            
            # Check if file has changed
            if s3_etag and files_have_same_content(local_path, s3_etag):
                print(f"{Fore.YELLOW}Skipping{Style.RESET_ALL} {s3_key} (no changes)")
                return False
            
            # Upload file
            print(f"{Fore.GREEN}Uploading{Style.RESET_ALL} {s3_key}")
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            return True
            
        except (ClientError, NoCredentialsError) as e:
            print(f"{Fore.RED}Error uploading {s3_key}: {e}{Style.RESET_ALL}")
            raise
    
    def upload_directory(self, local_dir: str, dry_run: bool = False) -> Tuple[List[str], List[str]]:
        """
        Upload all files in a directory to S3.
        
        Args:
            local_dir: Path to local directory
            dry_run: If True, only show what would be uploaded
            
        Returns:
            Tuple of (uploaded_files, skipped_files)
        """
        local_path = Path(local_dir)
        if not local_path.exists():
            raise FileNotFoundError(f"Directory not found: {local_dir}")
        
        uploaded_files = []
        skipped_files = []
        
        # Find all files in directory
        all_files = []
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)
        
        if dry_run:
            print(f"{Fore.CYAN}DRY RUN: Would process {len(all_files)} files{Style.RESET_ALL}")
        
        # Process files with progress bar
        with tqdm(total=len(all_files), desc="Processing files") as pbar:
            for file_path in all_files:
                # Calculate S3 key (relative path from local_dir)
                relative_path = file_path.relative_to(local_path)
                s3_key = str(relative_path).replace('\\', '/')  # Normalize path separators
                
                if dry_run:
                    s3_etag = self.get_s3_object_etag(s3_key)
                    if s3_etag and files_have_same_content(str(file_path), s3_etag):
                        print(f"{Fore.YELLOW}Would skip{Style.RESET_ALL} {s3_key}")
                        skipped_files.append(s3_key)
                    else:
                        print(f"{Fore.GREEN}Would upload{Style.RESET_ALL} {s3_key}")
                        uploaded_files.append(s3_key)
                else:
                    try:
                        if self.upload_file(str(file_path), s3_key):
                            uploaded_files.append(s3_key)
                        else:
                            skipped_files.append(s3_key)
                    except Exception as e:
                        print(f"{Fore.RED}Failed to process {s3_key}: {e}{Style.RESET_ALL}")
                        raise
                
                pbar.update(1)
        
        return uploaded_files, skipped_files 