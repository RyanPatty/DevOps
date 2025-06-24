# Static-Site Deployer - Command Inventory

## 🔍 Discovery Commands

### Find Your Values
```powershell
# Get your GitHub username
git config user.name
git config user.email

# Get your AWS account ID
aws sts get-caller-identity --profile your-aws-profile --query 'Account' --output text

# Get your AWS user/role name
aws sts get-caller-identity --profile your-aws-profile --query 'Arn' --output text

# List your AWS profiles
aws configure list-profiles

# Get your current AWS region
aws configure get region --profile your-aws-profile

# Get your current working directory
pwd

# Get your Python version
python --version

# Get your Node.js version
node --version

# Get your Terraform version
terraform --version
```

### Find AWS Resource IDs
```powershell
# List your S3 buckets
aws s3 ls --profile your-aws-profile

# List your CloudFront distributions
aws cloudfront list-distributions --profile your-aws-profile --query 'DistributionList.Items[*].[Id,DomainName,Origins.Items[0].DomainName]' --output table

# Get specific CloudFront distribution details
aws cloudfront get-distribution --id YOUR-DISTRIBUTION-ID --profile your-aws-profile --query 'Distribution.{Id:Id,DomainName:DomainName,Status:Status}' --output table

# List your IAM roles
aws iam list-roles --profile your-aws-profile --query 'Roles[*].[RoleName,Arn]' --output table

# List your OIDC providers
aws iam list-open-id-connect-providers --profile your-aws-profile --query 'OpenIDConnectProviderList[*]' --output table
```

### Find GitHub Information
```powershell
# Get your GitHub username (if you have GitHub CLI)
gh auth status

# Get your current git remote URL
git remote get-url origin

# Extract username from git remote
git remote get-url origin | ForEach-Object { ($_ -split '/')[-2] }

# Get your current git branch
git branch --show-current
```

### Find Terraform Outputs
```powershell
# Get all Terraform outputs
cd infra
terraform output

# Get specific outputs
terraform output bucket_name
terraform output cloudfront_distribution_id
terraform output cloudfront_url
terraform output github_actions_role_arn
```

---

## 🚀 Quick Start Commands

### Environment Setup
```powershell
# Activate virtual environment
cd static-site-deployer
.venv\Scripts\Activate.ps1

# Set environment variables
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
$env:CF_URL="https://your-cloudfront-url.cloudfront.net"
```

### One-Liner Deployment
```powershell
# Deploy with all parameters
deploy_site dist/ --bucket your-site-bucket --dist-id your-cloudfront-distribution-id --profile your-aws-profile

# Deploy with environment variables
deploy_site dist/ --profile your-aws-profile

# Dry run (preview changes)
deploy_site dist/ --dry-run --profile your-aws-profile

# Deploy and wait for invalidation
deploy_site dist/ --wait --profile your-aws-profile
```

---

## 🏗️ Build Commands

### Infrastructure
```powershell
# Initialize Terraform
cd infra
terraform init

# Plan changes
terraform plan -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"

# Apply changes
terraform apply -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"

# Destroy (if needed)
terraform destroy -var="bucket_name=your-site-bucket" -var="github_repo=yourusername/yourrepo"
```

### Python Package
```powershell
# Install in development mode
pip install -e .

# Test CLI
deploy_site --help
```

---

## 🔧 Operational Commands

### AWS S3 Management
```powershell
# List bucket contents
aws s3 ls s3://your-site-bucket --profile your-aws-profile

# Upload single file with content type
aws s3 cp index.html s3://your-site-bucket/ --content-type "text/html" --profile your-aws-profile

# Upload directory
aws s3 sync dist/ s3://your-site-bucket/ --profile your-aws-profile

# Delete file
aws s3 rm s3://your-site-bucket/file.html --profile your-aws-profile

# Check object metadata
aws s3api head-object --bucket your-site-bucket --key index.html --profile your-aws-profile
```

### CloudFront Management
```powershell
# Check distribution status
aws cloudfront get-distribution --id your-cloudfront-distribution-id --profile your-aws-profile

# List invalidations
aws cloudfront list-invalidations --distribution-id your-cloudfront-distribution-id --profile your-aws-profile

# Create invalidation
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/*" --profile your-aws-profile

# Check invalidation status
aws cloudfront get-invalidation --distribution-id your-cloudfront-distribution-id --id INVALIDATION_ID --profile your-aws-profile
```

