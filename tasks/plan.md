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

---

# Extensão: biblioteca organizada e metadados por faixa

## Objetivo

Transformar cada execução bem-sucedida em uma playlist portátil e organizada: uma pasta própria, um MP3 por música, capa e os metadados disponíveis da fonte. Quando o CSV informar `title` e/ou `artist`, esses valores são a fonte de verdade; os campos ausentes continuam sendo preenchidos pelo `yt-dlp` quando a origem os fornecer.

O resultado desejado para uma playlist chamada `Rock 2000` será:

```text
<pasta-escolhida>/
└── Rock 2000/
    ├── 001 - Linkin Park - Faint.mp3
    ├── 002 - Eminem - Till I Collapse.mp3
    ├── Rock 2000.m3u
    ├── Rock 2000.m3u8
    └── Rock 2000-report.json
```

As playlists `.m3u` e `.m3u8` continuarão usando caminhos relativos; portanto, a pasta inteira pode ser movida e aberta em players compatíveis. ZIP, banco de dados, conta, API de catálogo e busca paga não fazem parte desta extensão.

## Limites honestos

- Não há como garantir que toda fonte publique título, artista, álbum, data e capa corretos. O aplicativo grava somente os campos que a fonte disponibilizar e nunca inventa dados.
- Em uma busca textual, `ytsearch1:` seleciona o primeiro resultado da fonte. Para máxima precisão, o usuário deve fornecer URL, `title` e `artist` no CSV.
- Uma URL de MP3 direta pode não disponibilizar metadados nem capa. Nesse caso, título/artista do CSV são preservados e os demais campos permanecem vazios.
- A capa e a incorporação de metadados são melhorias opcionais: uma falha nelas não pode descartar um MP3 de áudio que já foi criado com sucesso.

## Contrato de entrada e prioridade

O formato CSV já aceito permanece pequeno e compatível:

```csv
title,artist,url
Faint,Linkin Park,https://www.youtube.com/watch?v=...
Till I Collapse,Eminem,https://www.youtube.com/watch?v=...
```

| Campo final | Prioridade | Comportamento |
| --- | --- | --- |
| Título | `title` explícito > metadado da fonte > consulta textual | Nunca substituir um `title` do CSV. |
| Artista | `artist` explícito > metadado da fonte | Nunca substituir um `artist` do CSV. |
| Álbum, data/ano, gênero e campos adicionais | Fonte | Gravar somente quando o `yt-dlp` disponibilizar. |
| Número da faixa | Ordem de entrada | Gravar como `001`, `002` etc. e manter a mesma ordem no nome/playlist. |
| Capa | Miniatura da fonte | Incorporar quando suportada; ausência ou falha é aviso, não falha da faixa. |
| URL de origem | URL fornecida ou resolvida | Registrar no relatório para auditoria, sem expor cookies ou credenciais. |

## Decisões técnicas mínimas

1. Manter `yt-dlp` como único provedor de busca, download e metadados; não adicionar serviços, chaves ou dependências.
2. Usar `--embed-metadata` e `--embed-thumbnail` para que o próprio `yt-dlp` grave os campos e a capa disponíveis no MP3. O projeto já depende de `mutagen`, também requerido pelo `yt-dlp` em certos casos de capa.
3. Depois da aquisição, usar o escritor local existente somente para aplicar as substituições explícitas do usuário e o número da faixa. Ele não deve apagar campos incorporados que não foram explicitamente substituídos.
4. Criar uma subpasta validada por execução dentro da pasta escolhida. Todos os MP3s, playlists e relatório devem ser gravados nela, nunca na raiz da biblioteca.
5. Manter `write_metadata` como etapa tolerante a falhas. O relatório deve distinguir `download_failed` de `metadata_warning`.

## Tarefas atômicas

### Task M1 — Preservar os dados explícitos da importação

**Descrição:** Estender o contrato normalizado de faixa para conservar `title` e `artist` separados de `query` e `url`, sem quebrar TXT, M3U e JSON existentes.

