# Static-Site Deployer CLI - Progress Tracking

## ✅ Completed Steps

### Step 0 - Prep your workstation (Windows Edition)
- ✅ **Environment Check**: Confirmed PowerShell execution policy is `RemoteSigned`
- ✅ **Package Manager**: Chocolatey v2.2.2 already installed
- ✅ **Tools Inventory**: 
  - Python 3.12.1 ✅
  - AWS CLI 2.15.15 ✅
  - Node.js v20.10.0 ✅
  - Git 2.42.0 ✅
  - Terraform v1.12.2 ✅ (just installed)
  - jq ✅ (installed via Chocolatey)
- ✅ **Project Setup**: Created `static-site-deployer` directory
- ✅ **Git Init**: Git repository already initialized with main branch

### Step 1 - Python environment
- ✅ **Virtual Environment**: Created `.venv` using `python -m venv .venv`
- ✅ **Activation**: Activated virtual environment with `.venv\Scripts\Activate.ps1`
- ✅ **Python Version**: Confirmed Python 3.12.1 in virtual environment
- ✅ **Gitignore Setup**: Created comprehensive `.gitignore` to prevent committing virtual environment files
- ✅ **Virtual Environment Recreation**: Recreated `.venv` after cleanup to avoid Git issues

### Step 2 - Basic repo scaffold
- ✅ **Folder Structure**: Created `cli/`, `infra/`, `.github/workflows/`, `site-sample/` directories
- ✅ **Python Package**: Created `cli/__init__.py` to make cli a Python package
- ✅ **Documentation**: Created `README.md` and `REQUIREMENTS.md` files
- ✅ **Sample Site**: Created `site-sample/index.html` with "Hello world" content
- ✅ **Git Commit**: Committed scaffold with message "chore: scaffold repo"

### Step 3 - AWS account bootstrap
- ✅ **AWS Authentication**: Initially logged in as `ryan_admin` IAM user
- ✅ **IAM User Setup**: Created new IAM user `ryan_dev_home` with appropriate permissions
- ✅ **Access Keys**: Generated programmatic access keys for CLI usage
- ✅ **Profile Configuration**: Set up AWS CLI profile `ryan_dev_home` with credentials
- ✅ **Authentication Test**: Confirmed `ryan_dev_home` profile is working correctly
- ✅ **S3 Bucket**: Created `ryan-static-site-deployer-tf-state` for Terraform state storage (in correct account 296950653587)
- ✅ **DynamoDB Table**: Created `tf-state-lock` table for Terraform state locking
- ✅ **Backend Config**: Created `infra/backend.tf` with remote state configuration
- ✅ **Git Commit**: Committed backend configuration with message "infra: add remote backend"

### Step 4 - Terraform installation
- ✅ **Terraform Install**: Installed Terraform v1.12.2 via Chocolatey
- ✅ **Environment Setup**: Imported Chocolatey profile module for PATH updates
- ✅ **Version Test**: Confirmed Terraform is working correctly

### Step 5 - Create S3 bucket & CloudFront (COMPLETED)
- ✅ **Terraform Infrastructure**: Created `infra/main.tf` with S3 bucket and CloudFront distribution
- ✅ **Terraform Plan**: Successfully planned infrastructure with 6 resources
- ✅ **Terraform Apply**: Successfully created all AWS resources
- ✅ **S3 Bucket**: `ryan-static-site-deployer` created with versioning and website hosting
- ✅ **CloudFront Distribution**: `E2U98SO9UWJ7JS` created with Origin Access Control
- ✅ **CloudFront URL**: `https://d2ckbhbg0ietbn.cloudfront.net`
- ✅ **S3 Website URL**: `ryan-static-site-deployer.s3-website-us-east-1.amazonaws.com`
- ✅ **S3 Bucket Policy**: Added policy to allow CloudFront access via Origin Access Control
- ✅ **CloudFront Access Fix**: Resolved "Access Denied" error by adding missing bucket policy

### Step 6 - IAM OIDC role (GitHub) (PENDING)
- 🔄 **Next**: Create `infra/oidc.tf` for GitHub Actions OIDC role

### Step 7 - Local Secrets (COMPLETED)
- ✅ **Environment Variables**: Set up PowerShell environment variables
- ✅ **DEPLOY_BUCKET**: `ryan-static-site-deployer`
- ✅ **CF_DIST_ID**: `E2U98SO9UWJ7JS`
- ✅ **CF_URL**: `https://d2ckbhbg0ietbn.cloudfront.net`

### Step 8 - Python package skeleton (COMPLETED)
- ✅ **pyproject.toml**: Created with all required dependencies (boto3, click, tqdm, colorama)
- ✅ **Package Installation**: Successfully installed with `pip install -e .`
- ✅ **Console Script**: `deploy_site = "cli.main:cli"` configured

### Step 9 - CLI hash & upload logic (COMPLETED)
- ✅ **cli/hashutil.py**: Created file hash comparison utilities
- ✅ **cli/uploader.py**: Created S3 upload logic with delta detection
- ✅ **Hash Comparison**: MD5 hash comparison with S3 ETags
- ✅ **Progress Bar**: TQDM integration for file processing
- ✅ **Colored Output**: Colorama integration for cross-platform colors

