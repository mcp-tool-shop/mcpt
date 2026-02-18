# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-02-18

### Added
- HANDBOOK.md -- deep-dive guide covering architecture, workspace model, trust & safety, visual language, command reference, CI patterns, and FAQ

### Changed
- README.md -- rewritten with "At a Glance" section, ecosystem links, docs table, standardized badge row
- npm/README.md -- rewritten for npm page with quick start and requirements

## [1.0.0] - 2026-02-15

- **Official Release**: Synchronized with mcp-tool-registry v1.0.0.
- **Contract**: Full support for Registry v1.x artifacts (search, bundles, curation).
- **Hardened**: Production-grade isolation, deterministic installation, and hermetic testing.

## [0.2.3] - 2026-02-15

### Added
- **Featured & Collections**: New curation views in `mcpt list` and `mcpt search` via `--featured` and `--collection` flags.
- **Improved Tool Discovery**: `mcpt list --featured` now displays curated collections with specialized rendering.
- **Install Hints**: `mcpt info` now explicitly displays the canonical installation command for tools.
- **Hermetic Testing**: Introduced fully isolated test suite for curation features using local fixtures.

### Changed
- **UX Polish**: Collection slugs in featured view are now styled for easy copying (dimmed).
- **Deprecated Tools**: Deprecated tools in curated lists are now visually separated and dimmed.
- **Path Contracts**: Enforced strict usage of `featured.json` artifact path for registry consistency.

## [0.2.0] - 2026-02-15

### Visual Identity & Safety Language
- **Trust Tiers**: Added trusted, verified, neutral, and experimental tiers with visual indicators (Gold, Green, Purple).
- **Risk Aura**: Implemented visual risk markers (e.g., `⬢▲` for High Risk) and tinting for untrusted tools.
- **Semantic Badges**: New capability badges (e.g. `NET`, `EXEC!`) with semantic coloring (Orange, Red).
- **Icons Legend**: Added `mcpt icons` command to show the visual language cheat sheet.
- **Accessibility**: Added `--plain`, `NO_COLOR` support, and ASCII sigil modes (`ui.sigil: ascii`).
- **Performance**: Optimized rendering with caching for large registries.

### Changed
- CLI output now defaults to rich formatting unless piped (or forced with `--force-rich`).
- Sigils are now deterministic and cache-optimized.
