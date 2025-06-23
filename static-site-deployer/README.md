# Static-Site Deployer CLI

A production-ready CLI tool for deploying static websites to AWS S3 + CloudFront with intelligent delta uploads, automatic cache invalidation, and quality gates.

## 📋 Description

The Static-Site Deployer CLI automates the deployment of static websites to AWS infrastructure. It intelligently uploads only changed files, creates CloudFront cache invalidations, and integrates with Lighthouse CI for performance monitoring. Built with security-first principles, it eliminates the need for long-lived AWS credentials in CI/CD pipelines.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **CLI Framework** | Python + Click | Command-line interface |
| **AWS SDK** | boto3 | AWS service integration |
| **Infrastructure** | Terraform | Infrastructure as Code |
| **CDN** | CloudFront | Global content delivery |
| **Storage** | S3 | Static file hosting |
| **CI/CD** | GitHub Actions | Automated deployment |
| **Quality Gates** | Lighthouse CI | Performance monitoring |
| **Authentication** | AWS OIDC | Secure CI/CD access |

## ✨ Features

### 🚀 Performance
- **Delta Uploads**: Only uploads changed files using MD5 hash comparison
- **Fast Deployments**: Complete deployments in <30 seconds for typical sites
- **Smart Caching**: Automatic CloudFront invalidation for changed files only

### 🔒 Security
- **Zero Long-lived Keys**: Uses AWS OIDC for CI/CD authentication
- **Private S3 Buckets**: Secure storage with Origin Access Control
- **Least Privilege**: Minimal IAM permissions for deployment operations

### 🎯 Quality Assurance
- **Lighthouse Integration**: Automatic performance and accessibility testing
- **Quality Gates**: Deployment fails if scores drop below 90
- **Rollback Ready**: S3 versioning preserves all deployments

### 🛠️ Developer Experience
- **Simple CLI**: One command deployment
- **Dry Run Mode**: Preview changes before deployment
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Progress Tracking**: Real-time upload progress with colored output

## 🎯 Use Cases

### Static Site Deployment
Deploy any static site built with modern frameworks:
```powershell
# React/Vue/Angular
npm run build
deploy_site dist/ --profile production

# Next.js
npm run export
deploy_site out/ --profile production

# Hugo/Jekyll
hugo
deploy_site public/ --profile production
```

### CI/CD Integration
Automate deployments in GitHub Actions with zero secrets:
```yaml
- name: Deploy to AWS
  run: deploy_site dist/
  env:
    AWS_ROLE_TO_ASSUME: ${{ secrets.AWS_ROLE_TO_ASSUME }}
```

### Multi-Environment Deployments
Deploy to different environments with different configurations:
```powershell
# Staging
deploy_site dist/ --bucket staging-site --dist-id E123ABC --profile staging

# Production
deploy_site dist/ --bucket prod-site --dist-id E456DEF --profile production
```

### Performance Monitoring
Automatically test and monitor site performance:
```powershell
# Deploy with quality gates
deploy_site dist/ --profile production
# Automatically runs Lighthouse and fails if scores < 90
```

## 🏗️ System Architecture

### Infrastructure Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Site   │    │   S3 Bucket     │    │  CloudFront     │
│   (Local)       │───▶│   (Private)     │◀───│   (CDN)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Terraform     │    │   Lighthouse    │
                       │   (State)       │    │   (Quality)     │
                       └─────────────────┘    └─────────────────┘
```

### Deployment Flow

1. **File Analysis**: CLI scans local directory and calculates MD5 hashes
2. **Hash Comparison**: Compares local hashes with S3 object ETags
3. **Delta Upload**: Uploads only files with different hashes
4. **Cache Invalidation**: Creates CloudFront invalidation for changed paths
5. **Quality Check**: Runs Lighthouse CI against deployed URL
6. **Success/Failure**: Reports results and exits with appropriate code

### Security Model

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub OIDC   │───▶│   AWS STS       │───▶│   IAM Role      │
│   (Identity)    │    │   (Token)       │    │   (Permissions) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   S3 + CF       │
                       │   (Resources)   │
                       └─────────────────┘
```

### Data Flow

```
Local Files → Hash Calculation → S3 Upload → CloudFront Invalidation → Quality Check
     │              │              │              │                    │
     ▼              ▼              ▼              ▼                    ▼
  MD5 Hash    Compare ETags    PUT Object    Create Invalidation   Lighthouse
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI v2
- Terraform 1.5+
- Node.js 20+ (for Lighthouse)

### Installation
```powershell
# Clone and setup
git clone https://github.com/ryanpatty/static-site-deployer
cd static-site-deployer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

# Deploy infrastructure
cd infra
terraform apply -var="bucket_name=my-site" -var="github_repo=username/repo"

# Deploy your site
deploy_site site-sample --profile your-aws-profile
```

### Basic Usage
```powershell
# Deploy with environment variables
$env:DEPLOY_BUCKET="my-bucket"
$env:CF_DIST_ID="E123ABC"
deploy_site dist/ --profile production

# Dry run to preview changes
deploy_site dist/ --dry-run --profile production

# Deploy and wait for invalidation
deploy_site dist/ --wait --profile production
```

## 📊 Performance Metrics

| Metric | Target | Typical Result |
|--------|--------|----------------|
| **Deployment Time** | <30 seconds | 15-25 seconds |
| **Lighthouse Performance** | ≥90 | 95-100 |
| **Lighthouse Accessibility** | ≥90 | 95-100 |
| **Monthly Cost** | <$1 | $0.50-0.80 |

## 🔧 Configuration

### Environment Variables
```powershell
$env:DEPLOY_BUCKET="your-s3-bucket"
$env:CF_DIST_ID="your-cloudfront-distribution-id"
$env:CF_URL="https://your-cloudfront-url.cloudfront.net"
```

### CLI Options
```powershell
deploy_site <folder> [--bucket BUCKET] [--dist-id DIST_ID] 
           [--profile PROFILE] [--dry-run] [--wait]
```

### Exit Codes
- **0**: Success
- **1**: Invalid arguments
- **2**: AWS operation failed
- **3**: Lighthouse quality gate failed

## 📚 Documentation

- **[howTo.md](howTo.md)**: Complete setup and usage guide
- **[REQUIREMENTS.md](REQUIREMENTS.md)**: Detailed specifications
- **[PLAN.md](PLAN.md)**: Step-by-step build plan
- **[thingsWeDid.md](thingsWeDid.md)**: Progress tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the [troubleshooting guide](howTo.md#troubleshooting)
2. Review the [requirements](REQUIREMENTS.md)
3. Open an issue on GitHub

---

**Built with ❤️ for the DevOps community** 