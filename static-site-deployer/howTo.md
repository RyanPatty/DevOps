# How To: Static-Site Deployer CLI

A complete guide to building, installing, and using the static site deployer CLI tool.

---

## 🏗️ Building from Source

### Prerequisites

Before you start, ensure you have these tools installed:

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.11+ | `choco install python` or download from python.org |
| **Git** | Latest | `choco install git` |
| **Node.js** | 20+ | `choco install nodejs` (for Lighthouse testing) |

### Step 1: Clone the Repository

```powershell
git clone https://github.com/ryanpatty/static-site-deployer
cd static-site-deployer
```

### Step 2: Set Up Python Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Verify Python version
python --version  # Should show 3.11+
```

### Step 3: Install Dependencies

```powershell
# Install the CLI package in development mode
pip install -e .

# Verify installation
deploy_site --help
```

### Step 4: Install Development Tools (Optional)

```powershell
# Install linting and formatting tools
pip install ruff black pre-commit

# Install testing framework
pip install pytest

# Set up pre-commit hooks
pre-commit install
```

---

## 🚀 Setting Up AWS Infrastructure

### Prerequisites

| Tool | Installation |
|------|--------------|
| **AWS CLI v2** | `choco install awscli` |
| **Terraform** | `choco install terraform` |
| **jq** | `choco install jq` |

### Step 1: Configure AWS CLI

```powershell
# Configure AWS CLI with your credentials
aws configure --profile your-profile-name

# Test your configuration
aws sts get-caller-identity --profile your-profile-name
```

### Step 2: Create Terraform Backend (One-time per AWS account)

```powershell
# Create S3 bucket for Terraform state
aws s3 mb s3://your-tf-state-bucket --profile your-profile-name

# Create DynamoDB table for state locking
aws dynamodb create-table `
  --table-name tf-state-lock `
  --attribute-definitions AttributeName=LockID,AttributeType=S `
  --key-schema AttributeName=LockID,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --profile your-profile-name
```

### Step 3: Deploy Infrastructure

```powershell
# Navigate to infrastructure directory
cd infra

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var="bucket_name=your-static-site-bucket" `
               -var="github_repo=yourusername/static-site-deployer"

# Apply the infrastructure
terraform apply -var="bucket_name=your-static-site-bucket" `
                -var="github_repo=yourusername/static-site-deployer"
```

### Step 4: Save Outputs

After successful deployment, save the outputs:

```powershell
# Set environment variables
$env:DEPLOY_BUCKET="your-static-site-bucket"
$env:CF_DIST_ID="E123ABCXYZ"  # From terraform output
$env:CF_URL="https://xxxxx.cloudfront.net"  # From terraform output

# Verify the outputs
echo "Bucket: $env:DEPLOY_BUCKET"
echo "Distribution ID: $env:CF_DIST_ID"
echo "CloudFront URL: $env:CF_URL"
```

---

## 📦 Adding to PATH

### Option 1: Virtual Environment (Recommended)

The CLI is installed in your virtual environment. To use it:

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Use the CLI
deploy_site --help
```

### Option 2: Global Installation

If you want to install globally (not recommended):

```powershell
# Install globally
pip install -e . --user

# Add Python Scripts to PATH (if not already there)
$env:PATH += ";$env:APPDATA\Python\Python312\Scripts"
```

### Option 3: PowerShell Profile

Add to your PowerShell profile for persistent access:

```powershell
# Edit your PowerShell profile
notepad $PROFILE

# Add this line to the profile
function deploy_site { & "C:\path\to\your\project\.venv\Scripts\deploy_site.exe" $args }
```

---

## 🎯 Using the CLI

### Basic Usage

```powershell
# Deploy a directory
deploy_site /path/to/your/site --profile your-aws-profile

# Use environment variables
deploy_site /path/to/your/site --profile your-aws-profile
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--bucket` | S3 bucket name | `--bucket my-static-site` |
| `--dist-id` | CloudFront distribution ID | `--dist-id E123ABCXYZ` |
| `--profile` | AWS profile to use | `--profile my-aws-profile` |
| `--dry-run` | Show what would be uploaded | `--dry-run` |
| `--wait` | Wait for invalidation to complete | `--wait` |

### Environment Variables

You can set these environment variables to avoid typing them every time:

```powershell
$env:DEPLOY_BUCKET="your-static-site-bucket"
$env:CF_DIST_ID="E123ABCXYZ"
$env:CF_URL="https://xxxxx.cloudfront.net"
```

### Examples

#### Test with Dry Run

```powershell
# Test what would be uploaded
deploy_site site-sample --dry-run --profile your-aws-profile
```

#### Deploy for Real

```powershell
# Deploy the sample site
deploy_site site-sample --profile your-aws-profile

# Deploy a built React app
deploy_site dist --profile your-aws-profile

# Deploy and wait for invalidation
deploy_site dist --profile your-aws-profile --wait
```

#### Deploy with Custom Bucket

```powershell
# Override bucket and distribution
deploy_site dist --bucket my-custom-bucket --dist-id E999ZZZ999 --profile your-aws-profile
```

---

## 🧪 Testing

### Test the CLI

```powershell
# Test help
deploy_site --help

# Test with sample site
deploy_site site-sample --dry-run --profile your-aws-profile

