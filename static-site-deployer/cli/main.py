"""
Main CLI entry point for deploy_site command.
"""

import os
import sys
from typing import Optional
import click
import colorama
from colorama import Fore, Style

from .uploader import S3Uploader
from .invalidate import CloudFrontInvalidator

# Initialize colorama for cross-platform colored output
colorama.init()


@click.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--bucket', envvar='DEPLOY_BUCKET', help='S3 bucket name')
@click.option('--dist-id', envvar='CF_DIST_ID', help='CloudFront distribution ID')
@click.option('--profile', help='AWS profile to use')
@click.option('--dry-run', is_flag=True, help='Show what would be uploaded without making changes')
@click.option('--wait', is_flag=True, help='Wait for CloudFront invalidation to complete')
def cli(folder: str, bucket: Optional[str], dist_id: Optional[str], 
        profile: Optional[str], dry_run: bool, wait: bool):
    """
    Deploy static site files to S3 and invalidate CloudFront cache.
    
    FOLDER: Path to directory containing static site files
    """
    try:
        # Validate required parameters
        if not bucket:
            click.echo(f"{Fore.RED}Error: S3 bucket name required. Use --bucket or set DEPLOY_BUCKET env var.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        if not dist_id:
            click.echo(f"{Fore.RED}Error: CloudFront distribution ID required. Use --dist-id or set CF_DIST_ID env var.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        # Initialize uploader and invalidator
        uploader = S3Uploader(bucket, profile)
        invalidator = CloudFrontInvalidator(dist_id, profile)
        
        click.echo(f"{Fore.CYAN}Deploying {folder} to S3 bucket: {bucket}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}CloudFront distribution: {dist_id}{Style.RESET_ALL}")
        
        if dry_run:
            click.echo(f"{Fore.YELLOW}DRY RUN MODE - No changes will be made{Style.RESET_ALL}")
        
        # Upload files
        uploaded_files, skipped_files = uploader.upload_directory(folder, dry_run)
        
        # Summary
        click.echo(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        click.echo(f"  Uploaded: {len(uploaded_files)} files")
        click.echo(f"  Skipped: {len(skipped_files)} files")
        
        if not dry_run and uploaded_files:
            # Create CloudFront invalidation for uploaded files
            click.echo(f"\n{Fore.CYAN}Creating CloudFront invalidation...{Style.RESET_ALL}")
            
            try:
                invalidation_id = invalidator.create_invalidation(uploaded_files)
                
                if wait:
                    # Wait for invalidation to complete
                    success = invalidator.wait_for_invalidation(invalidation_id)
                    if not success:
                        click.echo(f"{Fore.YELLOW}Warning: Invalidation may still be in progress{Style.RESET_ALL}")
                
                click.echo(f"{Fore.GREEN}Deployment completed successfully!{Style.RESET_ALL}")
                click.echo(f"{Fore.GREEN}Invalidation ID: {invalidation_id}{Style.RESET_ALL}")
                
            except Exception as e:
                click.echo(f"{Fore.RED}Error creating CloudFront invalidation: {e}{Style.RESET_ALL}", err=True)
                sys.exit(2)
        
        elif dry_run:
            click.echo(f"\n{Fore.YELLOW}DRY RUN: Would create invalidation for {len(uploaded_files)} files{Style.RESET_ALL}")
        
        else:
            click.echo(f"\n{Fore.GREEN}No files uploaded - no invalidation needed{Style.RESET_ALL}")
        
        # Exit with success
        sys.exit(0)
        
    except FileNotFoundError as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(2)


if __name__ == '__main__':
    cli() 