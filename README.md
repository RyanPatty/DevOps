
# Static-Site Deployer CLI

**Ship any static build to S3 + CloudFront in one command, with zero long-lived keys and an automatic Lighthouse gate.**


npm run build           # Vite / next export / Hugo / plain HTML
deploy\_site dist/       # <30 s later → live on CloudFront


---

## 🔥 Why you’ll like it

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
│   ├── main.py          # click entry-point → deploy\_site
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

````

**What each “shit” does**

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

   ```bash
   git clone https://github.com/youruser/static-site-deployer
   cd static-site-deployer
   python -m venv .venv && source .venv/bin/activate
   pip install -e .                 # install CLI
````

2. **Provision AWS (one-time)**

   ```bash
   cd infra
   terraform init
   terraform apply -var="bucket_name=my-static-bucket" \
                   -var="github_repo=youruser/static-site-deployer"
   ```

   *Outputs show the bucket name, CloudFront distribution ID, and public URL — save them as repo secrets.*

3. **Deploy your first site**

   ```bash
   cd ..
   npm run build          # produces dist/
   export DEPLOY_BUCKET=your-bucket
   export CF_DIST_ID=E123ABCXYZ
   deploy_site dist/
   ```

   Open the printed CloudFront URL — you’re live.

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

1. **Hash compare** — each local file’s SHA-256 is compared to the S3 object’s ETag; unchanged files are skipped.
2. **Upload delta** — only new/changed files are PUT, speeding deploys and saving S3 costs.
3. **Invalidate CDN** — every changed path is sent to CloudFront (max 1 000 per request) so users get fresh files.
4. **Auth strategy** —

   * *Local:* AWS SSO or named profile.
   * *CI:* GitHub OIDC → short-lived IAM role (no stored secrets).

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

```
