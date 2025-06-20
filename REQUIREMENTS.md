### Static-Site Deployer CLI — Requirements & Specifications

---

#### 1. Objective

Provide a one-command tool (`deploy_site`) that takes a folder of pre-built static assets (HTML / CSS / JS / images) and:

1. Uploads only the changed files to an S3 bucket configured for static-website hosting.
2. Requests a CloudFront cache invalidation so the new content is served worldwide within minutes.
3. Runs entirely without long-lived AWS keys in source control or CI.
4. Fails a deployment if Lighthouse Performance **or** Accessibility scores drop below 90.

---

#### 2. Functional Requirements

| ID  | Requirement                                                                                                           |
| --- | --------------------------------------------------------------------------------------------------------------------- |
| F-1 | CLI command format: `deploy_site <folder> [--bucket] [--dist-id] [--dry-run] [--profile]`.                            |
| F-2 | Calculates a hash for every local file and skips uploads when the remote object’s hash matches.                       |
| F-3 | Batches all changed paths into one or more CloudFront invalidation requests (maximum 1 000 paths per request).        |
| F-4 | Displays colour-coded logs and a progress bar while uploading.                                                        |
| F-5 | Exit codes — **0** success, **1** invalid arguments, **2** AWS operation failed, **3** Lighthouse gate failed.        |
| F-6 | `--dry-run` flag lists the files that *would* upload and the paths that *would* be invalidated, but makes no changes. |

---

#### 3. Security Requirements

| ID  | Requirement                                                                                                                                       |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| S-1 | No static AWS access keys shall exist in code, Git history, or GitHub Secrets.                                                                    |
| S-2 | GitHub Actions must obtain credentials through an OIDC IAM role scoped only to S3 **PutObject/ListBucket** and CloudFront **CreateInvalidation**. |
| S-3 | Local executions must use AWS SSO or a named credentials profile, never hard-coded keys.                                                          |
| S-4 | (Optional) Bucket name and distribution ID may be stored in AWS Secrets Manager, encrypted with AWS-managed KMS.                                  |

---

#### 4. Non-Functional Requirements

| Category        | Target                                                                          |
| --------------- | ------------------------------------------------------------------------------- |
| Performance     | End-to-end deploy for a 5 MB bundle must complete in ≤ 30 seconds.              |
| Reliability     | CLI must retry AWS API calls up to three times on throttling or network errors. |
| Maintainability | Source must pass `black` formatting and `ruff` linting.                         |
| Cost            | Demo stack should remain under \$1 per month at low traffic levels.             |

---

#### 5. Infrastructure Requirements (Terraform-managed)

* One private S3 bucket with versioning, static-website hosting enabled, and Origin Access Control.
* One CloudFront distribution pointing to the bucket, forcing HTTPS and default root `index.html`.
* One IAM OIDC role trusted by GitHub with least-privilege permissions (upload + invalidate).
* (Optional) One Secrets Manager secret that stores `{bucket, dist_id}` in JSON.
* Terraform remote state stored in S3 with DynamoDB state lock.

---

#### 6. CI / CD Requirements (GitHub Actions)

1. Pipeline triggers on pushes to `main` and all pull-requests.
2. Steps in order:

   * Install Node 20 and build the static site (`npm ci && npm run build`).
   * Install Python 3.11 and run the CLI to deploy.
   * Run Lighthouse-CI against the CloudFront URL.
3. Pipeline must fail if Lighthouse Performance **or** Accessibility score is below 90.
4. Pipeline must post the deployed URL and Lighthouse scores as a pull-request comment.
5. (Optional) Slack notification on success or failure.

---

#### 7. Acceptance Criteria

* Terraform `plan` shows zero drift after the initial apply.
* Running `deploy_site` on a sample folder uploads changed files and outputs a CloudFront invalidation ID.
* Browser shows updated content at the CloudFront URL within 60 seconds of a deploy.
* GitHub Actions workflow passes with Lighthouse scores ≥ 90.
* Repository scan with `git secrets --scan` returns zero credential findings.

---

#### 8. Tooling Prerequisites

* Python 3.11
* Terraform 1.5 or higher
* AWS CLI v2 configured with SSO
* Node 20 (for Lighthouse-CI)
* Docker 20 (builds pinned CI image)

---

#### 9. Roles & Responsibilities

* **Developer** — builds static site, runs CLI locally, reviews pipeline results.
* **CI Pipeline** — automates deploy and quality checks on every commit.
* **AWS Account Owner** — approves IAM policies and pays the bill.

---

**End of Detailed Requirements**
