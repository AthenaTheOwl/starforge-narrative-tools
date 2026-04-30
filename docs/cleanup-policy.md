# Cleanup policy

Keep:

- `prose/act1/`
- Act 1-safe public specs in `spec/`
- `tools/`
- tests and docs

Do not commit:

- unreleased later-act prose or specs
- Python bytecode
- local caches
- engine SDKs
- generated game exports
- save files
- logs and traceback files

This repo should stay useful as a public Act 1 source and tooling mirror, not a
dump of the active workshop. The private workshop can continue to hold later
acts until they are published.
