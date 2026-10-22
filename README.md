<div align="center">

# 🔐 DAT250 Secure Coding: Hands-on Demo Kit

**Twelve small, runnable demos that show how real vulnerabilities happen and how the tools that catch them work.**

[![Course](https://img.shields.io/badge/course-DAT250-0b5394)](#)
[![University](https://img.shields.io/badge/University%20of%20Stavanger-UiS-1f6feb)](https://www.uis.no)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OWASP Top 10](https://img.shields.io/badge/OWASP-Top%2010-000000?logo=owasp&logoColor=white)](https://owasp.org/Top10/)
[![CI](https://img.shields.io/badge/CI-fails%20on%20purpose-critical)](#12-automate-the-checks-cicd)

</div>

> [!CAUTION]
> **Everything in this repository is intentionally vulnerable.**
> Run it **only on your own machine**. The Flask app binds to `127.0.0.1` and must never be deployed or exposed to a network.
> All "secrets" are fake and generated at runtime. Use the techniques you see here **only** on systems you own or are explicitly authorised to test.

---

## 📑 Table of contents

- [About](#-about)
- [Learning objectives](#-learning-objectives)
- [Demo overview](#-demo-overview)
- [Repository structure](#-repository-structure)
- [Getting started](#-getting-started)
- [The demos](#-the-demos)
  - [1. Security unit tests](#1-security-unit-tests)
  - [2. Fuzzing a sanitizer](#2-fuzzing-a-sanitizer)
  - [3. Memory safety: one byte too many](#3-memory-safety-one-byte-too-many)
  - [4. Reviewing AI-generated code](#4-reviewing-ai-generated-code)
  - [5. Broken access control (IDOR)](#5-broken-access-control-idor)
  - [6. Stored XSS](#6-stored-xss)
  - [7. Static analysis: write your own SAST rule](#7-static-analysis-write-your-own-sast-rule)
  - [8. Dynamic testing (DAST)](#8-dynamic-testing-dast)
  - [9. The secret you deleted](#9-the-secret-you-deleted)
  - [10. Dependency confusion](#10-dependency-confusion)
  - [11. Vulnerable dependencies (SCA)](#11-vulnerable-dependencies-sca)
  - [12. Automate the checks (CI/CD)](#12-automate-the-checks-cicd)
- [Vulnerability reference](#-vulnerability-reference)
- [Suggested exercises](#-suggested-exercises)
- [Troubleshooting](#-troubleshooting)
- [Further reading](#-further-reading)
- [License and acknowledgements](#-license-and-acknowledgements)

---

## 📖 About

This kit accompanies the **Secure Coding** lecture in **DAT250 Information Security** at the University of Stavanger.
Each demo is self-contained, takes a few minutes, and follows the same pattern:

1. **Break it:** see the vulnerability with your own eyes.
2. **Detect it:** let a tool (tests, fuzzer, SAST, DAST, scanner) find it for you.
3. **Fix it:** apply the fix and watch the check turn green.

Demos are numbered in the order they appear in the lecture, but you can run them in any order.

## 🎯 Learning objectives

After working through the kit you should be able to:

- Write **security regression tests** that fail on vulnerable code and pass on fixed code.
- Use **property-based fuzzing** to find inputs a human would not think of.
- Explain why **memory-unsafe languages** allow silent corruption, and how sanitizers and Rust prevent it.
- Critically **review AI-generated code** for insecure patterns and hallucinated packages.
- Recognise and fix **IDOR, XSS, SQL injection, command injection** and **insecure deserialization**.
- Write a custom **Semgrep taint rule** and interpret **Bandit** findings.
- Run a **DAST** scan with Nuclei against a live application.
- Find **leaked secrets in Git history** with gitleaks.
- Explain **dependency confusion** and audit dependencies with **pip-audit**.
- Combine all of the above into a **CI pipeline** with GitHub Actions.

## 🗺️ Demo overview

| # | Demo | Folder | Category | Tools |
|:-:|------|--------|----------|-------|
| 1 | Security unit tests | [`vulnerable-app/tests`](vulnerable-app/tests) | Testing | pytest |
| 2 | Fuzzing a sanitizer | [`demo-fuzzing`](demo-fuzzing) | Testing | Hypothesis |
| 3 | One byte too many | [`demo-memory-safety`](demo-memory-safety) | Memory safety | C compiler + AddressSanitizer, Rust *(optional)* |
| 4 | Reviewing AI-generated code | [`demo-ai`](demo-ai) | Code review | Bandit, Semgrep, PyPI lookup |
| 5 | Reading someone else's grades (IDOR) | [`vulnerable-app`](vulnerable-app) | Access control | curl, pytest |
| 6 | Stored XSS in a profile bio | [`vulnerable-app`](vulnerable-app) | Injection | curl, browser, pytest |
| 7 | Write your own SAST rule | [`semgrep-rules`](semgrep-rules) | SAST | Semgrep, Bandit |
| 8 | Testing the running code | [`vulnerable-app`](vulnerable-app) | DAST | curl, Nuclei |
| 9 | The secret you deleted | [`demo-secrets`](demo-secrets) | Secrets | gitleaks |
| 10 | Dependency confusion | [`demo-dependency-confusion`](demo-dependency-confusion) | Supply chain | pip |
| 11 | Vulnerable dependencies | [`vulnerable-app`](vulnerable-app) | SCA | pip-audit |
| 12 | Automate the checks | [`.github/workflows`](.github/workflows) | DevSecOps | GitHub Actions |

## 📂 Repository structure

```text
dat250-secure-coding-demos/
├── vulnerable-app/              # Intentionally insecure Flask app (demos 1, 5–8, 11)
│   ├── app.py                   #   the vulnerable application
│   ├── seed_db.py               #   creates users.db with two students
│   ├── requirements.txt         #   deliberately outdated pins (demo 11 only)
│   ├── nuclei-report.sh         #   Nuclei scan → single HTML report
│   ├── tests/                   #   security regression tests
│   └── solutions/app_fixed.py   #   reference fix
├── demo-fuzzing/                # Path sanitizer + Hypothesis property tests
├── demo-memory-safety/          # C stack overflow, ASan build, Rust comparison
├── demo-ai/                     # Prompt, typical AI answer, package existence check
├── demo-secrets/                # Builds a throwaway repo with a "deleted" fake token
├── demo-dependency-confusion/   # Offline internal vs. "public" package index
├── semgrep-rules/dat250.yml     # Custom Semgrep rules (SQLi, CMDi, JWT, path traversal)
├── reports/                     # Example scan reports (PDF)
└── .github/workflows/           # CI pipeline that runs all checks on push
```

## 🚀 Getting started

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **OS** | macOS, Linux (Ubuntu / Kali). Windows users: use WSL2. |
| **Python** | 3.10 or newer |
| **Git** | Any recent version |
| **C compiler** | `cc` / `clang` / `gcc`. On macOS: `xcode-select --install` |
| **Rust** *(optional)* | Only for the Rust comparison in demo 3. Install with [rustup](https://rustup.rs). |
| **gitleaks**, **Nuclei** | Single binaries from their GitHub releases ([gitleaks](https://github.com/gitleaks/gitleaks/releases), [Nuclei](https://github.com/projectdiscovery/nuclei/releases)), or `brew install gitleaks nuclei` |

### Installation

```bash
git clone https://github.com/ocatak/dat250-secure-coding-demos.git
cd dat250-secure-coding-demos

python3 -m venv .venv
source .venv/bin/activate
pip install flask pyyaml argon2-cffi pytest hypothesis semgrep bandit pip-audit
```

> [!NOTE]
> Install a **current** Flask to *run* the app. The old versions pinned in `vulnerable-app/requirements.txt` exist only so that `pip-audit` has something to find in demo 11. **Do not** `pip install -r` that file.

<details>
<summary><b>Tested versions</b> (22 September 2026)</summary>

| Tool | Version |
|------|---------|
| Semgrep | 1.177 |
| Bandit | 1.9.4 |
| pip-audit | 2.10.1 |
| pytest | 8 |
| Hypothesis | 6 |
| gitleaks | 8.30.1 |
| Nuclei | 3.11.1 |

</details>

---

## 🧪 The demos

### 1. Security unit tests

Security requirements written as tests: they **fail** on the vulnerable app and **pass** on the fixed one.

```bash
cd vulnerable-app
python -m pytest -v tests                                              # 5 tests fail
TARGET=solutions.app_fixed SECRET_KEY=dev python -m pytest -v tests    # all pass
```

The tests cover SQL injection, command injection, IDOR and XSS. The `TARGET` environment variable switches which module is tested, so the **same** tests verify both versions.

**Takeaway:** once a vulnerability is fixed, a test makes sure it never comes back.

---

### 2. Fuzzing a sanitizer

```bash
cd demo-fuzzing
python -m pytest -q
```

[`sanitize.py`](demo-fuzzing/sanitize.py) contains a "path traversal filter" as it is often written: `name.replace("../", "")`.
[Hypothesis](https://hypothesis.readthedocs.io/) generates thousands of inputs and quickly finds one such as `....//`, which the filter turns **into** `../`.
The safer `safe_name()` passes the same property test.

**Takeaway:** state what must *always* be true and let the tool look for counterexamples.

---

### 3. Memory safety: one byte too many

```bash
cd demo-memory-safety
./run_demo.sh
```

| Step | What happens |
|------|--------------|
| `./overflow alice` | Normal input, `is_admin=0` |
| `./overflow AAAAAAAAB` | 9 characters into an 8-byte buffer. The extra `B` (ASCII 66) silently lands in `is_admin` → **admin access granted** |
| AddressSanitizer build | A longer input is caught immediately with a `stack-buffer-overflow` report |
| Rust version | The bounds-checked copy **panics** instead of corrupting memory |

> [!TIP]
> The script picks a working compiler automatically (`cc` → `clang` → `gcc`). Override it with `CC=gcc-14 ./run_demo.sh`.

**Takeaway:** in C a bug like this is silent. Sanitizers make it loud; memory-safe languages make it impossible.

---

### 4. Reviewing AI-generated code

Give [`prompt.txt`](demo-ai/prompt.txt) to any AI coding assistant, save the answer and scan it.
[`ai_generated.py`](demo-ai/ai_generated.py) is a representative answer if you want a fixed example.

```bash
cd demo-ai
bandit ai_generated.py
semgrep --config ../semgrep-rules/dat250.yml ai_generated.py
./check_packages.sh requirements-ai.txt     # needs internet access
```

Typical findings: path traversal in `send_file`, SQL injection through an f-string, a JWT decoded **without verifying the signature**, a hardcoded secret, and `debug=True`.
`check_packages.sh` also shows that one suggested package **does not exist on PyPI**: an attacker could register it ("slopsquatting").

**Takeaway:** AI-generated code is untrusted code. Review and scan it like any other contribution.

---

### 5. Broken access control (IDOR)

```bash
cd vulnerable-app
python seed_db.py            # alice / "correct horse", bob / "battery staple"
python app.py &

curl -c jar -d "username=alice&password=correct horse" http://127.0.0.1:5000/login
curl -b jar http://127.0.0.1:5000/grades/1     # alice's own grades ✅
curl -b jar http://127.0.0.1:5000/grades/2     # bob's grades: should be 403 ❌
```

The query is parameterized, so there is no SQL injection, yet any logged-in user can read anyone's grades. The route checks *that* you are logged in but never *who* you are.

**Fix:** compare `session["user_id"]` with `student_id` and return `403` on mismatch (see [`solutions/app_fixed.py`](vulnerable-app/solutions/app_fixed.py)).

---

### 6. Stored XSS

```bash
curl -b jar --data-urlencode "bio=<script>alert(document.cookie)</script>" http://127.0.0.1:5000/bio
curl http://127.0.0.1:5000/profile/1           # the script comes back unescaped
```

Open <http://127.0.0.1:5000/profile/1> in a browser to see it execute. The template uses `{{ bio|safe }}`, which switches off Jinja2's autoescaping.

**Fix:** remove `|safe`, and add a `Content-Security-Policy` header as defence in depth.

---

### 7. Static analysis: write your own SAST rule

```bash
bandit -r vulnerable-app -ll -x vulnerable-app/tests,vulnerable-app/solutions
semgrep --config semgrep-rules/dat250.yml vulnerable-app/app.py
```

[`semgrep-rules/dat250.yml`](semgrep-rules/dat250.yml) contains four custom rules, three of them **taint-mode** rules that track user input from `flask.request` to a dangerous sink:

| Rule | Detects | CWE |
|------|---------|-----|
| `flask-sqli-fstring` | Request data in a string-built SQL query | CWE-89 |
| `flask-cmdi-shell-true` | Request data in `subprocess(..., shell=True)` | CWE-78 |
| `jwt-signature-not-verified` | `jwt.decode(..., verify_signature=False)` | CWE-347 |
| `flask-path-traversal-send-file` | Request data in `send_file()` | CWE-22 |

**Exercise:** rewrite the login query with a `?` placeholder and re-run Semgrep. The finding disappears.

---

### 8. Dynamic testing (DAST)

```bash
cd vulnerable-app
python app.py &                                                # localhost only
curl "http://127.0.0.1:5000/ping?host=127.0.0.1;id"            # command injection by hand
nuclei -u http://127.0.0.1:5000 -tags werkzeug,headers         # debug console + missing headers
```

For a shareable, self-contained HTML report:

```bash
./nuclei-report.sh                       # writes report.html
```

**Takeaway:** SAST reads the code; DAST attacks the running system. Each finds things the other misses (for example, missing security headers or an exposed debugger).

---

### 9. The secret you deleted

```bash
cd demo-secrets
./setup.sh                 # creates leaky-repo/ with a FAKE GitHub token
cd leaky-repo
gitleaks dir .             # current files: no leaks
gitleaks git -v .          # history: the "deleted" token is still there
```

**Takeaway:** deleting a secret in a new commit does **not** remove it from history. A leaked secret must be **revoked and rotated**; rewriting history is only cleanup.

---

### 10. Dependency confusion

```bash
cd demo-dependency-confusion
./run_demo.sh
```

The demo is **fully offline**. Two local folders play the role of a company's internal index (`uis-internal-utils 1.2.0`) and a public index controlled by an attacker (`uis-internal-utils 99.0.0`). When both are configured, pip picks the **highest version from either source**, so the attacker's package wins until the version is pinned.

**Fix:** pin exact versions, preferably with `--require-hashes`, or use a single proxying index that you control.

---

### 11. Vulnerable dependencies (SCA)

```bash
pip-audit -r vulnerable-app/requirements.txt
```

The requirements file pins old versions of Flask, Jinja2, PyYAML, requests and urllib3 with known CVEs.

> [!NOTE]
> The raw count includes duplicate rows. Look at the unique vulnerability IDs and the **Fix Versions** column.

---

### 12. Automate the checks (CI/CD)

[`.github/workflows/secure-coding.yml`](.github/workflows/secure-coding.yml) runs the checks from this kit on every push and pull request:

| Step | Demo |
|------|:----:|
| Secret scanning (gitleaks, full history) | 9 |
| SAST (Semgrep custom rules + Bandit) | 7 |
| Security unit tests + fuzzing | 1, 2 |
| Dependency audit (pip-audit) | 11 |

> [!IMPORTANT]
> The pipeline **fails on purpose**: the code is vulnerable. Your task is to fork the repository and fix the code until the pipeline is green ✅.

---

## 📚 Vulnerability reference

| Vulnerability | Where | CWE | OWASP Top 10 (2021) |
|---------------|-------|-----|---------------------|
| SQL injection | `app.py` `/login`, `ai_generated.py` | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | A03 Injection |
| OS command injection | `app.py` `/ping` | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | A03 Injection |
| Stored XSS | `app.py` `/profile` | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | A03 Injection |
| IDOR | `app.py` `/grades` | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) | A01 Broken Access Control |
| Path traversal | `ai_generated.py`, `sanitize.py` | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) | A01 Broken Access Control |
| Weak password hash (MD5) | `app.py` | [CWE-916](https://cwe.mitre.org/data/definitions/916.html) | A02 Cryptographic Failures |
| Hardcoded secret | `app.py`, `ai_generated.py` | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | A07 Identification & Auth Failures |
| JWT signature not verified | `ai_generated.py` | [CWE-347](https://cwe.mitre.org/data/definitions/347.html) | A02 Cryptographic Failures |
| Unsafe YAML / pickle | `app.py` `/import`, `/restore` | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) | A08 Software & Data Integrity Failures |
| Debug mode enabled | `app.py` | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) | A05 Security Misconfiguration |
| Missing security headers | `app.py` | [CWE-693](https://cwe.mitre.org/data/definitions/693.html) | A05 Security Misconfiguration |
| Stack buffer overflow | `overflow.c` | [CWE-121](https://cwe.mitre.org/data/definitions/121.html) | n/a (memory safety) |
| Secret in Git history | `demo-secrets` | [CWE-540](https://cwe.mitre.org/data/definitions/540.html) | A07 Identification & Auth Failures |
| Vulnerable / confused dependencies | `requirements.txt`, `demo-dependency-confusion` | [CWE-1104](https://cwe.mitre.org/data/definitions/1104.html), [CWE-427](https://cwe.mitre.org/data/definitions/427.html) | A06 Vulnerable & Outdated Components |

## ✍️ Suggested exercises

1. **Fix the app yourself.** Make all tests in `vulnerable-app/tests` pass *without* looking at `solutions/`.
2. **Close the gaps.** `/import` (unsafe YAML) and `/restore` (pickle) have no tests yet. Write failing tests first, then fix them.
3. **Extend the ruleset.** Add a Semgrep rule that flags `yaml.load` without `SafeLoader`, or `app.run(debug=True)`.
4. **Harden the passwords.** Replace MD5 with Argon2 (`argon2-cffi` is already installed).
5. **Go green.** Fork the repository and fix code until the GitHub Actions pipeline passes.
6. **Bring your own AI.** Run `prompt.txt` through a different assistant and compare its findings with `ai_generated.py`.

## 🛠️ Troubleshooting

<details>
<summary><b>macOS: <code>fatal error: _stdio.h: No such file or directory</code></b></summary>

A Homebrew `gcc` whose headers are out of date after an Xcode update. `run_demo.sh` prefers Apple `clang`; make sure the Command Line Tools are installed with `xcode-select --install`, or set `CC=clang`.
</details>

<details>
<summary><b><code>Address already in use</code> on port 5000</b></summary>

On macOS, AirPlay Receiver uses port 5000. Disable it in *System Settings → General → AirDrop & Handoff*, or stop the previous app instance with `kill %1` / `pkill -f app.py`.
</details>

<details>
<summary><b><code>sqlite3.OperationalError: no such table: users</code></b></summary>

Run `python seed_db.py` inside `vulnerable-app/` before starting the app.
</details>

<details>
<summary><b>The app crashes on start with an old Flask</b></summary>

You installed `vulnerable-app/requirements.txt`. Reinstall a current Flask: `pip install -U flask jinja2`.
</details>

<details>
<summary><b><code>Permission denied</code> when running a <code>.sh</code> script</b></summary>

Make it executable with `chmod +x <script>.sh`, or run it with `bash <script>.sh`.
</details>

## 🔗 Further reading

- [OWASP Top 10](https://owasp.org/Top10/) · [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
- [Semgrep: writing rules](https://semgrep.dev/docs/writing-rules/overview) · [Bandit documentation](https://bandit.readthedocs.io/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Alex Birsan: Dependency Confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)
- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

## 📄 License and acknowledgements

Created by **F. Özgür Catak** for **DAT250 Information Security**, University of Stavanger.

This material is provided **for educational purposes only**. The code is intentionally insecure and is provided "as is", without warranty of any kind. The authors are not responsible for any misuse.

<div align="center">

*Found a bug in a demo (not the intentional kind)? Open an issue.* 🐛

</div>
