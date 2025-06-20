# "Static-Site Deployer CLI" – Step-By-Step Build Plan (Windows Edition)

*Use each numbered step in order; read the little side notes (➜) to understand **why** you're doing it.*

---

## 0  Prep your workstation (15 min)

| Action             | Command / Note                                            |
| ------------------ | --------------------------------------------------------- |
| Install Chocolatey | Run PowerShell as Administrator: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))` |
| Install core tools | `choco install python terraform awscli jq git nodejs -y`   |
| Create project dir | `mkdir static-site-deployer; cd static-site-deployer; git init -b main` |

> ➜ **Why:** clean workspace keeps dependencies isolated and makes it easy to wipe/re-clone.

---

## 1  Python environment (5 min)

| Action             | Command                                                                             |
| ------------------ | ----------------------------------------------------------------------------------- |
| Create virtualenv  | `python -m venv .venv`                                                              |
| Activate           | `.venv\Scripts\Activate.ps1`                                                        |
| Confirm            | `python -V`  → shows `3.11.x`                                                       |

> ➜ A dedicated virtualenv prevents package conflicts with other projects.

---

## 2  Basic repo scaffold (5 min)

```powershell
mkdir cli, infra, .github\workflows, site-sample
New-Item cli\__init__.py -ItemType File
New-Item README.md -ItemType File
New-Item REQUIREMENTS.md -ItemType File
"<h1>Hello world</h1>" | Out-File -FilePath site-sample\index.html -Encoding UTF8
git add . ; git commit -m "chore: scaffold repo"
```

> ➜ You now have three clear zones: *cli*, *infra*, and *CI*.

---

## 3  AWS account bootstrap (15 min **one-time**)

1. **Log in with SSO**
   `aws configure sso --profile dev`
2. **Create backend bucket & lock table** *(only once per AWS account)*

   ```powershell
   aws s3 mb s3://YOUR-TF-STATE-BUCKET
   aws dynamodb create-table `
     --table-name tf-state-lock `
     --attribute-definitions AttributeName=LockID,AttributeType=S `
     --key-schema AttributeName=LockID,KeyType=HASH `
     --billing-mode PAY_PER_REQUEST
   ```

> ➜ Terraform remote state avoids "state file in Git" headaches; the lock table stops simultaneous applies.

---

## 4  Terraform backend file (2 min)

*`infra/backend.tf`* – just three lines pointing to that bucket + lock table.
Commit with message `infra: add remote backend`.

---

## 5  Create S3 bucket & CloudFront (30 min)

1. In `infra/main.tf` declare:

   * S3 bucket (`versioning`, `website` block).
   * CloudFront origin-access control + distribution (HTTPS only, root =`index.html`).
2. `terraform init && terraform validate`
3. `terraform plan -var="bucket_name=YOUR-BUCKET" -var="github_repo=YOURUSER/static-site-deployer"`
4. `terraform apply ...`  **Save** the outputs (bucket, dist ID, URL).

> ➜ The bucket remains **private**; CloudFront pulls via Origin Access Control (OAC).

---

## 6  IAM OIDC role (GitHub) (15 min)

Add a new file `infra/oidc.tf` that:

* trusts GitHub's OIDC provider
* limits `sts:AssumeRoleWithWebIdentity` to `repo:YOURUSER/static-site-deployer:ref:refs/heads/main`
* grants **only** `s3:PutObject/ListBucket` and `cloudfront:CreateInvalidation`.

Re-`terraform apply`. Copy the role ARN for later.

> ➜ This is what removes long-lived keys from CI entirely.

---

## 7  Local Secrets (1 min)

Save the three Terraform outputs to your PowerShell session for easy testing:

```powershell
$env:DEPLOY_BUCKET="YOUR-BUCKET"
$env:CF_DIST_ID="YOUR-DIST-ID"
$env:CF_URL="https://XXXX.cloudfront.net"
```

---

## 8  Python package skeleton (3 min)

*`pyproject.toml`* lists dependencies:

```
boto3, click, tqdm, colorama
```

Install: `pip install -e .`

> ➜ Boto3 for AWS calls, Click for CLI flags, TQDM for progress bar, Colorama for cross-platform colours.

---

## 9  CLI hash & upload logic (30 min)

1. `cli/hashutil.py` → tiny `md5(path)` helper.
2. `cli/uploader.py` → loops over files, compares hash to `ETag`, calls `s3.upload_file` when different.
3. Log per-file status: **Uploading**, **Skipping**.
4. Unit-test hash util: `pytest tests/test_hash.py`.

> ➜ Comparing hashes minimises S3 PUT cost and speeds deploy.

---

## 10  CloudFront invalidation logic (10 min)

Function in `cli/invalidate.py`:

* Accept list of changed keys → prepend `/` → chunk into batches ≤ 1000.
* Call `create_invalidation` once per batch.

> ➜ CDN won't cache bust unless you send invalidation; batching saves API quota.

---

## 11  Entry-point script (10 min)

`cli/main.py`:

* Glue flags to uploader + invalidator.
* Implement `--dry-run` path.
* Map exit codes: 0 OK, 1 arg error, 2 AWS error.

Add console script in `pyproject.toml`:
`deploy_site = "cli.main:cli"`

Test locally:

```powershell
deploy_site site-sample/ --bucket $env:DEPLOY_BUCKET --dist-id $env:CF_DIST_ID
```

Check CloudFront URL updates.

---

## 12  Lighthouse manual sanity (5 min)

```powershell
npx lhci collect --url=$env:CF_URL
npx lhci upload --target=temporary-public-storage
```

Note scores—need ≥ 90 Perf & A11y to pass CI later.

---

## 13  GitHub Secrets / Vars (5 min)

* **Settings → Actions → New Repository Secret**

  * `CF_DIST_ID`, `DEPLOY_BUCKET`, `CF_URL`
* **Settings → Secrets → Actions → Add OIDC role ARN** (`AWS_ROLE_TO_ASSUME`).

> ➜ The job requests a short-lived token and swaps it for that role.

---

## 14  GitHub Actions workflow (20 min)

Steps in order:

1. Checkout
2. Setup Node, build site (`npm run build` or copy `site-sample`)
3. Setup Python, `pip install .`
4. Run `deploy_site dist/`
5. Lighthouse-CI action; fail if `< 90`
6. PR comment with URL and scores (`devops-infra/action-pull-request-commenter`)
7. *(optional)* Slack webhook.

Commit: `ci: add deploy workflow`.

---

## 15  Push + watch (5 min)

```powershell
git add . ; git commit -m "feat: MVP deploy CLI" ; git push -u origin main
```

Open **Actions** tab → confirm pipeline:

* uploads objects
* prints invalidation ID
* runs Lighthouse
* posts scores.

---

## 16  Dry-run & failure paths (10 min)

* Run `deploy_site site-sample/ --dry-run` → expect **no** S3/CF calls.
* Temporarily break bucket env var → expect exit 1.
* Throttle network or just kill Wi-Fi → expect exit 2 after retries.

> ➜ Confirms error handling and exit codes match spec.

---

## 17  Lint & format guards (5 min)

Add `ruff` and `black` pre-commit hook:

```powershell
pip install ruff black pre-commit
pre-commit install
```

Commit style fixes.

---

## 18  README & badges (10 min)

* Explain one-liner, feature table, prerequisites, quick start.
* Add CI status badge:
  `[![Deploy](https://github.com/<user>/<repo>/actions/workflows/deploy.yml/badge.svg)]`

---

## 19  (OPTIONAL) Slack notification (10 min)

* Add `action-slack` step in workflow.
* Create Incoming Webhook in Slack workspace; save URL as secret.

---

## 20  Acceptance checklist (5 min)

Tick every line in the **Requirements Acceptance** section:

1. `terraform plan` no drift ✓
2. `deploy_site` < 30 s ✓
3. Browser updates < 1 min ✓
4. GitHub Actions Lighthouse ≥ 90 ✓
5. `git secrets --scan` clean ✓

---

## 21  Tag v1.0 (2 min)

```powershell
git tag v1.0.0 -m "First stable release"
git push --tags
```

> ➜ Now you can reference `v1.0.0` in your résumé or interview.

---

### You're done!

You have a fully automated, key-less, quality-guarded static site deploy pipeline — built incrementally with clear understanding at every step.

---

## Windows-Specific Notes

### PowerShell Execution Policy
If you encounter execution policy issues:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path Separators
- Use backslashes (`\`) for Windows paths in PowerShell
- Use forward slashes (`/`) in Git and cross-platform tools

### Environment Variables
- PowerShell: `$env:VARIABLE_NAME="value"`
- CMD: `set VARIABLE_NAME=value`
- For persistence across sessions, add to your PowerShell profile

### Virtual Environment Activation
- PowerShell: `.venv\Scripts\Activate.ps1`
- CMD: `.venv\Scripts\activate.bat`

### Package Management
- Chocolatey: `choco install package-name`
- Winget: `winget install package-name`
- Python: `pip install package-name`