# Test actual deployment
deploy_site site-sample --profile your-aws-profile
```

### Test Infrastructure

```powershell
# Test S3 access
aws s3 ls s3://your-bucket --profile your-aws-profile

# Test CloudFront
Start-Process "https://your-cloudfront-url.cloudfront.net"

# Test Lighthouse (if Node.js is installed)
npx lhci collect --url=https://your-cloudfront-url.cloudfront.net
```

### Test Error Handling

```powershell
# Test with invalid bucket
deploy_site site-sample --bucket invalid-bucket --profile your-aws-profile

# Test with invalid profile
deploy_site site-sample --profile invalid-profile

# Test with non-existent directory
deploy_site /path/does/not/exist --profile your-aws-profile
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "deploy_site is not recognized"

**Solution:**
```powershell
# Make sure virtual environment is activated
.venv\Scripts\Activate.ps1

# Reinstall the package
pip install -e .
```

#### 2. "403 Forbidden" error

**Solution:**
```powershell
# Make sure you're using the correct AWS profile
deploy_site site-sample --profile your-aws-profile

# Verify your AWS credentials
aws sts get-caller-identity --profile your-aws-profile
```

#### 3. "No module named 'cli.main'"

**Solution:**
```powershell
# Reinstall the package
pip install -e .

# Check that all CLI files exist
ls cli/
```

#### 4. CloudFront "Access Denied" Error

**Problem:** You can deploy files to S3 successfully, but when you visit the CloudFront URL, you get an "Access Denied" error.

**Root Cause:** This happens when CloudFront is configured with Origin Access Control (OAC) but the S3 bucket doesn't have a policy allowing CloudFront to access it.

**Diagnosis:**
```powershell
# Check if CloudFront is deployed
aws cloudfront get-distribution --id YOUR-DIST-ID --profile your-profile

# Check if S3 bucket has content
aws s3 ls s3://your-bucket --profile your-profile --recursive

# Check if bucket policy exists
aws s3api get-bucket-policy --bucket your-bucket --profile your-profile
```

**Solution:** Add S3 bucket policy to allow CloudFront access:

1. **Update Terraform configuration** (`infra/main.tf`):
```hcl
# S3 bucket policy to allow CloudFront access via Origin Access Control
resource "aws_s3_bucket_policy" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontServicePrincipal"
        Effect    = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.static_site.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.static_site.arn
          }
        }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.static_site]
}
```

2. **Apply the changes:**
```powershell
cd infra
terraform plan -var="bucket_name=your-bucket" -var="github_repo=yourusername/repo"
terraform apply -var="bucket_name=your-bucket" -var="github_repo=yourusername/repo"
```

3. **Test the site:**
```powershell
Start-Process "https://your-cloudfront-url.cloudfront.net"
```

**Why This Happens:** When you create a CloudFront distribution with Origin Access Control, the S3 bucket must have a policy that explicitly allows CloudFront to access it. The bucket policy uses the CloudFront distribution ARN to ensure only your specific distribution can access the bucket.

#### 5. Terraform errors

**Solution:**
```powershell
# Check Terraform state
terraform show

# Reinitialize if needed
terraform init

# Check AWS credentials
aws sts get-caller-identity --profile your-aws-profile
```

### Debug Mode

For more verbose output, you can modify the CLI code to add debug logging:

```python
# In cli/main.py, add debug prints
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Development

### Project Structure

```
static-site-deployer/
├── cli/                    # Python CLI package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # CLI entry point
│   ├── hashutil.py        # File hash utilities
│   ├── uploader.py        # S3 upload logic
│   └── invalidate.py      # CloudFront invalidation
├── infra/                 # Terraform infrastructure
│   ├── main.tf            # Main infrastructure
│   ├── backend.tf         # Remote state config
│   └── variables.tf       # Variable definitions
├── site-sample/           # Sample static site
├── pyproject.toml         # Python package config
├── README.md              # Project documentation
├── REQUIREMENTS.md        # Detailed requirements
└── howTo.md              # This file
```

### Adding Features

1. **Add new CLI options:**
   - Edit `cli/main.py` to add new Click options
   - Update the CLI function signature
   - Add validation logic

2. **Add new AWS functionality:**
   - Create new modules in `cli/`
   - Import and use in `main.py`
   - Add proper error handling

3. **Update infrastructure:**
   - Edit `infra/main.tf`
   - Run `terraform plan` to preview changes
   - Run `terraform apply` to deploy

### Code Quality

```powershell
# Format code
black cli/

# Lint code
ruff check cli/

# Run tests (when implemented)
pytest tests/
```

---

## 🚀 Next Steps

### Immediate Tasks

1. **Complete Step 6**: Create GitHub OIDC role
2. **Complete Step 12**: Lighthouse testing
3. **Complete Step 13**: GitHub Secrets setup
4. **Complete Step 14**: GitHub Actions workflow

### Future Enhancements

1. **Add rollback functionality**
2. **Add Slack notifications**
3. **Add multi-environment support**
4. **Add performance monitoring**
5. **Add cost optimization features**

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Verify your AWS credentials and permissions
4. Check that all prerequisites are installed
5. Ensure your virtual environment is activated

For more detailed information, see:
- `README.md` - Project overview
- `REQUIREMENTS.md` - Detailed specifications
- `PLAN.md` - Step-by-step build plan
- `thingsWeDid.md` - Progress tracking 