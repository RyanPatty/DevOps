"""
CloudFront invalidation logic.
"""

from typing import List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init()


class CloudFrontInvalidator:
    """Handles CloudFront cache invalidations."""
    
    def __init__(self, distribution_id: str, aws_profile: str = None):
        """
        Initialize the invalidator.
        
        Args:
            distribution_id: CloudFront distribution ID
            aws_profile: AWS profile to use (optional)
        """
        self.distribution_id = distribution_id
        
        # Initialize CloudFront client
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            self.cf_client = session.client('cloudfront')
        else:
            self.cf_client = boto3.client('cloudfront')
    
    def create_invalidation(self, paths: List[str]) -> str:
        """
        Create a CloudFront invalidation for the given paths.
        
        Args:
            paths: List of paths to invalidate (e.g., ['/index.html', '/css/style.css'])
            
        Returns:
            Invalidation ID
        """
        try:
            # CloudFront requires paths to start with /
            normalized_paths = []
            for path in paths:
                if not path.startswith('/'):
                    path = '/' + path
                normalized_paths.append(path)
            
            # CloudFront allows max 1000 paths per invalidation
            if len(normalized_paths) > 1000:
                print(f"{Fore.YELLOW}Warning: {len(normalized_paths)} paths exceed CloudFront limit of 1000{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Creating multiple invalidations...{Style.RESET_ALL}")
                
                invalidation_ids = []
                for i in range(0, len(normalized_paths), 1000):
                    batch = normalized_paths[i:i+1000]
                    invalidation_id = self._create_single_invalidation(batch)
                    invalidation_ids.append(invalidation_id)
                
                return invalidation_ids
            
            return self._create_single_invalidation(normalized_paths)
            
        except (ClientError, NoCredentialsError) as e:
            print(f"{Fore.RED}Error creating invalidation: {e}{Style.RESET_ALL}")
            raise
    
    def _create_single_invalidation(self, paths: List[str]) -> str:
        """
        Create a single CloudFront invalidation.
        
        Args:
            paths: List of paths to invalidate
            
        Returns:
            Invalidation ID
        """
        try:
            response = self.cf_client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"deploy-{len(paths)}-files-{int(__import__('time').time())}"
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            print(f"{Fore.GREEN}Created invalidation {invalidation_id} for {len(paths)} paths{Style.RESET_ALL}")
            
            return invalidation_id
            
        except (ClientError, NoCredentialsError) as e:
            print(f"{Fore.RED}Error creating invalidation: {e}{Style.RESET_ALL}")
            raise
    
    def wait_for_invalidation(self, invalidation_id: str, timeout: int = 300) -> bool:
        """
        Wait for an invalidation to complete.
        
        Args:
            invalidation_id: Invalidation ID to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if invalidation completed, False if timed out
        """
        import time
        
        print(f"{Fore.CYAN}Waiting for invalidation {invalidation_id} to complete...{Style.RESET_ALL}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.cf_client.get_invalidation(
                    DistributionId=self.distribution_id,
                    Id=invalidation_id
                )
                
                status = response['Invalidation']['Status']
                
                if status == 'Completed':
                    print(f"{Fore.GREEN}Invalidation {invalidation_id} completed successfully{Style.RESET_ALL}")
                    return True
                elif status == 'InProgress':
                    print(f"{Fore.CYAN}Invalidation {invalidation_id} still in progress...{Style.RESET_ALL}")
                    time.sleep(10)  # Wait 10 seconds before checking again
                else:
                    print(f"{Fore.RED}Invalidation {invalidation_id} failed with status: {status}{Style.RESET_ALL}")
                    return False
                    
            except (ClientError, NoCredentialsError) as e:
                print(f"{Fore.RED}Error checking invalidation status: {e}{Style.RESET_ALL}")
                return False
        
        print(f"{Fore.YELLOW}Timeout waiting for invalidation {invalidation_id}{Style.RESET_ALL}")
        return False 