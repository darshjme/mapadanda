# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability, **do not open a public GitHub issue**.

Please email the maintainers directly at: security@example.com

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and aim to release a fix within 14 days.

## Scope

`agent-benchmark` is a pure stdlib timing library with no network access, no file I/O,
and no execution of untrusted code. The attack surface is minimal. Security issues are
most likely to arise if the library is used to benchmark untrusted callables — this is
the caller's responsibility to sandbox appropriately.
