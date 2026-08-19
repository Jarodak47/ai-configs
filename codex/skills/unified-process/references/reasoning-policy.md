# Reasoning-effort policy

- **Rapide:** use low effort for small, reversible tasks after immediate verification.
- **Standard:** use medium effort by default; increase to high for ambiguous debugging, architecture, or security work.
- **Rigoureux:** use high effort for makers and independent gates. Reserve xhigh for high-impact architecture/security decisions or repeated ambiguous failures.
- Keep deterministic scripts independent of reasoning effort.
- When effort cannot vary per task, use medium globally and request high-effort independent reviewers when delegation is authorized.
- Record model and effort with calibration results. Never compare baselines produced with unknown configurations.