**Mudanças:**

- Adicionar campos opcionais e imutáveis para título e artista em `TrackRequest`.
- No CSV, preservar as colunas já suportadas e gerar a consulta somente para busca quando não houver URL.
- No JSON, preservar `title` e `artist` se já forem aceitos no item; nos demais formatos, deixá-los ausentes.
- Manter mensagens de erro, ordem e deduplicação atuais.

**Critérios de aceitação:**

- [x] Uma linha CSV `Faint,Linkin Park,<url>` chega ao serviço com título, artista e URL separados.
- [x] Uma consulta pura continua funcionando e não ganha artista/título inventados.
- [x] Arquivos TXT, M3U, JSON e CSV atuais mantêm o comportamento anterior.

**Testes:**

- [x] Casos unitários para CSV com URL, CSV sem URL, JSON com/sem campos e Unicode.
- [x] Regressão dos testes de importação completos, sem rede.

**Arquivos prováveis:** `models.py`, `imports.py`, testes de importação.

### Task M2 — Isolar e validar a pasta da playlist

**Descrição:** Criar uma pasta de destino por execução usando o nome da playlist, sem permitir escrita fora da raiz que o usuário escolheu e sem sobrescrever uma execução anterior.

**Mudanças:**

- Implementar alocação central de diretório seguro, usando a sanitização existente e sufixos previsíveis de colisão (`Nome`, `Nome (2)`, ...).
- Resolver a pasta e verificar que ela permanece filha da raiz selecionada antes de criar arquivos.
- Passar esse diretório único ao downloader e ao gerador de artefatos.
- Expor o diretório efetivo no resultado do serviço para a interface abrir exatamente a pasta da playlist, não a raiz da biblioteca.

**Critérios de aceitação:**

- [x] Duas execuções com o mesmo nome não misturam nem sobrescrevem músicas.
- [x] Todos os MP3s, `.m3u`, `.m3u8` e relatório ficam na mesma subpasta.
- [x] Nome malicioso, reservado no Windows ou com traversal não escapa da raiz.

**Testes:**

- [x] Caminho normal, Unicode, nomes reservados, traversal e colisões.
- [x] Integração de serviço com duas faixas falsas confirma arquivos separados e artefatos no diretório correto.

**Arquivos prováveis:** `output.py`, `service.py`, `models.py`, `tests/test_output.py`, `tests/test_service.py`.

### Task M3 — Pedir metadados e capa ao provedor já instalado

**Descrição:** Ajustar o comando de aquisição para solicitar incorporação de metadados e miniatura, sem alterar a política de execução segura do subprocesso.

**Mudanças:**

- Acrescentar `--embed-metadata` e `--embed-thumbnail` à lista de argumentos, mantendo `shell=False`, `--`, timeout e caminho de FFmpeg atuais.
- Garantir que a saída resolvida continue sendo capturada para o relatório.
- Classificar erro de pós-processamento de metadados/capa como aviso quando o MP3 final validado existir; erros de download/conversão continuam sendo falhas da faixa.
- Não gerar `.info.json`, imagens soltas ou arquivos de cache no diretório final.

**Critérios de aceitação:**

- [x] O comando contém as duas opções de incorporação e ainda termina com `-- <origem>`.
- [x] Um retorno de pós-processamento com MP3 final preserva o áudio e registra aviso acionável.
- [x] Um retorno sem MP3 final permanece falha, sem artefato falso na playlist.

**Testes:**

- [x] Teste do comando exato, inclusive URL e `ytsearch1:`.
- [x] Runners falsos para sucesso, falha de download e falha opcional de pós-processamento.
- [x] Nenhum teste chama YouTube, rede ou FFmpeg real.

**Arquivos prováveis:** `downloader.py`, `models.py`, `tests/test_commands.py`, `tests/test_single_download.py`.

### Task M4 — Aplicar precedência e completar as tags locais

**Descrição:** Evoluir o escritor de ID3 para aplicar somente substituições confiáveis do usuário, conservar campos já incorporados e escrever o número de faixa.

