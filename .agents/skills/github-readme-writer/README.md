# README.skills

`README.skills` is a Codex skill for writing and improving GitHub project READMEs.

It helps an AI agent inspect a repository first, choose the right README shape, write accurate install and quickstart sections, and avoid unsupported claims.

## Install

```bash
npx skills add LaokeQwQ/README.skills
```

Restart Codex after installation so the new skill is loaded.

## Usage

Ask Codex to use the skill in a repository:

```text
Use $github-readme-writer to improve this repository's README.md.
```

Other useful prompts:

```text
Use $github-readme-writer to audit this README for missing setup details and unsupported claims.
```

```text
Use $github-readme-writer to write a README for this CLI project.
```

```text
Use $github-readme-writer to turn this existing README into a clearer GitHub open-source README without inventing facts.
```

## What It Does

- Inspects the repository before writing.
- Selects a README structure based on project type.
- Produces practical install, quickstart, usage, docs, and contribution sections.
- Preserves accurate existing content during rewrites.
- Avoids invented badges, benchmarks, screenshots, commands, or support claims.
- Includes distilled README patterns from mature open-source projects.

## Structure

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- references/
    `-- readme-patterns.md
```

## Reference Projects

The skill distills README patterns from Excalidraw, Supabase, Mermaid, RAGFlow, Hermes Agent, TensorFlow, Oh My Zsh, Hugging Face Transformers, Bootstrap, and React.

## License

MIT