### AWS Identity & Access
```powershell
# Check current identity
aws sts get-caller-identity --profile your-aws-profile

# List IAM roles
aws iam list-roles --profile your-aws-profile

# Check OIDC provider
aws iam list-open-id-connect-providers --profile your-aws-profile
```

---

## 🧪 Testing Commands

### Site Testing
```powershell
# Test site accessibility
Invoke-WebRequest -Uri "https://your-cloudfront-url.cloudfront.net" -UseBasicParsing

# Test with curl (if available)
curl -I https://your-cloudfront-url.cloudfront.net
```

### Performance Testing
```powershell
# Install Lighthouse
npm install -g @lhci/cli

# Run Lighthouse (single run)
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net" --numberOfRuns=1

# Run Lighthouse (3 runs)
npx @lhci/cli collect --url="https://your-cloudfront-url.cloudfront.net"

# Upload results
npx @lhci/cli upload --target=temporary-public-storage
```

### CLI Testing
```powershell
# Test help
deploy_site --help

# Test dry run
deploy_site site-sample --dry-run --profile your-aws-profile

# Test with different profiles
deploy_site site-sample --profile staging
deploy_site site-sample --profile production
```

---

## 🔍 Troubleshooting Commands

### Content-Type Issues
```powershell
# Fix content-type for HTML files
aws s3 cp index.html s3://your-site-bucket/index.html --content-type "text/html" --profile your-aws-profile

# Fix content-type for CSS files
aws s3 cp style.css s3://your-site-bucket/style.css --content-type "text/css" --profile your-aws-profile

# Fix content-type for JS files
aws s3 cp script.js s3://your-site-bucket/script.js --content-type "application/javascript" --profile your-aws-profile
```

### Cache Issues
```powershell
# Force complete cache invalidation
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/*" --profile your-aws-profile

# Invalidate specific files
aws cloudfront create-invalidation --distribution-id your-cloudfront-distribution-id --paths "/index.html" --profile your-aws-profile
```

### Terraform Issues
```powershell
# Reinitialize Terraform
cd infra
terraform init -reconfigure

# Check Terraform state
terraform show

# Import existing resources (if needed)
terraform import aws_s3_bucket.static_site your-site-bucket
```

---

## 📊 Monitoring Commands

### Resource Status
```powershell
# Check S3 bucket
aws s3 ls s3://your-site-bucket --profile your-aws-profile

# Check CloudFront
aws cloudfront get-distribution --id your-cloudfront-distribution-id --profile your-aws-profile

# Check IAM role
aws iam get-role --role-name github-actions-static-site-deployer --profile your-aws-profile
```

### Cost Monitoring
```powershell
# Check S3 costs
aws ce get-cost-and-usage --time-period Start=2025-06-01,End=2025-06-30 --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --profile your-aws-profile

# Check CloudFront costs
aws ce get-cost-and-usage --time-period Start=2025-06-01,End=2025-06-30 --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon CloudFront"]}}' --profile your-aws-profile
```

---

## 🎯 Environment Variables

### Set for Current Session
```powershell
$env:DEPLOY_BUCKET="your-site-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
$env:CF_URL="https://your-cloudfront-url.cloudfront.net"
$env:AWS_PROFILE="your-aws-profile"
```

### Set Permanently (Windows)
```powershell
[Environment]::SetEnvironmentVariable("DEPLOY_BUCKET", "your-site-bucket", "User")
[Environment]::SetEnvironmentVariable("CF_DIST_ID", "your-cloudfront-distribution-id", "User")
[Environment]::SetEnvironmentVariable("CF_URL", "https://your-cloudfront-url.cloudfront.net", "User")
[Environment]::SetEnvironmentVariable("AWS_PROFILE", "your-aws-profile", "User")
```

---

## 🔐 GitHub Actions Commands

### Local Testing of Workflow
```powershell
# Test OIDC token (if you have GitHub CLI)
gh auth token

# Test AWS role assumption
aws sts assume-role-with-web-identity --role-arn arn:aws:iam::YOUR-ACCOUNT:role/github-actions-static-site-deployer --role-session-name test-session --web-identity-token-file token.txt --profile your-aws-profile
```

---

## 📋 Resource Inventory

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

*Last Updated: June 24, 2025* 