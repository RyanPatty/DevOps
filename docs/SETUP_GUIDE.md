# Setup Guide - Static-Site Deployer CLI

Complete step-by-step guide for setting up the Static-Site Deployer CLI from scratch.

## 📋 **Prerequisites**

### **Required Tools**

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.11+ | `choco install python` (Windows) |
| **Terraform** | 1.5+ | `choco install terraform` |
| **AWS CLI** | v2 | `choco install awscli` |
| **Node.js** | 20+ | `choco install nodejs` |
| **Git** | Latest | `choco install git` |
| **jq** | Latest | `choco install jq` |

### **AWS Account Setup**
- Active AWS account with billing enabled
- IAM user with administrative permissions (for initial setup)
- AWS SSO configured (recommended for production)

---

## 🚀 **Step 1: Project Setup**

### **1.1 Clone Repository**
```bash
git clone https://github.com/yourusername/static-site-deployer
cd static-site-deployer
```

### **1.2 Create Python Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Verify Python version
python --version  # Should show 3.11+
```

### **1.3 Install CLI Tool**
```bash
# Install in development mode
pip install -e .

# Verify installation
deploy_site --help
```

### **1.4 Install Development Tools (Optional)**
```bash
# Install linting and formatting tools
pip install ruff black pre-commit

# Install testing framework
pip install pytest

# Set up pre-commit hooks
pre-commit install
```

---

## ☁️ **Step 2: AWS Infrastructure Setup**

### **2.1 Configure AWS CLI**

```bash
# Configure AWS CLI with your credentials
aws configure --profile your-profile-name

# Test your configuration
aws sts get-caller-identity --profile your-profile-name
```

**Expected Output:**
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### **2.2 Create Terraform Backend (One-time per AWS account)**

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://your-tf-state-bucket --profile your-profile-name

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name tf-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --profile your-profile-name
```

### **2.3 Configure Terraform Backend**

Edit `infra/backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket = "your-tf-state-bucket"
    key    = "static-site-deployer/terraform.tfstate"
    region = "us-east-1"
    
    dynamodb_table = "tf-state-lock"
    encrypt        = true
  }
}
```

### **2.4 Deploy Infrastructure**

```bash
# Navigate to infrastructure directory
cd infra

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var="bucket_name=your-static-site-bucket" \
               -var="github_repo=yourusername/static-site-deployer"

# Apply the infrastructure
terraform apply -var="bucket_name=your-static-site-bucket" \
                -var="github_repo=yourusername/static-site-deployer"
```

### **2.5 Save Infrastructure Outputs**

```bash
# Get all outputs
terraform output

# Save to environment variables (PowerShell)
$env:DEPLOY_BUCKET="your-static-site-bucket"
$env:CF_DIST_ID="E123ABCXYZ"  # From terraform output
$env:CF_URL="https://xxxxx.cloudfront.net"  # From terraform output
$env:AWS_ROLE_TO_ASSUME="arn:aws:iam::123456789012:role/github-actions-static-site-deployer"

# Verify the outputs
echo "Bucket: $env:DEPLOY_BUCKET"
echo "Distribution ID: $env:CF_DIST_ID"
echo "CloudFront URL: $env:CF_URL"
echo "Role ARN: $env:AWS_ROLE_TO_ASSUME"
```

---

## 🔐 **Step 3: GitHub Configuration**

### **3.1 Add Repository Secrets**

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add each secret with the exact name and value:

| Secret Name | Value Source |
|-------------|--------------|
| `AWS_ROLE_TO_ASSUME` | `terraform output github_actions_role_arn` |
| `DEPLOY_BUCKET` | `terraform output bucket_name` |
| `CF_DIST_ID` | `terraform output cloudfront_distribution_id` |
| `CF_URL` | `terraform output cloudfront_url` |

### **3.2 Verify Secret Setup**

```bash
# Test locally with environment variables
deploy_site site-sample/ --bucket $env:DEPLOY_BUCKET --dist-id $env:CF_DIST_ID
```

---

## 🧪 **Step 4: Testing & Validation**

### **4.1 Test Local Deployment**

