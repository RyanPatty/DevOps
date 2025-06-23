# Static-Site Deployer CLI
C:\Users\Ryan\Desktop\Work\BriteSystems\DevOps\static-site-deployer\infra>
**Ship any static build to S3 + CloudFront in one command, with zero long-lived keys and an automatic Lighthouse gate.**


npm run build           # Vite / next export / Hugo / plain HTML
deploy_site dist/       # <30 s later → live on CloudFront


---

## 🔥 Why you'll like it

| Feature | What it means |
|---------|---------------|
| **< 30 s deploy** | Delta-upload + single CDN invalidation |
| **Key-free CI** | GitHub OIDC role, no `AWS_ACCESS_KEY_ID` anywhere |
| **Quality gate** | Pipeline fails if Lighthouse **Perf AND A11y < 90** |
| **Rollback-ready** | S3 versioning keeps every release |

---

## 🏗️ Folder Layout

```
static-site-deployer/
├── cli/                 # Python package
│   ├── **init**.py
│   ├── main.py          # click entry-point → deploy_site
│   ├── hashutil.py      # SHA-256 helper
│   ├── uploader.py      # delta S3 sync
│   └── invalidate.py    # CloudFront invalidation
├── infra/               # Terraform stack
│   ├── backend.tf       # remote state config
│   ├── main.tf          # bucket + CloudFront
│   ├── oidc.tf          # GitHub OIDC IAM role
│   └── variables.tf
├── site-sample/         # tiny demo site (index.html)
├── .github/workflows/   # CI pipeline
│   └── deploy.yml
└── README.md / REQUIREMENTS.md
```

**What each thing does**

| Path | Purpose |
|------|---------|
| `cli/` | All Python logic: calculate file hashes, upload changed objects, call CDN invalidation. |
| `infra/` | Declarative AWS resources: private S3 bucket, CloudFront distro, IAM role for GitHub. |
| `site-sample/` | Minimal HTML page so you can test a deploy in 30 s. |
| `.github/workflows/deploy.yml` | Builds, deploys, then runs Lighthouse-CI; blocks if scores < 90. |

---

## 🛠️ Prerequisites

| Tool | Min version | Why |
|------|-------------|-----|
| **Python** | 3.11 | run the CLI |
| **Terraform** | 1.5 | manage AWS infra |
| **AWS CLI v2** | — | login via SSO |
| **Node** | 20 | Lighthouse-CI in pipeline |
| **Docker** | 20 | pinned CI image |

---

## ⚡ Quick Start

1. **Clone & bootstrap**

   ```powershell
   git clone https://github.com/youruser/static-site-deployer
   cd static-site-deployer
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e .                 # install CLI
   ```

2. **Provision AWS (one-time)**

   ```powershell
   cd infra
   terraform init
   terraform apply -var="bucket_name=my-static-bucket" `
                   -var="github_repo=youruser/static-site-deployer"
   ```

   *Outputs show the bucket name, CloudFront distribution ID, and public URL — save them as repo secrets.*

3. **Deploy your first site**

   ```powershell
   cd ..
   npm run build          # produces dist/
   $env:DEPLOY_BUCKET="your-bucket"
   $env:CF_DIST_ID="E123ABCXYZ"
   deploy_site dist/
   ```

   Open the printed CloudFront URL — you're live.

---

## 🤖 CI Pipeline (summary)

> Trigger: every push to `main` and every PR.

1. **Build** static site (`npm run build`).
2. **Deploy** via CLI inside Docker, using OIDC role.
3. **Audit** new URL with Lighthouse-CI.
4. **Comment** scores & URL on PR.
5. **Fail** job if Perf **or** A11y < 90.

---

## 🧩 CLI Flags

| Flag        | Description                                           | Default source                             |
| ----------- | ----------------------------------------------------- | ------------------------------------------ |
| `<folder>`  | Path to built assets (`dist/`, `out/`, etc.)          | —                                          |
| `--bucket`  | Target S3 bucket name                                 | `DEPLOY_BUCKET` env var or Secrets Manager |
| `--dist-id` | CloudFront distribution ID                            | `CF_DIST_ID` env var or Secrets Manager    |
| `--dry-run` | Show would-upload / would-invalidate, make no changes | Off                                        |

Exit codes: **0** ok, **1** arg error, **2** AWS error, **3** Lighthouse gate fail.

---

## 🛸 How it works (in plain words)

1. **Hash compare** — each local file's SHA-256 is compared to the S3 object's ETag; unchanged files are skipped.
2. **Upload delta** — only new/changed files are PUT, speeding deploys and saving S3 costs.
3. **Invalidate CDN** — every changed path is sent to CloudFront (max 1 000 per request) so users get fresh files.
4. **Auth strategy** —

   * *Local:* AWS SSO or named profile.
   * *CI:* GitHub OIDC → short-lived IAM role (no stored secrets).

---

## 🏗️ Infrastructure Architecture

### Terraform Remote State

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

---

## 🚀 Stretch ideas

* `deploy_site rollback --version <id>` — restore a previous S3 object version.
* Slack or Discord webhook notifications.
* Blue/green switch with a second bucket + CloudFront origin group.

---

## 📄 Licence

MIT — Have fun, no warranties.

---

> **Need more depth?** See `REQUIREMENTS.md` for the full spec and `infra/main.tf` for exact AWS resources.

---

## 🪟 Windows-Specific Setup

### Package Installation

**Option 1: Chocolatey (Recommended)**
```powershell
# Install Chocolatey first (run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install python terraform awscli jq git nodejs -y
```

**Option 2: Winget**
```powershell
winget install Python.Python.3.11
winget install HashiCorp.Terraform
winget install Amazon.AWSCLI
winget install Git.Git
winget install OpenJS.NodeJS
```

### PowerShell Execution Policy

If you encounter execution policy issues:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Environment Variables

For persistent environment variables across sessions, add to your PowerShell profile:
```powershell
# Edit profile
notepad $PROFILE

# Add these lines
$env:DEPLOY_BUCKET="your-bucket-name"
$env:CF_DIST_ID="your-distribution-id"
$env:CF_URL="https://your-cloudfront-url.net"
```

### Virtual Environment

Always activate your virtual environment before working:
```powershell
.venv\Scripts\Activate.ps1
```

To deactivate:
```powershell
deactivate
```
