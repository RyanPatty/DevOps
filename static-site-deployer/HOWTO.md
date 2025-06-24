# Static-Site Deployer - Complete Build & Operations Guide

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Step-by-Step Build Process](#step-by-step-build-process)
- [Infrastructure Setup](#infrastructure-setup)
- [CLI Development](#cli-development)
- [Testing & Validation](#testing--validation)
- [GitHub Actions Setup](#github-actions-setup)
- [Operational Commands](#operational-commands)
- [Troubleshooting](#troubleshooting)

---

## 🛠️ Prerequisites

### Required Software
```powershell
# Check what's installed
python --version          # Need 3.11+
aws --version            # Need 2.x
terraform --version      # Need 1.5+
node --version           # Need 20+
git --version            # Any recent version
```

### Install Missing Tools (Windows)
```powershell
# Install Chocolatey (run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install python terraform awscli jq git nodejs -y
```

---

## 🏗️ Step-by-Step Build Process

### Step 0: Environment Setup
```powershell
# Create project directory
mkdir static-site-deployer
cd static-site-deployer

# Initialize git
git init -b main

# Create Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Verify Python version
python -V  # Should show 3.11+
```

### Step 1: Project Structure
```powershell
# Create directory structure
mkdir cli, infra, .github\workflows, site-sample

# Create Python package files
New-Item cli\__init__.py -ItemType File
New-Item README.md -ItemType File
New-Item REQUIREMENTS.md -ItemType File

# Create sample site
"<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Static Site</title>
</head>
<body>
    <h1>Hello world - UPDATED!</h1>
</body>
</html>" | Out-File -FilePath site-sample\index.html -Encoding UTF8

# Create .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Terraform
.terraform/
*.tfstate
*.tfstate.*
.terraform.lock.hcl

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"@ | Out-File -FilePath .gitignore -Encoding UTF8

# Initial commit
git add .
git commit -m "chore: scaffold repo"
```

### Step 2: AWS Account Setup
```powershell
# Configure AWS CLI with your profile
aws configure --profile your-aws-profile

# Test AWS access
aws sts get-caller-identity --profile your-aws-profile

# Create S3 bucket for Terraform state (one-time per account)
aws s3 mb s3://your-tf-state-bucket --profile your-aws-profile

# Create DynamoDB table for Terraform state locking
aws dynamodb create-table `
  --table-name tf-state-lock `
  --attribute-definitions AttributeName=LockID,AttributeType=S `
  --key-schema AttributeName=LockID,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --profile your-aws-profile
```

### Step 3: Terraform Backend Configuration
```powershell
# Create backend.tf
@"
terraform {
  backend "s3" {
    bucket         = "your-tf-state-bucket"
    key            = "static-site-deployer/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-state-lock"
    encrypt        = true
  }
}
"@ | Out-File -FilePath infra\backend.tf -Encoding UTF8

# Commit backend config
git add infra/backend.tf
git commit -m "infra: add remote backend"
```

### Step 4: Infrastructure Deployment
```powershell
# Navigate to infra directory
cd infra

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"

# Apply infrastructure
terraform apply -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"

# Save outputs for later use
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
$env:CF_URL="https://your-cloudfront-url.cloudfront.net"
```

### Step 5: Python Package Setup
```powershell
# Go back to project root
cd ..

# Create pyproject.toml
@"
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "static-site-deployer"
version = "0.1.0"
description = "Deploy static sites to S3 + CloudFront with zero long-lived keys"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.34.0",
    "click>=8.1.0",
    "tqdm>=4.66.0",
    "colorama>=0.4.6",
]

[project.scripts]
deploy_site = "cli.main:cli"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["cli*"]
"@ | Out-File -FilePath pyproject.toml -Encoding UTF8

# Install package in development mode
pip install -e .
```

### Step 6: CLI Development
```powershell
# Create CLI modules (see individual files for content)
# cli/hashutil.py - File hash utilities
# cli/uploader.py - S3 upload logic
# cli/invalidate.py - CloudFront invalidation
# cli/main.py - Main CLI entry point

# Test CLI installation
deploy_site --help
```

### Step 7: Initial Deployment Test
```powershell
# Deploy sample site
deploy_site site-sample --profile your-aws-profile

# Test with environment variables
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
deploy_site site-sample --profile your-aws-profile

# Test dry run
deploy_site site-sample --dry-run --profile your-aws-profile
```

### Step 8: Content-Type Fix
```powershell
# Fix content-type issue (if site downloads instead of displays)
aws s3 cp site-sample/index.html s3://your-site-bucket/index.html --content-type "text/html" --profile your-aws-profile

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/*" --profile your-aws-profile
```

### Step 9: Lighthouse Testing
```powershell
# Install Lighthouse CI
npm install -g @lhci/cli

# Run Lighthouse test
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net"

# Upload results
npx @lhci/cli upload --target=temporary-public-storage
```

---

## 🔧 Infrastructure Setup

### Terraform Files Created:
- `infra/main.tf` - S3 bucket and CloudFront distribution
- `infra/oidc.tf` - GitHub Actions OIDC role
- `infra/backend.tf` - Remote state configuration

### Key Resources Created:
- **S3 Bucket**: `your-site-bucket`
- **CloudFront Distribution**: `your-cloudfront-distribution-id`
- **CloudFront URL**: `https://your-cloudfront-url.cloudfront.net`
- **IAM OIDC Role**: `arn:aws:iam::YOUR-ACCOUNT:role/github-actions-static-site-deployer`

---

## 🧪 Testing & Validation

### Test Site Deployment
```powershell
# Deploy test site
deploy_site site-sample --profile your-aws-profile

# Verify site is accessible
Invoke-WebRequest -Uri "https://your-cloudfront-url.cloudfront.net" -UseBasicParsing
```

### Test CLI Features
```powershell
# Test help
deploy_site --help

# Test dry run
deploy_site site-sample --dry-run --profile your-aws-profile

# Test with wait for invalidation
deploy_site site-sample --wait --profile your-aws-profile
```

### Performance Testing
```powershell
# Run Lighthouse
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net" --numberOfRuns=1
```

---

## 🔐 GitHub Actions Setup

### Step 1: Add Repository Secrets
Go to: `https://github.com/yourusername/yourrepo/settings/secrets/actions`

Add these secrets:
- `CF_DIST_ID` = `your-cloudfront-distribution-id`
- `DEPLOY_BUCKET` = `your-site-bucket`
- `CF_URL` = `https://your-cloudfront-url.cloudfront.net`
- `AWS_ROLE_TO_ASSUME` = `arn:aws:iam::YOUR-ACCOUNT:role/github-actions-static-site-deployer`

### Step 2: Create Workflow File
Create `.github/workflows/deploy.yml` (see workflow file content)

---

## 🚀 Operational Commands

### Daily Deployment Commands
```powershell
# Deploy a site
deploy_site dist/ --profile production

# Deploy with environment variables
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
deploy_site dist/ --profile production

# Deploy and wait for invalidation
deploy_site dist/ --wait --profile production

# Preview changes (dry run)
deploy_site dist/ --dry-run --profile production
```

### Infrastructure Management
```powershell
# Check infrastructure status
cd infra
terraform plan

# Update infrastructure
terraform apply -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"

# Destroy infrastructure (if needed)
terraform destroy -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"
```

### AWS Resource Management
```powershell
# Check S3 bucket contents
aws s3 ls s3://your-site-bucket --profile your-aws-profile

# Check CloudFront distribution
aws cloudfront get-distribution --id your-cloudfront-distribution-id --profile your-aws-profile

# List CloudFront invalidations
aws cloudfront list-invalidations --distribution-id your-cloudfront-distribution-id --profile your-aws-profile

# Create manual invalidation
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/*" --profile your-aws-profile
```

### Content Management
```powershell
# Upload single file with correct content type
aws s3 cp file.html s3://your-site-bucket/ --content-type "text/html" --profile your-aws-profile

# Upload directory
aws s3 sync dist/ s3://your-site-bucket/ --profile your-aws-profile

# Delete file
aws s3 rm s3://your-site-bucket/file.html --profile your-aws-profile

# Empty bucket (careful!)
aws s3 rm s3://your-site-bucket/ --recursive --profile your-aws-profile
```

### Monitoring & Debugging
```powershell
# Check CloudFront logs
aws cloudfront get-distribution-config --id your-cloudfront-distribution-id --profile your-aws-profile

# Test site accessibility
Invoke-WebRequest -Uri "https://your-cloudfront-url.cloudfront.net" -UseBasicParsing

# Check S3 object metadata
aws s3api head-object --bucket your-site-bucket --key index.html --profile your-aws-profile

# Run Lighthouse test
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net" --numberOfRuns=1
```

### Environment Variables Reference
```powershell
# Set for current session
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
$env:CF_URL="https://your-cloudfront-url.cloudfront.net"

# Set permanently (Windows)
[Environment]::SetEnvironmentVariable("DEPLOY_BUCKET", "your-site-bucket", "User")
[Environment]::SetEnvironmentVariable("CF_DIST_ID", "your-cloudfront-distribution-id", "User")
[Environment]::SetEnvironmentVariable("CF_URL", "https://your-cloudfront-url.cloudfront.net", "User")
```

---

## 🔧 Troubleshooting

### Common Issues

#### Site Downloads Instead of Displays
```powershell
# Fix content type
aws s3 cp index.html s3://your-site-bucket/index.html --content-type "text/html" --profile your-aws-profile

# Invalidate cache
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/*" --profile your-aws-profile
```

#### CloudFront Not Updating
```powershell
# Check invalidation status
aws cloudfront get-invalidation --distribution-id your-cloudfront-distribution-id --id INVALIDATION_ID --profile your-aws-profile

# Wait for invalidation (can take 5-15 minutes)
```

#### AWS Credentials Issues
```powershell
# Check current profile
aws sts get-caller-identity --profile your-aws-profile

# Reconfigure if needed
aws configure --profile your-aws-profile
```

#### Terraform State Issues
```powershell
# Reinitialize if needed
cd infra
terraform init -reconfigure
```

### Performance Issues
```powershell
# Check CloudFront distribution status
aws cloudfront get-distribution --id your-cloudfront-distribution-id --profile your-aws-profile

# Run Lighthouse to identify issues
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net"
```

---

## 📊 Resource Inventory

### AWS Resources
- **Account**: YOUR-AWS-ACCOUNT-ID
- **Region**: us-east-1
- **S3 Bucket**: your-site-bucket
- **CloudFront Distribution**: your-cloudfront-distribution-id
- **CloudFront URL**: https://your-cloudfront-url.cloudfront.net
- **IAM Role**: github-actions-static-site-deployer
- **Terraform State Bucket**: your-tf-state-bucket
- **DynamoDB Lock Table**: tf-state-lock

### GitHub Repository
- **Repo**: https://github.com/yourusername/yourrepo
- **Branch**: main
- **Secrets**: CF_DIST_ID, DEPLOY_BUCKET, CF_URL, AWS_ROLE_TO_ASSUME

### Local Environment
- **Project Path**: /path/to/your/static-site-deployer
- **Python Version**: 3.12.1
- **Virtual Environment**: .venv
- **AWS Profile**: your-aws-profile

---

## 🎯 Quick Reference

### One-Liner Deployment
```powershell
deploy_site dist/ --bucket your-site-bucket --dist-id your-cloudfront-distribution-id --profile your-aws-profile
```

### Environment Setup
```powershell
cd static-site-deployer
.venv\Scripts\Activate.ps1
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
```

### Infrastructure Update
```powershell
cd infra
terraform apply -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"
```

---

*Last Updated: June 24, 2025* 