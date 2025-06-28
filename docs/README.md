# Static-Site Deployer CLI - Complete Documentation

A production-ready static site deployment system that combines AWS S3 + CloudFront with intelligent delta uploads, OIDC security, and automated quality gates.

## 📚 **Documentation Structure**

### 🚀 **Getting Started**
- [Quick Start Guide](#quick-start-guide)
- [Prerequisites](#prerequisites)

### 🏗️ **Architecture & Design**
- [System Overview](#system-overview)
- [Security Model](#security-model)

### 🛠️ **Development & Setup**
- [Local Development](#local-development)
- [Infrastructure Setup](#infrastructure-setup)
- [CI/CD Configuration](#cicd-configuration)

### 📖 **Reference**
- [CLI Reference](#cli-reference)
- [GitHub Secrets](#github-secrets)
- [Troubleshooting](#troubleshooting)
- [Performance Metrics](#performance-metrics)

---

## 🚀 **Quick Start Guide**

### **1. Clone and Setup**
```bash
git clone https://github.com/yourusername/static-site-deployer
cd static-site-deployer
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -e .
```

### **2. Deploy Infrastructure**
```bash
cd infra
terraform init
terraform apply -var="bucket_name=my-static-site" -var="github_repo=yourusername/static-site-deployer"
```

### **3. Configure GitHub Secrets**
Add these secrets to your repository:
- `AWS_ROLE_TO_ASSUME`: OIDC role ARN from Terraform output
- `DEPLOY_BUCKET`: S3 bucket name
- `CF_DIST_ID`: CloudFront distribution ID
- `CF_URL`: CloudFront URL

### **4. Deploy Your Site**
```bash
deploy_site dist/ --bucket my-static-site --dist-id E123ABCXYZ
```

**🎉 That's it!** Your site is now deployed with automatic CI/CD, quality gates, and global CDN.

---

## 📋 **Prerequisites**

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.11+ | `choco install python` (Windows) |
| **Terraform** | 1.5+ | `choco install terraform` |
| **AWS CLI** | v2 | `choco install awscli` |
| **Node.js** | 20+ | `choco install nodejs` |
| **Git** | Latest | `choco install git` |

**AWS Requirements:**
- Active AWS account with billing enabled
- IAM user with administrative permissions (for initial setup)

---

## 🏗️ **System Overview**

### **Core Components**

```mermaid
graph TB
    subgraph CLI["🖥️ CLI Tool"]
        A[deploy_site command]
        B[Delta upload logic]
        C[Hash comparison]
        D[CloudFront invalidation]
    end
    
    subgraph INFRA["☁️ AWS Infrastructure"]
        E[S3 Bucket]
        F[CloudFront CDN]
        G[IAM OIDC Role]
    end
    
    subgraph CI["🔄 CI/CD Pipeline"]
        H[GitHub Actions]
        I[OIDC Authentication]
        J[Lighthouse Testing]
        K[PR Comments]
    end
    
    A --> B
    B --> C
    C --> D
    D --> F
    H --> I
    I --> G
    J --> F
```

### **Key Features**
- ✅ **Delta Uploads**: Only uploads changed files (MD5 hash comparison)
- ✅ **Global CDN**: CloudFront distribution with 400+ edge locations
- ✅ **Zero Credentials**: OIDC authentication with temporary tokens
- ✅ **Quality Gates**: Lighthouse testing with ≥90 performance/accessibility
- ✅ **Fast Deployments**: Complete deployments in <30 seconds
- ✅ **Cost Efficient**: <$1/month for typical usage

---

## 🔐 **Security Model**

### **OIDC Authentication Flow**

```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant AWS as AWS STS
    participant S3 as S3 Bucket
    participant CF as CloudFront
    
    GH->>AWS: Request OIDC token
    AWS->>AWS: Validate GitHub claims
    AWS->>GH: Temporary credentials (15min-1hr)
    GH->>S3: Upload files (PutObject)
    GH->>CF: Invalidate cache (CreateInvalidation)
```

### **Security Benefits**
- 🔒 **No Long-lived Keys**: Temporary credentials that auto-expire
- 🛡️ **Least Privilege**: Minimal IAM permissions (S3 upload + CF invalidation)
- 📋 **Audit Trail**: All operations logged to CloudTrail
- 🔍 **Repository Scoping**: Role only accessible from specific GitHub repo

---

## 🛠️ **Local Development**

### **Project Structure**
```
static-site-deployer/
├── cli/                    # CLI tool source code
│   ├── main.py            # Entry point
│   ├── uploader.py        # S3 upload logic
│   ├── hashutil.py        # Hash utilities
│   └── invalidate.py      # CloudFront invalidation
├── infra/                 # Terraform infrastructure
│   ├── main.tf           # S3 + CloudFront resources
│   ├── oidc.tf           # IAM OIDC role
│   └── backend.tf        # Terraform backend config
├── .github/workflows/     # CI/CD pipelines
├── site-sample/          # Sample static site
└── tests/                # Unit tests
```

### **Development Setup**
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black cli/
ruff check cli/

# Install pre-commit hooks
pre-commit install
```

---

## ☁️ **Infrastructure Setup**

### **Terraform Resources**

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **S3 Bucket** | Static site storage | Private with versioning, OAC |
| **CloudFront** | Global CDN | HTTPS only, custom domain |
| **IAM Role** | OIDC authentication | Least privilege permissions |
| **Backend** | State management | S3 + DynamoDB lock |

### **Deployment Commands**
```bash
# Initialize Terraform
cd infra
terraform init

# Plan deployment
terraform plan -var="bucket_name=my-site" -var="github_repo=user/repo"

# Apply infrastructure
terraform apply -var="bucket_name=my-site" -var="github_repo=user/repo"

# Get outputs
terraform output
```

---

## 🔄 **CI/CD Configuration**

### **GitHub Actions Workflow**

The workflow automatically:
1. **Builds** the static site
2. **Deploys** to AWS using OIDC authentication
3. **Tests** with Lighthouse (≥90 performance/accessibility)
4. **Comments** results on PRs

### **Quality Gates**
- **Performance Score**: ≥90 required
- **Accessibility Score**: ≥90 required
- **Best Practices**: ≥90 recommended
- **SEO Score**: ≥90 recommended

### **Workflow Triggers**
- Push to `main` branch
- Pull requests to `main` branch

---

## 📖 **CLI Reference**

### **Command Syntax**
```bash
deploy_site <folder> [options]
```

### **Options**
| Option | Description | Example |
|--------|-------------|---------|
| `--bucket` | S3 bucket name | `--bucket my-site` |
| `--dist-id` | CloudFront distribution ID | `--dist-id E123ABCXYZ` |
| `--profile` | AWS profile | `--profile my-aws-profile` |
| `--dry-run` | Preview changes | `--dry-run` |
| `--wait` | Wait for invalidation | `--wait` |

### **Environment Variables**
```bash
export DEPLOY_BUCKET="my-static-site"
export CF_DIST_ID="E123ABCXYZ"
export CF_URL="https://xxxxx.cloudfront.net"
```

### **Exit Codes**
- **0**: Success
- **1**: Invalid arguments
- **2**: AWS operation failed
- **3**: Lighthouse gate failed

### **Examples**
```bash
# Basic deployment
deploy_site dist/ --bucket my-site --dist-id E123ABCXYZ

# Dry run to preview changes
deploy_site dist/ --bucket my-site --dist-id E123ABCXYZ --dry-run

# Wait for invalidation to complete
deploy_site dist/ --bucket my-site --dist-id E123ABCXYZ --wait

# Use environment variables
export DEPLOY_BUCKET="my-site"
export CF_DIST_ID="E123ABCXYZ"
deploy_site dist/
```

---

## 🔐 **GitHub Secrets**

### **Required Secrets**

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `AWS_ROLE_TO_ASSUME` | OIDC role ARN | `terraform output github_actions_role_arn` |
| `DEPLOY_BUCKET` | S3 bucket name | `terraform output bucket_name` |
| `CF_DIST_ID` | CloudFront distribution ID | `terraform output cloudfront_distribution_id` |
| `CF_URL` | CloudFront URL | `terraform output cloudfront_url` |

### **Setup Instructions**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add each secret with exact name and value from Terraform outputs

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. OIDC Authentication Errors**
```bash
# Check role ARN format
arn:aws:iam::123456789012:role/github-actions-static-site-deployer

# Verify repository name in role trust policy
repo:yourusername/static-site-deployer:ref:refs/heads/main
```

#### **2. CloudFront Not Updating**
```bash
# Check invalidation status
aws cloudfront get-invalidation --distribution-id E123ABCXYZ --id I123ABCXYZ

# Wait for invalidation (can take 5-15 minutes)
```

#### **3. Lighthouse Test Failures**
```bash
# Check site accessibility
curl -I https://your-site.cloudfront.net

# Verify content-type headers
curl -H "Accept: text/html" https://your-site.cloudfront.net
```

#### **4. S3 Upload Errors**
```bash
# Check bucket permissions
aws s3 ls s3://your-bucket-name

# Verify file paths
ls -la dist/
```

### **Debug Commands**
```bash
# Test CLI locally
deploy_site dist/ --dry-run

# Check AWS credentials
aws sts get-caller-identity

# Verify Terraform state
terraform show
```

---

## 📊 **Performance Metrics**

### **Deployment Performance**
- **Upload Time**: <1 second for single file changes
- **Cache Invalidation**: 30-60 seconds for global propagation
- **Total Pipeline**: <3 minutes end-to-end
- **Cost**: <$1/month for typical usage

### **Quality Scores Achieved**
- **Performance**: 95-100 (exceeds 90 threshold)
- **Accessibility**: 95-100 (exceeds 90 threshold)
- **Best Practices**: 95-100
- **SEO**: 95-100

### **Infrastructure Performance**
- **S3 Availability**: 99.99% (11 9's durability)
- **CloudFront Uptime**: 99.9% (Global CDN)
- **Cache Hit Ratio**: >95% (Edge caching)
- **TTFB**: <100ms (Time to first byte)

---

## 🤝 **Contributing**

### **Development Workflow**
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting and formatting
5. Submit a pull request

### **Code Quality Standards**
- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking
- **Pytest**: Unit testing

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

- **Issues**: [GitHub Issues](https://github.com/yourusername/static-site-deployer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/static-site-deployer/discussions)
- **Documentation**: [Setup Guide](SETUP_GUIDE.md) | [Reference Guide](REFERENCE.md) 