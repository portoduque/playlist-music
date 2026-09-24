---
name: github-readme-writer
description: Use when creating, rewriting, auditing, or improving README.md files for GitHub repositories, especially open-source projects, libraries, CLIs, frameworks, apps, AI tools, documentation sites, or self-hosted services. Guides Codex to inspect the repository first, choose an appropriate README structure, write accurate install, quickstart, docs, community, and contribution sections, avoid hallucinated claims, and preserve project-specific tone and constraints.
---

# GitHub README Writer

Use this skill to create, rewrite, or review a GitHub project README. Treat the README as the project's front door: it should help a first-time evaluator understand the project, a new user try it, and a contributor find the next place to go.

## Workflow

1. Inspect the repository before writing.
   - Read any existing `README.md`, `docs/`, examples, package manifests, lockfiles, CLI entrypoints, Docker files, CI files, license, contributing guide, security policy, screenshots, demos, and release/config files.
   - Identify the project type: library/framework, CLI/tooling, app/service, AI/model project, documentation site, self-hosted system, template, or monorepo.
   - Identify the likely primary reader: evaluator, user, deployer, contributor, or integrator.

2. Choose the README shape.
   - Use a short docs-gateway README when the project already has strong external docs and the README's job is orientation.
   - Use a fuller homepage README when setup, self-hosting, examples, visual proof, or community onboarding must happen in the repository.
   - Read `references/readme-patterns.md` when you need structure options, project-type patterns, or an audit checklist.

3. Draft from evidence only.
   - Do not invent badges, install commands, screenshots, diagrams, benchmarks, supported platforms, model capabilities, roadmap items, sponsors, or community links.
   - If the repo lacks evidence for a common section, omit it or mark the missing fact as a question to the user instead of guessing.
   - Preserve accurate existing content when rewriting; improve organization, scanability, and correctness rather than replacing everything for style.

4. Make the first screen useful.
   - Put the project name, one-line value proposition, and primary links or actions near the top.
   - Include badges only when their target URLs are real and useful.
   - Include a screenshot, GIF, or demo link when the repository already provides one and the project benefits from visual proof.

5. Make the getting-started path executable.
   - Separate prerequisites from installation when setup is nontrivial.
   - Prefer one minimal quickstart path over several competing paths.
   - Use fenced code blocks for commands and include the working directory or environment assumptions when needed.
   - Keep examples small enough to copy, but complete enough to run.

6. Close with maintenance paths.
   - Link to documentation, examples, contribution guide, security policy, license, and community channels when they exist.
   - For monorepos, explain where packages/apps live and where contributors should start.
   - For self-hosted systems, include configuration, upgrade, data persistence, and troubleshooting pointers only when supported by repo evidence.

## Section Order

Use this default order, then trim or reorder based on project type:

1. Title, concise description, badges, and primary links
2. Screenshot, demo, or preview when useful and available
3. Why this project exists or what it solves
4. Features or capabilities
5. Installation
6. Quickstart
7. Usage examples
8. Configuration or deployment
9. Architecture or packages
10. Documentation links
11. Contributing, security, community, and license

## Quality Bar

- Accurate beats impressive.
- Specific beats generic.
- A short README with strong links beats a long README that duplicates stale docs.
- Commands must be copy-pasteable.
- Claims must be grounded in code, docs, tests, releases, or project assets.
- The README should not read like marketing copy unless the repo is actually a product landing surface.

## Final Check

Before finishing, verify:

- The top section answers what the project is, who it is for, and what to do first.
- Install and quickstart commands match the detected tooling.
- Links are relative when pointing inside the repo and absolute only for external destinations.
- Section headings are scannable and not over-nested.
- The README does not include unsupported claims or placeholder text.
- License, contribution, and security information matches files present in the repository.
