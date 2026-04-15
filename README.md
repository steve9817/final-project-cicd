# 🔴 Intentionally Vulnerable Python App — Trivy Testing

> **⚠️ WARNING:** This project is **intentionally insecure**.  
> It exists solely for **security tooling practice** (Trivy, SAST, etc.).  
> **Never deploy this in any real environment.**

---

## 📦 Project Structure

```
vuln-demo/
├── app/
│   └── main.py            # Flask app with OWASP Top-10 vulnerabilities
├── requirements.txt       # Pinned to old, vulnerable package versions
├── Dockerfile             # Lightweight image (python:3.9-slim) with misconfigs
├── docker-compose.yml     # Compose file with security misconfigurations
├── trivy-scan.sh          # All-in-one Trivy scanning script
└── README.md
```

---

## 🐳 Base Image

| Image | Approx. size | Why chosen |
|---|---|---|
| `python:3.9-slim` | ~45 MB | Lightweight Debian slim; ships enough OS packages to surface CVEs without the bulk of the full image |

The slim variant is **much smaller** than `python:3.9` (~900 MB) while still carrying Debian system libraries that Trivy can scan.

---

## 🐛 Intentional Vulnerabilities

### Application Code (`app/main.py`)

| Endpoint | Vulnerability | CWE |
|---|---|---|
| `/user?username=` | SQL Injection | CWE-89 |
| `/ping?host=` | Command Injection (RCE) | CWE-78 |
| `POST /load` | Insecure Deserialization (pickle) | CWE-502 |
| `POST /parse-yaml` | YAML arbitrary code exec | CWE-502 |
| `/read-file?file=` | Path Traversal | CWE-22 |
| `/greet?name=` | XSS / SSTI via render_template_string | CWE-79 |
| `/debug` | Sensitive data exposure (env vars, secrets) | CWE-200 |
| Hardcoded creds | Hardcoded secrets in source | CWE-798 |

### Python Packages (`requirements.txt`)

| Package | Version | Key CVEs |
|---|---|---|
| Flask | 0.12.2 | CVE-2018-1000656 (DoS) |
| Werkzeug | 0.14.1 | CVE-2019-14806 (debug PIN leak) |
| Jinja2 | 2.10 | CVE-2019-10906 (sandbox escape) |
| PyYAML | 5.3.1 | CVE-2020-14343 (arbitrary exec) |
| requests | 2.18.4 | CVE-2018-18074 (credential leak) |
| cryptography | 2.3 | CVE-2018-10903 (padding oracle) |
| Pillow | 6.2.0 | CVE-2020-5312 (buffer overflow) |
| urllib3 | 1.24.1 | CVE-2019-11324 (cert bypass) |
| paramiko | 2.4.1 | CVE-2018-7750 (auth bypass) |

### Dockerfile Misconfigurations

| Misconfiguration | Severity |
|---|---|
| Running as `root` (no `USER` instruction) | HIGH |
| `FLASK_DEBUG=1` in ENV | HIGH |
| Hardcoded AWS keys in `ENV` | CRITICAL |
| No `HEALTHCHECK` instruction | LOW |
| No `--no-install-recommends` for some apt pkgs | MEDIUM |

### docker-compose.yml Misconfigurations

| Misconfiguration | Severity |
|---|---|
| `privileged: true` | CRITICAL |
| `cap_add: NET_ADMIN, SYS_PTRACE` | HIGH |
| Hardcoded secrets in `environment:` | HIGH |
| Redis exposed without auth | HIGH |
| No resource limits | MEDIUM |
| Mounting host `/tmp` | MEDIUM |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Trivy
brew install aquasecurity/trivy/trivy        # macOS
# or
sudo apt install trivy                        # Debian/Ubuntu
# or
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
```

### Build & Scan

```bash
# 1. Clone / enter the project
cd vuln-demo

# 2. Run everything at once
chmod +x trivy-scan.sh
./trivy-scan.sh

# ── OR run individual scans ───────────────────────────────────────────────

# Build image
docker compose build

# Scan image for OS + pip CVEs
trivy image vuln-python-app:latest --severity HIGH,CRITICAL

# Scan source files + requirements.txt
trivy fs . --severity HIGH,CRITICAL --scanners vuln,secret,misconfig

# Scan IaC files (Dockerfile, docker-compose.yml)
trivy config . --severity HIGH,CRITICAL

# Scan for hardcoded secrets only
trivy fs . --scanners secret
```

### Run the App (for dynamic testing)

```bash
docker compose up
# App available at http://localhost:5000
```

---

## 📊 Expected Trivy Output (summary)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VULNERABILITY SUMMARY                           │
├──────────────┬──────────┬──────────┬──────────┬──────────┬─────────────┤
│    Target    │ CRITICAL │   HIGH   │  MEDIUM  │   LOW    │   UNKNOWN   │
├──────────────┼──────────┼──────────┼──────────┼──────────┼─────────────┤
│ OS packages  │    5+    │   15+    │   20+    │   10+    │      0      │
│ pip packages │    3+    │   10+    │    5+    │    2+    │      0      │
│ Misconfigs   │    2+    │    5+    │    3+    │    1+    │      0      │
│ Secrets      │    5+    │    0     │    0     │    0     │      0      │
└──────────────┴──────────┴──────────┴──────────┴──────────┴─────────────┘
```

---

## 🧹 Cleanup

```bash
docker compose down
docker rmi vuln-python-app:latest
rm -rf trivy-reports/
```
