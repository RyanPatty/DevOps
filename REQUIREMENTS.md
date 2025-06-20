# Static-Site Deployer CLI  
**Detailed Requirements Specification**  
*(last update 2025-06-20)*  

---

## 1  Project Overview

### 1.1  Objective  
Deliver a Python command-line tool, `deploy_site`, that publishes a **pre-built static web folder** (HTML / CSS / JS / assets) to the public internet in **one command** by:

1. Syncing only changed files to an Amazon S3 bucket configured for static-website hosting.  
2. Requesting a CloudFront cache invalidation so new content propagates globally within minutes.  
3. Operating without storing long-lived AWS credentials anywhere in code, the repo, or CI.

### 1.2  Definition – “Static Build”  
A directory that contains *only* files which can be served verbatim by an object store or CDN.  
Examples:

| Framework / Tool            | Build Command                       | Output Folder |
|-----------------------------|-------------------------------------|---------------|
| Vite / CRA                  | `npm run build`                     | `dist/`       |
| Next.js (static export)     | `next build && next export -o out`  | `out/`        |
| Hugo / Jekyll               | `hugo` / `jekyll build`             | `public/`     |
| Plain HTML / CSS / JS       | none (author files manually)        | project root  |

No server-side rendering, runtime scripting, or Lambda@Edge is supported.

---

## 2  Scope

### 2.1  In Scope
* One S3 bucket + one CloudFront distribution (single environment).
* Terraform ≥ 1.5 for all AWS resources.
* GitHub Actions as the only CI/CD system.
* Lighthouse-CI quality gate in the pipeline.
* Optional Slack or Mattermost notification.

### 2.2  Out of Scope
* Multi-region replication, multi-environment promotion (staging → prod).
* Alternative CI platforms (GitLab, Jenkins, Azure DevOps).
* Live reload, incremental preview servers.
* Monitoring stacks (Prometheus, Grafana, ELK).

---

## 3  Stakeholders

| Role            | Responsibility                              |
|-----------------|---------------------------------------------|
| **Developer**   | Builds static site, runs CLI locally.        |
| **CI Pipeline** | Executes automated deploy on commit.         |
| **Reviewer**    | Verifies quality gate & release history.     |
| **AWS Account Owner** | Pays AWS bill, enforces IAM policy. |

---

## 4  Assumptions & Constraints

| # | Statement |
|---|-----------|
| A-1 | Developer and CI have permission to create IAM roles, S3 buckets, CloudFront distributions, and Secrets Manager secrets. |
| A-2 | Max bundle size tested: 100 MB, ≤ 10 000 objects. |
| A-3 | CloudFront invalidation quotas (1 000 paths per request, 1 000 requests / day) will not be exceeded in normal use. |
| A-4 | Local environment: macOS / Linux, Python 3.11+, Node 20+, Docker 20+. |

---

## 5  Functional Requirements

| ID  | Description |
|-----|-------------|
| **FR-1** | The CLI SHALL be invoked as `deploy_site <folder> [--bucket BUCKET] [--dist-id ID] [--dry-run] [--profile PROFILE]`. |
| **FR-2** | The CLI SHALL compute a hash (SHA-256) for each local file and skip upload when the hash matches the current S3 object’s `ETag` (zero-byte PUT). |
| **FR-3** | After uploading, the CLI SHALL batch all changed object paths into one or more `CreateInvalidation` calls, each with ≤ 1 000 paths. |
| **FR-4** | The CLI SHALL print coloured, timestamped logs and a byte-progress bar using `tqdm`. |
| **FR-5** | Exit codes: `0` success, `1` invalid arguments, `2` AWS operation failed, `3` Lighthouse quality gate failed. |
| **FR-6** | The `--dry-run` flag SHALL list files that would be uploaded and paths that would be invalidated without calling AWS APIs. |

---

## 6  Security Requirements

| ID  | Requirement |
|-----|-------------|
| **SEC-1** | No static AWS access keys SHALL exist in source code, Git history, or GitHub Secrets. |
| **SEC-2** | GitHub Actions SHALL authenticate via **OIDC** and assume an IAM role scoped to: `s3:PutObject`, `s3:ListBucket`, `cloudfront:CreateInvalidation`. |
| **SEC-3** | Local executions SHALL authenticate via AWS SSO or a named credential profile. |
| **SEC-4** | *(Optional)* Bucket name and CloudFront distribution ID MAY be stored in AWS Secrets Manager and encrypted with AWS-managed KMS. |