**Mudanças:**

- Alterar a API de metadados para aceitar título/artista opcionais e número de faixa.
- Quando título/artista explícitos existirem, substituí-los no MP3; quando não existirem, preservar o que o provedor já escreveu e usar a consulta somente como último recurso para título.
- Escrever `TRCK` a partir da ordem de entrada; manter álbum, data, gênero e capa existentes se não houver valor explícito correspondente.
- Retornar aviso estruturado, sem apagar áudio, quando `mutagen` não conseguir editar um arquivo válido.

**Critérios de aceitação:**

- [x] CSV com `title` e `artist` sempre vence dados conflituosos incorporados pela fonte.
- [x] Álbum, ano/data e capa incorporados não desaparecem após a etapa local.
- [x] Um MP3 sem tags recebe ao menos título de fallback e número da faixa.
- [x] Falha de tag deixa o MP3 e o restante da playlist utilizáveis.

**Testes:**

- [x] Fixture MP3/ID3 com campos de fonte; validar precedência, preservação e `TRCK`.
- [x] Casos sem CSV, sem metadados de origem e exceção do escritor.

**Arquivos prováveis:** `metadata.py`, `service.py`, `tests/test_metadata.py`, `tests/test_service.py`.

### Task M5 — Ajustar artefatos, interface e mensagens de conclusão

**Descrição:** Fazer a interface apresentar claramente a pasta criada, o resultado por faixa e avisos de metadados sem transformar-os em falhas de download.

**Mudanças:**

- Criar `.m3u`, `.m3u8` e relatório depois de todas as faixas no diretório efetivo.
- Acrescentar ao relatório por faixa: caminho relativo, origem resolvida, status de download e aviso de metadados, quando houver.
- Atualizar o resumo/UI para mostrar “X músicas criadas” e “Y avisos de metadados”; a ação de abrir pasta aponta para a subpasta validada.
- Preservar nomes relativos em playlists e evitar regravar entradas de faixas com falha.

**Critérios de aceitação:**

- [x] Uma execução de duas faixas produz dois MP3s distintos, duas playlists e um relatório na subpasta.
- [x] Abrir pasta abre a subpasta da playlist; abrir playlist abre o `.m3u8` validado.
- [x] Aviso de metadados aparece como aviso, não reduz a contagem de músicas criadas.

**Testes:**

- [x] Integração completa com fake downloader e fake metadados, incluindo falha opcional.
- [x] Testes de ações de conclusão para a subpasta e de relatório para status mistos.

**Arquivos prováveis:** `service.py`, `artifacts.py`, `app.py`, `ui_state.py`, testes de serviço/artefatos/UI.

### Task M6 — Documentar o fluxo final e validar sem rede

**Descrição:** Atualizar a porta de entrada pública do projeto com o formato CSV recomendado, a estrutura de saída, o que é garantido e os limites de metadados.

**Mudanças:**

- Seguir obrigatoriamente `github-readme-writer` antes de alterar `README.md`.
- Explicar o fluxo simples: importar CSV, escolher pasta, criar playlist, abrir a `.m3u8` em qualquer player compatível.
- Documentar prioridade CSV > fonte, busca textual como conveniência e ausência possível de dados em MP3s diretos.
- Não anunciar compatibilidade, campos ou metadados que os testes/implementação não comprovem.

**Critérios de aceitação:**

- [x] Um usuário novo consegue criar uma pasta organizada seguindo apenas o README.
- [x] O README não promete correspondência perfeita em buscas textuais nem metadados inexistentes na fonte.

**Testes e verificação:**

- [x] `py -m pytest` e `py -m ruff check .` passam.
- [x] Smoke manual com duas fontes autorizadas: verificar dois MP3s, tags em um editor ID3 e playlist `.m3u8` após mover a pasta temporária.
- [x] Revisão final confirma que nenhuma mídia de teste não licenciada entra no repositório.

**Arquivos prováveis:** `README.md`, `tasks/plan.md`, `tasks/todo.md`.

