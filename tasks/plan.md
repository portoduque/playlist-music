# Implementation Plan: Playlist Music MVP

## Overview

Implementar o MVP em 15 tarefas atômicas. Cada tarefa altera no máximo cinco arquivos, possui testes focados e deixa uma unidade verificável. Downloads reais não fazem parte da suíte automática; a integração externa será testada por processos simulados e por um smoke test manual autorizado.

## Architecture Decisions

- **Desktop local:** Tkinter, sem servidor, conta, banco de dados ou navegador embutido.
- **Um modelo de entrada:** todos os importadores produzem `TrackRequest`; os módulos seguintes desconhecem o formato original.
- **Execução sequencial:** uma faixa por vez para tornar progresso, falhas e arquivos parciais previsíveis.
- **Processos seguros:** executar `yt-dlp` como módulo do Python atual e FFmpeg por argumentos separados, nunca com `shell=True`.
- **Saída confinada:** todo caminho é resolvido e validado dentro da pasta da playlist antes de qualquer escrita.
- **Metadados opcionais:** ausência de tag ou capa não invalida um MP3 concluído.
- **UI desacoplada:** a thread de trabalho publica eventos; somente a thread principal altera widgets Tkinter.
- **Sem abstrações antecipadas:** funções e dataclasses simples; nenhum sistema de plugins no MVP.

## Dependency Graph

```text
Task 1 foundation
  └─ Task 2 model + pasted text
       ├─ Task 3 TXT + CSV
       └─ Task 4 M3U/M3U8 + JSON
            └─ Task 5 safe paths + deduplication
                 └─ Task 6 preflight + command construction
                      └─ Task 7 single-track runner
                           └─ Task 8 resilient queue
                                ├─ Task 9 metadata + cover
                                └─ Task 10 playlists + report
                                     └─ Task 11 end-to-end service
                                          └─ Task 12 UI input flow
                                               └─ Task 13 background progress
                                                    └─ Task 14 completion flow
                                                         └─ Task 15 docs + final verification
```

## Test Strategy

### Automated layers

| Layer | Purpose | Network |
|---|---|---|
| Unit | Parsers, validation, names, deduplication, commands and reports | Never |
| Integration | Temporary folders, fake downloader, metadata fixtures and complete service | Never |
| UI/controller | State transitions and event handling with fake services | Never |
| Manual smoke | One authorized source, real yt-dlp/FFmpeg and one player | Only when explicitly run |

### Required edge cases

- Empty input, blank lines, comments, UTF-8 BOM, Unicode and malformed files.
- CSV quoted fields, alternate column order, missing headers and invalid rows.
- M3U comments, relative paths and URLs; JSON wrong type, missing fields and mixed valid/invalid items.
- Windows reserved names, forbidden characters, trailing dots/spaces, collisions and path traversal.
- Missing yt-dlp/FFmpeg, non-zero exit, timeout, partial file and unexpected output.
- Missing metadata/cover, invalid image and tag-write failure without losing valid audio.
- One failed item between successful items, duplicate items and empty successful result.
- UI progress, completion, recoverable errors and prevention of a second concurrent run.

## Phases and Checkpoints

### Phase 1: Foundation and input

- Tasks 1–4 establish the executable package and every supported input format.
- **Checkpoint A:** full import matrix passes and normalized ordering is reviewed.

### Phase 2: Safe output and acquisition

- Tasks 5–8 establish path safety, external-tool preflight, one-track execution and queue resilience.
- **Checkpoint B:** subprocess tests pass without network; no write can escape the selected directory.

### Phase 3: Portable library

- Tasks 9–11 add tags, playlists, reports and the complete headless workflow.
- **Checkpoint C:** an integration test creates and moves a complete temporary playlist.

### Phase 4: User experience

- Tasks 12–14 implement the smallest usable Tkinter flow.
- **Checkpoint D:** manual flow works with fake services and UI stays responsive.

### Phase 5: Release readiness

- Task 15 documents and verifies the MVP.
- **Checkpoint E:** full test suite, Ruff, manual authorized smoke test and human review.

## Definition of Done per Task

Uma tarefa só pode ser marcada como concluída quando:

- critérios de aceitação e testes focados passam;
- suíte existente e Ruff continuam passando;
- comportamento alterado foi executado, não apenas inspecionado;
- caminhos de erro relevantes estão testados;
- não há debug, código morto, dependência ou refatoração fora do escopo;
- documentação é atualizada quando a tarefa muda comportamento público.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Conteúdo indisponível ou protegido | High | Falhar somente o item, registrar motivo e não contornar proteção. |
| Resultado incorreto para consulta textual | High | Registrar URL/origem resolvida e marcar correspondência como verificável no relatório. |
| Escrita fora da pasta escolhida | High | Resolver caminhos, bloquear `..`/absolutos derivados e testar traversal. |
| Comando externo inseguro | High | Lista de argumentos, sem shell, timeout e captura limitada de stderr. |
| FFmpeg ausente/incompatível | High | Preflight antes da fila com mensagem de correção acionável. |
| Arquivo parcial tratado como concluído | Medium | Trabalhar em nome temporário e só registrar após saída final válida. |
| Interface congelada ou atualizada pela thread errada | Medium | Fila de eventos e polling com `after()` na thread Tkinter. |
| Testes dependentes da internet | Medium | Fake runner em toda suíte; download real apenas no smoke manual. |
| Nomes incompatíveis no Windows | Medium | Sanitização central e tabela de casos reservados/collisions. |

## Parallelization

O caminho crítico é sequencial. Depois da Task 11, a documentação inicial da Task 15 pode ser redigida enquanto Tasks 12–14 avançam, mas sua verificação final depende de todas elas. Nenhuma implementação paralela deve modificar o mesmo arquivo.

## Task List Target

As tarefas detalhadas e checkpoints ficam em `tasks/todo.md`.

## Open Questions

- Nenhuma bloqueia o MVP. Formatos adicionais, instalador e integrações autenticadas permanecem fora do escopo.