### Step 10 - CloudFront invalidation logic (COMPLETED)
- ✅ **cli/invalidate.py**: Created CloudFront invalidation logic
- ✅ **Path Normalization**: Automatic `/` prefix for CloudFront paths
- ✅ **Batch Processing**: Handles >1000 paths with multiple invalidations
- ✅ **Invalidation Tracking**: Wait for invalidation completion

### Step 11 - Entry-point script (COMPLETED)
- ✅ **cli/main.py**: Created main CLI entry point with Click framework
- ✅ **CLI Flags**: Implemented all required flags (--bucket, --dist-id, --dry-run, --wait)
- ✅ **Environment Variables**: Support for DEPLOY_BUCKET and CF_DIST_ID env vars
- ✅ **Exit Codes**: Proper exit codes (0=success, 1=arg error, 2=AWS error)
- ✅ **Dry Run Mode**: Full dry-run implementation
- ✅ **Error Handling**: Comprehensive error handling and user feedback

## 🔄 Current Status
- **Current Step**: Step 12 (Lighthouse manual sanity check)
- **Working Directory**: `C:\Users\Ryan\Desktop\Work\BriteSystems\DevOps\static-site-deployer`
- **Virtual Environment**: ✅ Active and working
- **AWS Profile**: `ryan_dev_home` configured and tested
- **Terraform**: ✅ Infrastructure created successfully
- **Python CLI**: ✅ Fully functional with all components
- **jq**: ✅ Installed and available
- **Documentation**: ✅ Updated README and created howTo.md

## 📋 Next Steps (According to Plan)
1. **Step 12**: Lighthouse manual sanity check (in progress)
2. **Step 6**: Create IAM OIDC role for GitHub Actions (`infra/oidc.tf`)
3. **Step 13**: GitHub Secrets/Vars setup
4. **Step 14**: GitHub Actions workflow
5. **Step 15**: Push and test pipeline

## 🚀 CLI Testing Status
- ✅ **deploy_site --help**: Working
- ✅ **deploy_site site-sample --dry-run**: Working with AWS profile
- ✅ **deploy_site site-sample**: Working with actual deployment
- ✅ **Actual deployment**: Successfully deployed to CloudFront
- ✅ **CloudFront invalidation**: Working (ID: I3RQYWATE9JM8FE1ZCJVKF0TG3)
- ✅ **Hash comparison**: Working (skips unchanged files)
- ✅ **Error handling**: Working (403 errors handled properly with profile)

## 📚 Documentation Status
- ✅ **README.md**: Updated with current progress and accurate information
- ✅ **howTo.md**: Created comprehensive build and usage guide
- ✅ **thingsWeDid.md**: Updated with current progress
- ✅ **PLAN.md**: Updated with .gitignore notes

## 🛠️ Windows-Specific Adaptations Made
- Using PowerShell instead of bash
- Using `python -m venv` instead of pyenv
- Windows path separators (`\`)
- PowerShell environment variable syntax (`$env:VARIABLE_NAME`)
- Chocolatey package management
- AWS CLI profile configuration for Windows
- Chocolatey profile module import for PATH updates

## 🔐 AWS Setup Notes
- **Account**: 296950653587 (correct account for IAM user)
- **IAM User**: ryan_dev_home (newly created)
- **Profile**: ryan_dev_home (configured in AWS CLI)
- **S3 Bucket**: ryan-static-site-deployer-tf-state (for Terraform state, in correct account)
- **DynamoDB Table**: tf-state-lock (for Terraform state locking)
- **Permissions**: Full access granted (`"Action": "*"`)

## 🏗️ Infrastructure Architecture Explained

### Why Terraform Remote State?

**The Problem:**
- Terraform needs to remember what resources it created (S3 buckets, CloudFront, etc.)
- By default, Terraform stores this info in a local file called `terraform.tfstate`
- If you put this file in Git, you're storing sensitive info (resource IDs, etc.) in your repo
- If multiple people work on the project, they could overwrite each other's changes

**The Solution:**
- Store the state file in S3 (remote storage) instead of locally
- Use DynamoDB to "lock" the state so only one person can run Terraform at a time
- This way:
  - ✅ No sensitive files in Git
  - ✅ Team can collaborate safely
  - ✅ State is backed up in AWS
  - ✅ You can see what resources exist even if you delete your local files

**What we're building:**
```
Your Local Files → Terraform → AWS Resources
     ↓
Terraform State (stored in S3)
     ↓
Lock Table (DynamoDB prevents conflicts)
```

**So the S3 bucket is like a "memory bank" for Terraform to remember what it built.**

## 🚨 Issues Resolved
- **Account Mismatch**: Bucket was created in wrong AWS account (471112835616 vs 296950653587)
- **State File Corruption**: Local state file had invalid JSON format
- **Backend Configuration Conflicts**: Multiple backend config changes causing initialization issues
- **Permission Issues**: 403 errors due to account ownership problems

---
*Last Updated: Step 5 - Terraform initialization successful with local state*