## Ordem, checkpoints e dependências

| Ordem | Tarefa | Depende de | Resultado verificável |
| --- | --- | --- | --- |
| 1 | M1 | — | Campos explícitos chegam ao serviço. |
| 2 | M2 | M1 | Uma execução possui diretório próprio seguro. |
| 3 | M3 | M2 | Downloader pede campos/capa sem rede nos testes. |
| 4 | M4 | M1, M3 | Tags obedecem à precedência e preservam áudio. |
| 5 | M5 | M2, M4 | Resultado, relatório e UI refletem a pasta real. |
| 6 | M6 | M5 | Documentação e validação final coerentes. |

**Checkpoint M-A (após M2):** importação preserva título/artista; nenhuma saída ou colisão escapa da raiz.

**Checkpoint M-B (após M4):** testes de downloader e ID3 provam que download, capa/metadados opcionais e precedência não perdem áudio.

**Checkpoint M-C (após M6):** suíte, Ruff e smoke autorizado comprovam pasta portátil com MP3s separados.

## Matriz de testes

| Camada | Casos obrigatórios | Dependência externa |
| --- | --- | --- |
| Importação | CSV explícito, CSV só consulta, JSON, TXT, M3U, Unicode, linhas inválidas | Nenhuma |
| Saída | subpasta, colisão, traversal, nomes Windows, arquivos relativos | Nenhuma |
| Downloader | argumentos, URL, busca, sucesso, erro e pós-processamento opcional | Fake runner |
| ID3 | precedência, preservação, número, ausência de tags e erro do escritor | Fixture local |
| Serviço | duas faixas, falha intermediária, aviso de tags, relatório | Fakes + diretório temporário |
| UI | contadores, abrir subpasta, abrir `.m3u8`, recuperação | Serviço falso |
| Manual | duas fontes autorizadas e player real após mover pasta | Rede/FFmpeg, opt-in |

## Riscos e tratamento

| Risco | Tratamento |
| --- | --- |
| Fonte não publica dados confiáveis | Preferir CSV explícito e nunca inventar campos. |
| Busca escolhe vídeo errado | Exibir/registrar URL resolvida e recomendar URL no CSV. |
| Capa ou tags falham | Conservar MP3, registrar aviso e continuar a fila. |
| `yt-dlp` atualizado muda pós-processamento | Fixar testes de argumentos e classificar por existência do MP3 final, não somente por texto de stderr. |
| Pasta existente | Alocar sufixo sem sobrescrever conteúdo anterior. |
| Player não entende `.m3u8` | Manter também `.m3u` e informar que o áudio é MP3 local comum. |

## Fontes técnicas verificadas

- A documentação oficial do `yt-dlp` descreve `--embed-metadata`, os campos que ele mapeia (título, artista, álbum, data, faixa etc.) e `--embed-thumbnail` como capa incorporada.
- O projeto já usa `mutagen`; a documentação do `yt-dlp` o lista como dependência relevante para incorporação de miniatura em certos formatos.

---

# Plano de implementação: validação e mapeamento de CSV

## Objetivo

Tornar a importação de CSV previsível para pessoas não técnicas: o aplicativo sugere o significado dos cabeçalhos, mostra uma prévia curta e pede confirmação antes de substituir a lista atual. O usuário pode corrigir o vínculo entre as colunas do arquivo e `title`, `artist` e `url` sem editar o CSV manualmente.

## Decisões de arquitetura

- **Sempre validar CSV:** a página modal aparece para toda importação CSV; TXT, M3U, M3U8 e JSON continuam no fluxo atual.
- **Uma única leitura padronizada:** a importação lê cabeçalhos e amostra em memória, devolvendo um contrato simples para a UI e reaproveitando a normalização atual após a confirmação.
- **Aliases determinísticos:** normalizar apenas o cabeçalho e compará-lo a uma lista pequena PT/EN. Sem IA, rede ou heurística baseada no conteúdo das músicas.
- **Três destinos reais:** a UI permite somente `title`, `artist` e `url`, que são os campos efetivamente aceitos pelo modelo atual. Colunas extras são ignoradas.
- **Estado seguro:** cancelar, arquivo ilegível, cabeçalho duplicado ou mapeamento inválido não muda `InputState` nem a lista exibida.
- **Sem persistência:** não salvar perfis de mapeamento nem adicionar dependências; um CSV é confirmado uma vez por importação.