```bash
# Test with dry run
deploy_site site-sample/ --bucket $env:DEPLOY_BUCKET --dist-id $env:CF_DIST_ID --dry-run

# Test actual deployment
deploy_site site-sample/ --bucket $env:DEPLOY_BUCKET --dist-id $env:CF_DIST_ID --wait
```

### **4.2 Verify Site Accessibility**

```bash
# Check if site is accessible
curl -I $env:CF_URL

# Expected response:
# HTTP/2 200
# content-type: text/html
# ...
```

### **4.3 Test Lighthouse Locally**

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run Lighthouse test
npx lhci collect --url=$env:CF_URL

# Upload results (optional)
npx lhci upload --target=temporary-public-storage
```

**Expected Scores:**
- Performance: ≥90
- Accessibility: ≥90
- Best Practices: ≥90
- SEO: ≥90

---

## 🔄 **Step 5: CI/CD Pipeline Testing**

### **5.1 Trigger GitHub Actions**

```bash
# Make a small change to trigger the workflow
echo "<!-- Updated: $(Get-Date) -->" >> site-sample/index.html

# Commit and push
git add .
git commit -m "test: Trigger CI/CD pipeline"
git push origin main
```

### **5.2 Monitor Workflow**

1. Go to **Actions** tab in GitHub repository
2. Click on the running workflow
3. Monitor each step for success/failure

### **5.3 Verify Results**

- ✅ **Deployment**: Site should be updated
- ✅ **Lighthouse**: Scores should be ≥90
- ✅ **PR Comments**: Results posted to PR (if applicable)

---

## 🔧 **Step 6: Troubleshooting**

### **Common Issues & Solutions**

#### **6.1 Terraform Backend Issues**

```bash
# If backend bucket doesn't exist
aws s3 mb s3://your-tf-state-bucket --profile your-profile-name

# If DynamoDB table doesn't exist
aws dynamodb create-table \
  --table-name tf-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --profile your-profile-name
```

#### **6.2 AWS Authentication Issues**

```bash
# Check current credentials
aws sts get-caller-identity --profile your-profile-name

# Reconfigure if needed
aws configure --profile your-profile-name
```

#### **6.3 CloudFront Not Updating**

```bash
# Check invalidation status
aws cloudfront get-invalidation \
  --distribution-id $env:CF_DIST_ID \
  --id I123ABCXYZ

# Wait for invalidation (can take 5-15 minutes)
```

#### **6.4 GitHub Actions Failures**

```bash
# Check workflow logs for specific errors
# Common issues:
# - Missing secrets
# - Incorrect secret values
# - OIDC role permissions
```

### **Debug Commands**

```bash
# Test CLI functionality
deploy_site --help
deploy_site site-sample/ --dry-run

# Check AWS resources
aws s3 ls s3://$env:DEPLOY_BUCKET
aws cloudfront get-distribution --id $env:CF_DIST_ID

# Verify Terraform state
terraform show
terraform output
```

---

## 📊 **Step 7: Performance Validation**

### **7.1 Deployment Performance**

```bash
# Time a deployment
Measure-Command { deploy_site site-sample/ --bucket $env:DEPLOY_BUCKET --dist-id $env:CF_DIST_ID }

# Expected: <30 seconds for small sites
```

### **7.2 Cost Monitoring**

```bash
# Check AWS costs (monthly)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Expected: <$1/month for typical usage
```

---

## ✅ **Setup Complete!**

Your Static-Site Deployer CLI is now fully configured and ready for production use.

### **What You Can Do Now:**

1. **Deploy Static Sites**: `deploy_site dist/ --bucket your-bucket --dist-id your-dist-id`
2. **CI/CD Integration**: Automatic deployment on git push
3. **Quality Assurance**: Automatic Lighthouse testing
4. **Multi-Environment**: Support for staging/production
5. **Rollback Capability**: S3 versioning for easy recovery

### **Next Steps:**

- [Read the CLI Reference](../README.md#cli-reference)
- [Check the Technical Reference](REFERENCE.md)
- [Configure custom domains](CUSTOM_DOMAINS.md)
- [Set up monitoring and alerts](MONITORING.md)

---

## 🆘 **Need Help?**

- **Documentation**: [Main README](../README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/static-site-deployer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/static-site-deployer/discussions) 