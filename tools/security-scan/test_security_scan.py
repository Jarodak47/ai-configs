#!/usr/bin/env python3
"""test_security_scan.py — Tests unitaires de security_scan.py (partie déterministe).

Couvre le parsing des sorties de scanners de dépendances (pip-audit, npm audit,
composer audit) et la détection de secrets — sans nécessiter de vrai projet ni
réseau. Complète le smoke test d'intégration.

Usage:
    python3 test_security_scan.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from security_scan import parse_dep_output, scan_secrets, is_env_committed
from pathlib import Path as _P
import tempfile

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ✓ {name}")
    else:
        FAILURES.append(name)
        print(f"  ✗ {name} — {detail}")


print("parse_dep_output — pip-audit (table)")
PIP_AUDIT = """\
Found 2 known vulnerabilities in 2 packages
Name       Version   ID                  Fix Versions
django     3.2.0     PYSEC-2022-4        3.2.14
requests   2.25.0    PYSEC-2023-71       2.28.0
"""
# la sortie table ne contient pas de mot-clé de sévérité -> aucun finding
out = parse_dep_output(PIP_AUDIT, "pip-audit")
check("table sans sévérité -> 0 finding", len(out) == 0, f"got {len(out)}")

PIP_AUDIT_SEV = """\
Found 1 known vulnerability in 1 package
Name       Version   Severity
flask      2.0.0     HIGH
"""
out = parse_dep_output(PIP_AUDIT_SEV, "pip-audit")
check("HIGH -> sévérité 3 (bloquant)", len(out) == 1 and out[0]["severity"] == 3,
      f"got {out}")

print("parse_dep_output — npm audit (résumé + entrées)")
NPM = """\
found 2 vulnerabilities (1 low, 1 moderate)
# npm audit report

lodash <=4.17.20
Severity: high
Prototype Pollution
```
"""
out = parse_dep_output(NPM, "npm audit")
sev_scores = sorted(f["severity"] for f in out)
check("résumé 'found 2 vulnerabilities' ignoré", len(out) == 1, f"got {out}")
check("npm 'Severity: high' -> sévérité 3", sev_scores == [3], f"got {sev_scores}")

print("parse_dep_output — composer audit")
COMPOSER = """\
No known vulnerabilities found
"""
out = parse_dep_output(COMPOSER, "composer audit")
check("composer propre -> 0 finding", len(out) == 0, f"got {len(out)}")

print("parse_dep_output — cas vides / JSON")
out = parse_dep_output("", "x")
check("sortie vide -> 0 finding", len(out) == 0)
out = parse_dep_output('{"dependencies": []}', "x")
check("JSON sans sévérité -> 0 finding", len(out) == 0, f"got {len(out)}")

print("scan_secrets — patterns")
with tempfile.TemporaryDirectory() as td:
    root = _P(td)
    (root / "aws.py").write_text('key = "AKIAIOSFODNN7EXAMPLE"\n')
    (root / "stripe.py").write_text('sk = "sk_test_FAKE_KEY_FOR_TESTING_ONLY"\n')
    (root / "gh.py").write_text('tok = "ghp_123456789012345678901234567890123456"\n')
    (root / "medium.py").write_text('api_secret = "abcdefghijklmnopqrstuvwxyz1234"\n')
    (root / "privkey.pem").write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIB\n")
    (root / "clean.py").write_text('x = "salut"\n')

    files = [root / f for f in
             ("aws.py", "stripe.py", "gh.py", "medium.py", "privkey.pem", "clean.py")]
    findings = scan_secrets(files, root)
    labels = {f["label"] for f in findings}
    check("clé AWS détectée", "AWS access key" in labels, str(labels))
    check("clé Stripe détectée", "Stripe secret key" in labels, str(labels))
    check("GitHub PAT détecté", "GitHub PAT" in labels, str(labels))
    check("secret générique -> sévérité 2 (moyen)",
          any(f["severity"] == 2 for f in findings), str(findings))
    check("clé privée détectée", any("Clé privée" in f["label"] for f in findings), str(labels))
    check("fichier propre sans finding",
          not any(f["file"].endswith("clean.py") for f in findings), str(findings))

print("is_env_committed")
check(".env -> oui", is_env_committed(_P("proj/.env"), _P("proj")))
check(".env.local -> oui", is_env_committed(_P("proj/.env.local"), _P("proj")))
check(".env.example -> non", not is_env_committed(_P("proj/.env.example"), _P("proj")))

print()
if FAILURES:
    print(f"FAIL — {len(FAILURES)} test(s) échoué(s) : {FAILURES}")
    sys.exit(1)
print("PASS — tous les tests unitaires de security_scan.py passent")
