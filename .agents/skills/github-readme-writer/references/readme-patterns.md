# README Patterns

Use this reference after inspecting the target repository. Do not copy a pattern mechanically; choose the smallest structure that helps the project's real readers.

## Reference Projects Studied

- Excalidraw: visual-first product README with immediate identity, links, and contribution paths.
- Supabase: broad platform README that routes readers to docs, local development, architecture, and community.
- Mermaid: docs-oriented library/tooling README with clear examples and ecosystem links.
- RAGFlow: self-hosted AI system README with screenshots, setup, configuration, and deployment detail.
- Hermes Agent: AI agent README with positioning, install, examples, and model/tooling context.
- TensorFlow: mature framework README that stays concise and delegates to official documentation.
- Oh My Zsh: community-heavy CLI project README with installation, usage, plugins/themes, and contribution paths.
- Transformers: library README with installation, quick examples, model ecosystem, docs, and community links.
- Bootstrap: framework README with install paths, docs, status, and contribution information.
- React: concise docs-gateway README focused on official docs and contribution links.

## Top-Fold Pattern

Strong GitHub READMEs usually answer these within the first screen:

- What is this?
- Why should this reader care?
- What is the first useful action?
- Where are the docs, demo, or install path?

Useful top-fold elements:

- Project name as the first heading.
- One sentence that names the category and core value.
- Badges only for real status signals.
- Primary links: docs, demo, examples, install, contributing.
- Screenshot or GIF when visual behavior matters.

Avoid:

- Long origin stories before the reader knows what the project does.
- Badge walls with weak signal.
- Generic claims such as "powerful", "modern", "easy", or "next-generation" without concrete proof.

## Project-Type Shapes

### Library or Framework

Recommended sections:

1. Overview
2. Installation
3. Quickstart code
4. Core concepts or examples
5. Documentation
6. Compatibility or supported environments
7. Contributing and license

Rules:

- Show the smallest working example early.
- Prefer official package-manager commands from manifests.
- Include API docs links rather than embedding large API references.
- Mention version compatibility only when repo evidence supports it.

### CLI or Developer Tool

Recommended sections:

1. Overview
2. Install
3. Quickstart command
4. Common commands
5. Configuration
6. Shell integration or plugins when relevant
7. Troubleshooting

Rules:

- Make commands copy-pasteable.
- Show expected output only when it is stable.
- Separate global install, local install, and source build paths.

### App, Product, or Visual Tool

Recommended sections:

1. Overview with screenshot or demo
2. Features
3. Run locally
4. Configuration
5. Architecture or package layout
6. Contributing

Rules:

- Use actual screenshots or demo links from the repo.
- Explain local development separately from production deployment.
- Avoid product marketing claims that the repo cannot substantiate.

### Self-Hosted Service

Recommended sections:

1. Overview and screenshots
2. Requirements
3. Quickstart, often Docker-first if supported
4. Configuration
5. Data persistence and upgrades
6. Deployment notes
7. Troubleshooting
8. Security and contribution links

Rules:

- Name required external services.
- Show where data lives if persistence matters.
- Include default ports, env files, and health checks only when found in the repo.

### AI, Model, or Agent Project

Recommended sections:

1. Overview and intended use
2. Install
3. Quickstart
4. Examples
5. Models, tools, or integrations
6. Evaluation, limitations, or safety notes when present
7. Citation, license, and community

Rules:

- Do not invent benchmark results or model capabilities.
- Separate local inference, API usage, and training/fine-tuning paths.
- Mention hardware or dependency requirements only when evidenced.

### Monorepo

Recommended sections:

1. Overview
2. Packages/apps table
3. Development setup
4. Common tasks
5. Documentation
6. Contributing

Rules:

- Include a compact package table when it helps navigation.
- Explain workspace commands from the actual tooling.
- Do not document every package in the root README if package-level READMEs exist.

## Section Catalog

Use only sections that the repo can support.

- `Overview`: name the category and value.
- `Features`: use concrete capabilities, not adjectives.
- `Demo`: link or embed only real assets.
- `Installation`: package manager or binary install.
- `Quickstart`: shortest path to a useful result.
- `Usage`: common workflows and examples.
- `Configuration`: env vars, config files, flags.
- `Architecture`: high-level components and package layout.
- `Deployment`: production or self-hosting steps.
- `Troubleshooting`: common failures known from docs/issues/config.
- `Documentation`: route to docs site or repo docs.
- `Contributing`: link to contribution docs or summarize basic local workflow.
- `Security`: link to security policy or reporting path.
- `License`: match the repo license file.

## Rewrite Rules

- Keep working commands and accurate links.
- Move detailed docs out of the README when a docs site already owns them.
- Collapse duplicate installation paths.
- Replace vague feature bullets with evidence-backed capabilities.
- Convert long prose setup instructions into ordered steps.
- Use tables for package lists, supported integrations, and command summaries.
- Prefer relative links for repo files.

## Audit Checklist

Ask these questions before finalizing:

- Can a new reader describe the project after the first screen?
- Can a new user run one successful command or example?
- Are prerequisites stated before commands that require them?
- Are all links real and useful?
- Are badges meaningful and current?
- Are screenshots or demos real project assets?
- Is any claim unsupported by code, docs, tests, releases, or assets?
- Does the README duplicate docs that are likely to go stale?
- Does it include contribution, security, and license paths when available?
