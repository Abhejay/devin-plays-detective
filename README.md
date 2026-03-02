# Automated Security Auto-Remediation with CodeQL & Devin AI

This repository demonstrates a fully automated, agentic CI/CD workflow that identifies security vulnerabilities using **GitHub CodeQL** and autonomously orchestrates **Devin AI** to write, verify, and propose fixes via Pull Requests.

## Features & Highlights

### 1. The "Vulnerable Playground" App
To effectively demonstrate the workflow, this repository contains a sample Python Flask application artificially seeded with critical OWASP vulnerabilities:
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Server-Side Request Forgery (SSRF - CWE-918)
- External Entity Injection (XXE - CWE-611)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Insecure Deserialization (CWE-502)
- Open Redirect (CWE-601)
- Hardcoded Credentials & Weak Cryptography

### 2. Intelligent Alert Batching
Rather than firing off a monolithic request that overwhelms an AI context window, or creating disjointed PRs for every single finding, a custom JavaScript GitHub Action step parses CodeQL's SARIF output and groups alerts by **vulnerability type**.

### 3. The "Stacked PR" Architecture (Zero Merge Conflicts)
A common failure pattern in automated remediation (often seen with basic Dependabot implementations) is generating multiple parallel PRs that touch the same files, leading to immediate merge conflicts the moment the first PR is approved.

To solve this, this pipeline instructs Devin to resolve issues sequentially in batches, **stacking** each new branch on top of the commits from the previous batch. 
- Branches are created incrementally (e.g., `feature` -> `CodeQL-Fix-Batch-1` -> `CodeQL-Fix-Batch-2`).
- As a reviewer, you get distinct, cleanly separated Draft PRs for each class of vulnerability (e.g., one PR for all SQLi, one PR for all XSS).
- Merging the final, top-level PR into `main` automatically closes all underlying stacked PRs without a single local Git conflict.

### 4. "Auto-Healing" Feedback Loop
If Devin's proposed fix is pushed to its draft PR and CodeQL still detects the vulnerability (or if Devin accidentally introduces a new one), the pipeline operates recursively. CodeQL will flag the remaining issue on Devin's PR, and the workflow will trigger a new Devin session to correct its own mistake, ensuring that only fully secure code is presented for final human review.

### 5. Enterprise-Grade Robustness
The GitHub Actions workflow (`.github/workflows/codeql.yml`) goes beyond a basic proof-of-concept by incorporating several defensive programming redundancies:
- **Comprehensive Triggers:** Runs defensively against new PRs, proactively on `push` merges, and regressively via a nightly `schedule` (cron) to catch zero-days against outdated dependencies.
- **API Quota Management:** Implements an optional `max_issues` cap per workflow run (defaulting to 30) ensuring prompt sizes stay within Devin's and LLM context limits. If there are 100 issues, the nightly cron will seamlessly chip away at the debt over consecutive nights.
- **Injection Protection:** Safely parses SARIF data and CodeQL alert payloads using Node.js `process.env` rather than risky string interpolation padding, preventing syntax failures if vulnerability messages contain strange characters.
- **Graceful Degradation:** Employs branch fallbacks and conditional logic to intelligently switch between "Pull Request Commentary" mode and silent "Nightly Cron" mode depending on the GitHub event trigger.

## How It Works (The Pipeline)
1. **Trigger:** Code is pushed, a PR is opened, or the nightly cron job fires.
2. **Analysis (`codeql-scan`):** GitHub CodeQL analyzes the Python codebase, generating `.sarif` artifacts.
3. **Parsing (`group-alerts`):** A custom Node script downloads the SARIF data, maps rules to specific CWE families, and groups them structurally.
4. **Live Context (`fetch-live-alerts`):** The workflow pulls live alert IDs from the GitHub API so Devin has direct links to the rich GitHub UI for additional context.
5. **Orchestration (`trigger-devin-fixes`):** The workflow compiles a dynamic, structured prompt containing the batched vulnerabilities and invokes the Devin API (`api.devin.ai`). 
6. **Reporting (`no-issues-comment` / PR Comment):** The workflow comments on the active PR with the session status, or formally approves the PR if CodeQL returns a clean bill of health.

## Usage
- **Manual Trigger:** You can trigger the remediation pipeline manually via the GitHub Actions UI by dispatching the `CodeQL Auto-Fix with Devin` workflow. You can optionally define the maximum number of issues Devin should attempt to fix in one run.
- **API Key Configuration:** The repository requires two secrets to run the orchestration: `DEVIN_SERVICE_USER_TOKEN` and `DEVIN_ORG_ID`.