---

## 7  Non-Functional Requirements

| Category      | Requirement |
|---------------|-------------|
| **Performance** | End-to-end deploy for a 5 MB bundle SHALL complete in ≤ 30 seconds. |
| **Reliability** | CLI SHALL retry AWS API calls up to 3 times on throttling or network errors with exponential backoff. |
| **Maintainability** | Source code SHALL conform to `black` formatting and `ruff` linting. |
| **Quality Gate** | CI job SHALL fail if Lighthouse Performance **or** Accessibility < 90. |
| **Cost** | Baseline stack SHOULD remain under USD \$1 per month at low traffic levels. |

---

## 8  Infrastructure Requirements (Terraform)

### 8.1  Resources
| Resource | Configuration Highlights |
|----------|--------------------------|
| **S3 Bucket** | `website` block, **versioning enabled**, ACL `private`, default encryption AES-256. |
| **CloudFront Distribution** | Origin = bucket OAC, HTTPS only, default TTL 300 s, `index.html` root object. |
| **IAM OIDC Role** | Trust = GitHub provider, permissions per SEC-2. |
| **(Optional) Secrets Manager Secret** | JSON `{ "bucket": "...", "dist_id": "..." }`. |

### 8.2  State Management
* Terraform state stored in an S3 backend (`infra/tfstate` key).  
* State locking enabled via DynamoDB table `tf-state-lock`.

---

## 9  CLI Interface Specification

| Argument / Flag | Type | Default | Notes |
|-----------------|------|---------|-------|
| `<folder>` | path | — | Must exist and contain at least one `.html` file. |
| `--bucket` | string | ENV `DEPLOY_BUCKET` or SM secret | S3 bucket name. |
| `--dist-id` | string | ENV `CF_DIST_ID` or SM secret | CloudFront distribution ID. |
| `--dry-run` | bool | `false` | No changes—print only. |
| `--profile` | string | default profile | Local only; ignored in CI. |

---

## 10  CI/CD Requirements (GitHub Actions)

| ID | Step | Success Criteria |
|----|------|------------------|
| **CI-1** | Trigger on `push` to `main` and all pull requests. | Workflow starts. |
| **CI-2** | Install Node 20, build static site (`npm ci && npm run build`). | Exit 0. |
| **CI-3** | Install Python 3.11, pip-install project, run `deploy_site`. | CLI exit 0. |
| **CI-4** | Run `treosh/lighthouse-ci-action` on CloudFront URL. | Perf ≥ 90 AND A11y ≥ 90. |
| **CI-5** | Post PR comment with deployed URL and Lighthouse scores. | Comment visible. |
| **CI-6** | *(Optional)* Slack notification via `8398a7/action-slack`. | Message sent. |

---

## 11  Local Development Setup

```bash
# tools
brew install pyenv terraform awscli

# Python env
pyenv install 3.11.7 && pyenv virtualenv 3.11.7 deploy-env
pyenv activate deploy-env
pip install -e .

# AWS SSO
aws sso login --profile my-sso

# Provision infra
cd infra && terraform init && terraform apply
````

---

## 12  Acceptance Criteria

| ✓ | Test                                                                                      |
| - | ----------------------------------------------------------------------------------------- |
|   | `terraform plan` shows **no drift** after initial apply.                                  |
|   | `deploy_site dist/` uploads only changed files; console shows CloudFront invalidation ID. |
|   | Browser refresh within 60 s reveals updated content.                                      |
|   | GitHub Actions workflow passes with Lighthouse Perf & A11y ≥ 90.                          |
|   | `git secrets --scan` returns zero findings.                                               |

---

## 13  Glossary

| Term              | Meaning                                                             |
| ----------------- | ------------------------------------------------------------------- |
| **OIDC**          | OpenID Connect – GitHub’s mechanism for short-lived AWS tokens.     |
| **OAC**           | Origin Access Control – newer CloudFront → S3 auth replacing OAI.   |
| **Delta Upload**  | Only PUT objects whose hash differs from bucket version.            |
| **Invalidate**    | CloudFront API call that purges cached files so new versions serve. |
| **Lighthouse-CI** | Headless Chrome audit scoring performance and accessibility.        |

---

**End of Specification**

```