## Contrato de mapeamento

| Campo do sistema | Obrigatoriedade | Aliases sugeridos |
| --- | --- | --- |
| `title` | obrigatório se `url` estiver ausente | `title`, `titulo`, `música`, `musica`, `song`, `track`, `faixa`, `name` |
| `artist` | opcional | `artist`, `artista`, `band`, `banda`, `performer`, `singer` |
| `url` | obrigatório se `title` estiver ausente | `url`, `link`, `source`, `fonte` |

O mapeamento usa a identidade da coluna, não apenas o texto do cabeçalho. Cabeçalhos vazios ou repetidos são erros claros. A mesma coluna não pode ser escolhida para dois campos. Depois da confirmação, linhas seguem as regras atuais: linhas vazias são ignoradas e cada linha sem título e URL recebe erro localizado.

## Fluxo do usuário

```text
Import file → selecionar CSV → ler cabeçalho/amostra
  → modal: prévia + sugestões de Title/Artist/URL
  → Confirm → validar mapeamento → normalizar linhas → atualizar resumo
  → Cancel/erro → manter lista anterior e explicar o motivo
```

## Dependências e ordem

```text
C1 prévia e sugestões puras
  └─ C2 validação e normalização pelo mapeamento
       └─ C3 modal e integração com InputState
            └─ C4 documentação e verificação final
```

### Task C1 — Criar contrato de prévia e sugestão automática

**Descrição:** Adicionar à camada de importação um contrato imutável para cabeçalhos, até cinco linhas de prévia e sugestões de `title`, `artist` e `url`, sem alterar o parser CSV existente.

**Critérios de aceitação:**

- [x] CSV UTF-8/BOM retorna cabeçalhos distintos, até cinco linhas e sugestões determinísticas para aliases PT/EN.
- [x] Cabeçalho vazio, duplicado ou arquivo ilegível retorna erro legível e não produz prévia utilizável.
- [x] A sugestão não infere valores de músicas, não acessa rede e não escolhe duas colunas para o mesmo campo.

**Testes:**

- [x] Casos para aliases, espaços/hífens/sublinhados, Unicode, nenhuma correspondência, duplicata e BOM.
- [x] `py -m pytest tests/test_tabular_import.py` e `py -m ruff check .` passam.

**Arquivos prováveis:** `src/playlist_music/imports.py`, `src/playlist_music/models.py`, `tests/test_tabular_import.py`.

### Task C2 — Aplicar mapeamento validado ao parser CSV

**Descrição:** Transformar uma prévia confirmada em `ImportResult`, reutilizando a normalização de `TrackRequest` e preservando as regras de erro por linha.

**Critérios de aceitação:**

- [x] Um CSV com cabeçalhos não convencionais importa corretamente após o usuário selecionar as três colunas.
- [x] O parser recusa mapa sem `title` e `url`, mapa com a mesma coluna em dois destinos e coluna inexistente.
- [x] O caminho atual para CSV canônico continua compatível com seus testes existentes.

**Testes:**

- [x] Casos para título sem URL, URL sem título, artista opcional, campos entre aspas, linhas inválidas e mapa inválido.
- [x] `py -m pytest tests/test_tabular_import.py` e `py -m ruff check .` passam.

**Arquivos prováveis:** `src/playlist_music/imports.py`, `src/playlist_music/models.py`, `tests/test_tabular_import.py`.

### Checkpoint C-A — Contrato CSV seguro

- [x] C1 e C2 passam em testes focados sem rede.
- [x] Um CSV com `Musica`, `Banda` e `Link` vira os mesmos `TrackRequest` de um CSV canônico.
- [x] Nenhum mapeamento inválido substitui uma lista existente.

