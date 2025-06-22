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
  - jq ❌ (needs installation)
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

### Step 5 - Terraform initialization (RESOLVED)
- ✅ **Account Mismatch Issue**: Identified and resolved account mismatch (bucket created in 471112835616, IAM user in 296950653587)
- ✅ **Bucket Recreation**: Deleted old bucket and recreated in correct account (296950653587)
- ✅ **State File Issues**: Resolved corrupted state file and backend configuration conflicts
- ✅ **Local Initialization**: Successfully initialized Terraform with local state and AWS provider v5.100.0
- ✅ **Provider Installation**: AWS provider installed and lock file created
- 🔄 **Next**: Create S3 bucket & CloudFront distribution with Terraform

## 🔄 Current Status
- **Current Step**: Step 5 (Create S3 bucket & CloudFront with Terraform)
- **Working Directory**: `C:\Users\Ryan\Desktop\Work\BriteSystems\DevOps\static-site-deployer\infra`
- **Virtual Environment**: Needs recreation (`.venv` was deleted to avoid Git issues)
- **AWS Profile**: `ryan_dev_home` configured and tested
- **Terraform**: v1.12.2 installed, needs reinitialization
- **Backend**: Temporarily using local state (backend.tf renamed to backend.tf.temp)
- **Gitignore**: ✅ Properly configured to prevent future virtual environment commits

## 📋 Next Steps
1. Recreate Python virtual environment: `python -m venv .venv`
2. Activate virtual environment: `.venv\Scripts\Activate.ps1`
3. Reinitialize Terraform: `terraform init`
4. Create S3 bucket and CloudFront distribution with `terraform plan` and `terraform apply`
5. Restore remote backend configuration once infrastructure is created
6. Install jq (last missing tool)
7. Begin Python CLI development

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
