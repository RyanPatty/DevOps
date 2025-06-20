```markdown
# Static-Site Deployer CLI

**One command → world-wide update.**  
Give any pre-built front-end bundle (React + Vite, `next export`, Hugo, plain HTML—whatever) a 30-second path to AWS S3 + CloudFront, with no long-lived keys and a Lighthouse quality gate in CI.

---

## ✨ What You Get

| 🚀 Fast | < 30 s deploy for a 5 MB site |
|---------|------------------------------|
| 🔒 Key-free | GitHub OIDC role in CI, AWS SSO locally |
| 🟢 Quality | Deploy fails if Lighthouse **Perf & A11y < 90** |
| ↩️ Rollback | Every version kept via S3 object versioning |

---

## 🗺️ 30-Second Tour

```

npm run build          # or next export / hugo / gatsby build
deploy\_site dist/      # upload changed files, invalidate CDN

```

**Behind the curtain**

```

┌─ you / CI ─┐                ┌─ S3 bucket (static, versioned) ─┐
│deploy\_site │── put objects ─▶                               │
└────────────┘                └─ CloudFront CDN (https) ◀──────┘
↳  CreateInvalidation  ↲

````

*Infra is codified in Terraform; CI runs the CLI inside Docker, then audits the live URL with Lighthouse-CI.*

---

## 🛠️  Prerequisites

| Tool | Min Version | Notes |
|------|-------------|-------|
| Python | 3.11 | `pyenv` recommended |
| Terraform | 1.5 | state in S3 w/ Dynamo lock |
| AWS CLI | v2 | SSO profile set up |
| Node | 20 | Lighthouse-CI in pipeline |
| Docker | 20 | Builds pinned action image |

---

## ⚡ Quick Start

1. **Clone & bootstrap**

   ```bash
   git clone https://github.com/youruser/static-site-deployer
   cd static-site-deployer
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
````

2. **Deploy the infra (one-time)**

   ```bash
   cd infra
   terraform init
   terraform apply      # creates bucket, CDN, OIDC role
   ```

3. **Publish your first site**

   ```bash
   cd ..
   npm run build        # produces dist/
   deploy_site dist/    # uses your AWS profile
   ```

   Output ends with the CloudFront URL—open it and you’re live.

---

## 🤖  GitHub Actions Pipeline

`.github/workflows/deploy.yml`

```
on: push:
  branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci && npm run build
      - uses: actions/setup-python@v5
        with: { python-version: 3.11 }
      - run: |
          pip install .
          deploy_site dist/
      - uses: treosh/lighthouse-ci-action@v11
        with:
          urls: https://${{ env.CF_URL }}
```

The job fails if Lighthouse Performance or Accessibility drops below 90.

---

## 🧩 CLI Flags

| Flag        | Default                          | Description                                 |
| ----------- | -------------------------------- | ------------------------------------------- |
| `<folder>`  | –                                | built assets (dist/, out/, public/)         |
| `--bucket`  | env `DEPLOY_BUCKET` or SM secret | target S3 bucket                            |
| `--dist-id` | env `CF_DIST_ID` or SM secret    | CloudFront distro                           |
| `--dry-run` | `false`                          | show uploads/invalidation but don’t execute |

---

## 🏗️  How It Works

1. **Delta sync** – file hash vs S3 ETag, upload only changes.
2. **Batch invalidate** – changed paths grouped (≤ 1000) and sent to CloudFront.
3. **Least-priv IAM** – role allows `s3:PutObject`, `s3:ListBucket`, `cloudfront:CreateInvalidation` only.
4. **Zero keys** – GitHub gets a short-lived STS token via OIDC; local dev uses AWS SSO.

---

## 🚀  Stretch Goals

* `deploy_site rollback --version <id>` – revert to any previous S3 object version.
* Slack webhook on success/failure.
* Blue/green bucket swap with origin fail-over.

---

## 📜  Licence

MIT – do whatever, just don’t blame me.

---

Happy instant-deploying! Pull requests welcome.

```