### Task C3 — Exibir e confirmar o mapeamento na interface

**Descrição:** No fluxo de `Import file`, abrir um modal Tkinter para CSV com prévia e seletores simples para Title, Artist e URL. Confirmar aplica o parser; cancelar mantém a entrada e o resumo anteriores.

**Critérios de aceitação:**

- [x] Ao escolher CSV, a janela mostra até cinco linhas e pré-seleciona aliases conhecidos.
- [x] Confirmar habilita apenas um mapeamento válido; o resumo mostra o resultado importado.
- [x] Cancelar, fechar a janela ou encontrar erro mantém `InputState` intacto e mostra uma mensagem recuperável.

**Testes:**

- [x] Testes de estado/controlador para confirmar, cancelar e erro sem depender de uma janela Tk real.
- [ ] Smoke manual: importar um CSV de cabeçalho não convencional, corrigir um seletor e confirmar a contagem correta.
- [x] `py -m pytest tests/test_ui_state.py tests/test_tabular_import.py` e `py -m ruff check .` passam.

**Arquivos prováveis:** `src/playlist_music/app.py`, `src/playlist_music/ui_state.py`, `tests/test_ui_state.py`, `tests/test_tabular_import.py`.

### Task C4 — Documentar e validar o fluxo CSV

**Descrição:** Atualizar a porta de entrada pública com um exemplo de CSV não convencional e o fluxo de validação. Executar a verificação completa sem incluir arquivos de música ou listas pessoais no Git.

**Critérios de aceitação:**

- [x] README explica que CSV sempre abre uma confirmação, quais campos o sistema entende e como ignorar colunas extras.
- [x] README não promete reconhecimento de qualquer cabeçalho nem suporte a Excel/perfis salvos.
- [ ] O plano e a lista de tarefas registram as provas automatizadas e manuais realizadas.

**Testes e verificação:**

- [x] `py -m pytest` e `py -m ruff check .` passam (79 testes em 25/09/2026).
- [ ] Smoke manual confirma importação, correção de vínculo, cancelamento e preservação da lista anterior.
- [x] Revisão final confirma que nenhum CSV pessoal, arquivo de áudio ou segredo entra no repositório (25/09/2026).

**Arquivos prováveis:** `README.md`, `tasks/plan.md`, `tasks/todo.md`.

### Checkpoint C-B — Mapeamento pronto para uso

- [ ] C1–C4 concluídas com testes focados.
- [x] Suíte e Ruff passam (79 testes em 25/09/2026).
- [ ] O fluxo manual confirma sugestão, correção, confirmação e cancelamento.

## Matriz de testes

| Camada | Casos | Rede |
| --- | --- | --- |
| Prévia | BOM, Unicode, cabeçalho vazio/duplicado, aliases e amostra limitada | Nunca |
| Mapeamento | destino obrigatório, coluna inexistente, duplicidade e colunas ignoradas | Nunca |
| Parser | aspas, ordem das colunas, URL/título isolados e erro por linha | Nunca |
| Estado/UI | confirmar, cancelar, fechar e preservar importação anterior | Nunca |
| Manual | CSV de cabeçalho não convencional corrigido no modal | Nunca |

## Riscos e tratamento

| Risco | Tratamento |
| --- | --- |
| Alias ambíguo | Não escolher silenciosamente; deixar o campo sem seleção para o usuário decidir. |
| Cabeçalho repetido | Bloquear confirmação com erro, em vez de depender da posição escondida. |
| Usuário cancela | Não chamar `set_imported`; manter estado anterior. |
| Modal cresce demais | Limitar prévia a cinco linhas e três seletores. |
| CSV pessoal no teste | Usar fixtures sintéticas mínimas e não versionar arquivos reais. |

## Fora deste plano

- Importação `.xlsx`/`.xls`, detecção de delimitador, edição de células, perfis salvos e mapeamento de campos de metadados ainda inexistentes no modelo.
