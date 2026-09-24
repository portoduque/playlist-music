# Playlist Music MVP Tasks

## Task 1: Bootstrap the executable package

**Description:** Criar o menor pacote Python executável, separar dependências de runtime/desenvolvimento e provar que os comandos básicos funcionam.

**Acceptance criteria:**
- [x] `py -m playlist_music` inicia e encerra sem erro com um placeholder explícito.
- [x] Instalação editável disponibiliza somente as dependências aprovadas em `SPEC.md`.
- [x] Pytest e Ruff encontram o pacote no layout `src/`.

**Verification:**
- [x] `py -m pip install -e ".[dev]"`
- [x] `py -m pytest tests/test_smoke.py`
- [x] `py -m ruff check .`
- [x] `py -m playlist_music`

**Dependencies:** None

**Files likely touched:** `pyproject.toml`, `src/playlist_music/__init__.py`, `src/playlist_music/__main__.py`, `tests/test_smoke.py`

**Estimated scope:** Medium (4 files)

## Task 2: Define normalized requests and pasted-text import

**Description:** Criar o contrato `TrackRequest` e transformar texto colado em pedidos ordenados, preservando erros por linha.

**Acceptance criteria:**
- [x] Linhas de consulta e URL válidas mantêm a ordem original e índices estáveis.
- [x] Linhas vazias são ignoradas; entradas sem conteúdo útil geram erro legível.
- [x] Unicode, espaços externos e mistura de itens válidos/inválidos são cobertos.

**Verification:**
- [x] `py -m pytest tests/test_text_import.py`
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 1

**Files likely touched:** `src/playlist_music/models.py`, `src/playlist_music/imports.py`, `tests/test_text_import.py`

**Estimated scope:** Medium (3 files)

## Task 3: Import TXT and CSV files

**Description:** Reutilizar o normalizador para TXT e adicionar CSV com schema pequeno e erros localizados por linha.

**Acceptance criteria:**
- [x] TXT aceita UTF-8 e UTF-8 com BOM usando as mesmas regras do texto colado.
- [x] CSV reconhece `title`, `artist` e `url`, independentemente da ordem das colunas.
- [x] CSV cobre vírgulas entre aspas, cabeçalho inválido e linhas parcialmente válidas.

**Verification:**
- [x] `py -m pytest tests/test_tabular_import.py`
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 2

**Files likely touched:** `src/playlist_music/imports.py`, `tests/test_tabular_import.py`, `tests/fixtures/input/`

**Estimated scope:** Small (2 files + fixtures)

## Task 4: Import M3U/M3U8 and JSON files

**Description:** Completar os formatos do MVP sem alterar o contrato normalizado.

**Acceptance criteria:**
- [x] M3U/M3U8 ignora comentários, aceita BOM e preserva URLs/caminhos relativos úteis.
- [x] JSON aceita uma lista de strings ou objetos com `title`, `artist` e `url`.
- [x] Arquivo malformado, tipo raiz inválido e objetos incompletos geram erros localizados.

**Verification:**
- [x] `py -m pytest tests/test_playlist_json_import.py`
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 2

**Files likely touched:** `src/playlist_music/imports.py`, `tests/test_playlist_json_import.py`, `tests/fixtures/input/`

**Estimated scope:** Small (2 files + fixtures)

## Checkpoint A: Input contract

- [ ] Tasks 1–4 complete their focused checks.
- [ ] `py -m pytest` and `py -m ruff check .` pass.
- [ ] Every supported input reaches the same normalized model and ordering.
- [ ] Human review approves the normalized contract.

## Task 5: Constrain output paths and deduplicate requests

**Description:** Definir pasta, nomes seguros, colisões e duplicatas antes de qualquer ferramenta externa escrever arquivos.

**Acceptance criteria:**
- [x] Nomes bloqueiam caracteres inválidos, traversal, nomes reservados e finais com ponto/espaço.
- [x] Colisões recebem sufixo determinístico sem sobrescrever arquivo existente.
- [x] Duplicatas da mesma execução são detectadas preservando a primeira ocorrência.

**Verification:**
- [x] `py -m pytest tests/test_output_paths.py`
- [x] Casos incluem `..`, caminho absoluto, `CON`, Unicode, colisão e nome vazio.
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Tasks 3 and 4

**Files likely touched:** `src/playlist_music/output.py`, `src/playlist_music/models.py`, `tests/test_output_paths.py`

**Estimated scope:** Medium (3 files)

## Task 6: Validate tools and build safe commands

**Description:** Verificar yt-dlp/FFmpeg e construir argumentos de MP3 sem executar downloads.

**Acceptance criteria:**
- [x] yt-dlp é referenciado pelo interpretador Python atual; FFmpeg é localizado explicitamente.
- [x] Qualidades suportadas mapeiam para argumentos definidos e testados.
- [x] URLs/consultas são argumentos literais, sem shell ou concatenação executável.

**Verification:**
- [x] `py -m pytest tests/test_commands.py`
- [x] Testar ferramenta presente, ausente, versão inválida e entrada com caracteres de shell.
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 5

**Files likely touched:** `src/playlist_music/downloader.py`, `src/playlist_music/models.py`, `tests/test_commands.py`

**Estimated scope:** Medium (3 files)

## Task 7: Run one acquisition safely

**Description:** Executar uma única faixa com timeout, captura de erro limitada e validação da saída final.

**Acceptance criteria:**
- [x] Sucesso retorna caminho final confinado e origem resolvida.
- [x] Exit code, timeout e ausência do arquivo final retornam falhas distintas.
- [x] Arquivo parcial nunca é informado como concluído e não sobrescreve destino válido.

**Verification:**
- [x] `py -m pytest tests/test_single_download.py`
- [x] Usar somente runner/subprocesso falso; nenhuma rede.
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 6

**Files likely touched:** `src/playlist_music/downloader.py`, `src/playlist_music/models.py`, `tests/test_single_download.py`

**Estimated scope:** Medium (3 files)

## Task 8: Process a resilient queue

**Description:** Processar pedidos em sequência, emitir progresso e continuar após falhas individuais.

**Acceptance criteria:**
- [x] Ordem de entrada é preservada nos resultados e eventos de progresso.
- [x] Uma falha entre dois sucessos não impede o terceiro item.
- [x] Duplicatas, falhas e sucessos possuem estados finais exclusivos.

**Verification:**
- [x] `py -m pytest tests/test_queue.py`
- [x] Testar fila vazia, todos falham, falha intermediária e duplicatas.
- [x] `py -m pytest`
- [x] `py -m ruff check .`

**Dependencies:** Task 7

**Files likely touched:** `src/playlist_music/queue.py`, `src/playlist_music/models.py`, `tests/test_queue.py`

**Estimated scope:** Medium (3 files)

## Checkpoint B: Safe acquisition

- [x] Tasks 5–8 complete focused checks.
- [x] Full suite and Ruff pass without network.
- [x] Traversal and shell-character cases remain safe.
- [ ] Human review approves command/output boundaries.

## Task 9: Write metadata without losing audio

**Description:** Gravar tags e capa disponíveis, preservando o MP3 quando dados opcionais falharem.

**Acceptance criteria:**
- [x] Título, artista e álbum são gravados quando válidos.
- [x] JPEG/PNG válido é incorporado; imagem inválida é relatada e ignorada.
- [x] Ausência ou falha de tag não apaga nem invalida áudio concluído.

**Verification:**
- [x] `py -m pytest tests/test_metadata.py`
- [x] Ler novamente as tags gravadas em fixture temporária.
- [x] Testar sem capa, capa inválida e erro de escrita simulado.
- [x] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Task 8

**Files likely touched:** `src/playlist_music/metadata.py`, `tests/test_metadata.py`, `tests/fixtures/audio/`

**Estimated scope:** Small (2 files + fixtures)

## Task 10: Generate portable playlists and report

**Description:** Criar `.m3u8`, `.m3u` e `resultado.txt` exclusivamente a partir dos resultados finais.

**Acceptance criteria:**
- [x] Playlists incluem apenas arquivos concluídos e usam caminhos relativos na ordem original.
- [x] M3U8 preserva Unicode; M3U usa representação compatível documentada.
- [x] Relatório registra consulta, status, origem, arquivo e erro sem expor dados sensíveis.

**Verification:**
- [x] `py -m pytest tests/test_artifacts.py`
- [x] Mover diretório temporário e validar que todas as entradas ainda resolvem.
- [x] Testar zero sucessos, Unicode, falha e duplicata.
- [x] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Tasks 8 and 9

**Files likely touched:** `src/playlist_music/artifacts.py`, `src/playlist_music/models.py`, `tests/test_artifacts.py`

**Estimated scope:** Medium (3 files)

## Task 11: Assemble the headless end-to-end service

**Description:** Compor importação, preflight, fila, metadados e artefatos em uma única função de aplicação utilizável pela UI.

**Acceptance criteria:**
- [x] Entrada válida com fake runner produz a pasta completa prevista em `SPEC.md`.
- [x] Erros de entrada/preflight impedem início; falhas por faixa não cancelam a fila.
- [x] O serviço expõe eventos de progresso sem conhecer Tkinter.

**Verification:**
- [x] `py -m pytest tests/test_service.py`
- [x] Executar cenários: sucesso total, sucesso parcial, dependência ausente e entrada inválida.
- [x] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Task 10

**Files likely touched:** `src/playlist_music/service.py`, `src/playlist_music/models.py`, `tests/test_service.py`

**Estimated scope:** Medium (3 files)

## Checkpoint C: Portable library

- [x] Tasks 9–11 complete focused checks.
- [x] Full suite and Ruff pass without network.
- [x] Temporary output can be moved while playlists remain valid.
- [ ] Human review approves the headless user flow.

## Task 12: Build the minimal input screen

**Description:** Criar a tela com nome, texto/importação, pasta, qualidade e opções avançadas recolhidas.

**Acceptance criteria:**
- [x] Fluxo padrão exibe somente os campos essenciais e “Criar playlist”.
- [x] Importação mostra contagem válida/inválida antes de executar.
- [x] Teclado, foco, labels e mensagens básicas permanecem acessíveis.

**Verification:**
- [x] `py -m pytest tests/test_ui_state.py`
- [x] Testar estado inicial, importação válida/inválida e expansão de opções.
- [ ] Inspeção manual de navegação por teclado e escala do Windows.
- [x] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Task 11

**Files likely touched:** `src/playlist_music/app.py`, `src/playlist_music/ui_state.py`, `src/playlist_music/__main__.py`, `tests/test_ui_state.py`

**Estimated scope:** Medium (4 files)

## Task 13: Run work without freezing the UI

**Description:** Conectar o serviço a uma thread de trabalho e entregar eventos à thread principal por fila.

**Acceptance criteria:**
- [ ] Nenhum widget é alterado fora da thread Tkinter.
- [ ] Progresso e resultado chegam em ordem e um segundo início simultâneo é bloqueado.
- [ ] Exceção inesperada da thread vira mensagem recuperável, não encerramento silencioso.

**Verification:**
- [ ] `py -m pytest tests/test_worker.py`
- [ ] Testar eventos, exceção, término e dupla execução com serviço falso.
- [ ] Teste manual confirma que a janela pode ser movida durante processamento falso.
- [ ] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Task 12

**Files likely touched:** `src/playlist_music/worker.py`, `src/playlist_music/app.py`, `tests/test_worker.py`

**Estimated scope:** Medium (3 files)

## Task 14: Complete the user feedback flow

**Description:** Mostrar progresso por faixa, resumo final, pendências e ações de abrir pasta/playlist.

**Acceptance criteria:**
- [ ] Usuário distingue sucesso, falha e duplicata sem ler logs técnicos.
- [ ] “Abrir pasta” usa o recurso nativo do sistema somente para a pasta validada.
- [ ] Após término ou erro, controles voltam a um estado utilizável.

**Verification:**
- [ ] `py -m pytest tests/test_ui_completion.py`
- [ ] Testar sucesso total, parcial, zero sucessos e falha inesperada.
- [ ] Teste manual do fluxo completo com serviço falso.
- [ ] `py -m pytest` and `py -m ruff check .`

**Dependencies:** Task 13

**Files likely touched:** `src/playlist_music/app.py`, `src/playlist_music/ui_state.py`, `tests/test_ui_completion.py`

**Estimated scope:** Medium (3 files)

## Checkpoint D: User experience

- [ ] Tasks 12–14 complete focused checks.
- [ ] Full suite and Ruff pass.
- [ ] Interface remains responsive and keyboard-usable.
- [ ] Human review approves the complete fake-service flow.

## Task 15: Document and verify the MVP

**Description:** Escrever instruções reproduzíveis, executar a matriz final e registrar evidências dos critérios de sucesso.

**Acceptance criteria:**
- [ ] README cobre instalação, FFmpeg, formatos, uso, solução de erros e limites legais.
- [ ] Uma instalação limpa consegue executar testes e abrir o aplicativo seguindo somente o README.
- [ ] Cada critério de sucesso de `SPEC.md` possui verificação automatizada ou manual registrada.

**Verification:**
- [ ] `py -m pip install -e ".[dev]"`
- [ ] `py -m pytest`
- [ ] `py -m ruff check .`
- [ ] `py -m playlist_music`
- [ ] Smoke test manual com uma fonte autorizada e reprodução da `.m3u8` em um player.

**Dependencies:** Task 14

**Files likely touched:** `README.md`, `SPEC.md`, `tasks/plan.md`, `tasks/todo.md`

**Estimated scope:** Medium (4 files)

## Checkpoint E: Complete

- [ ] Todas as tarefas e checkpoints anteriores estão concluídos.
- [ ] Definition of Done completa foi aplicada.
- [ ] Suíte, Ruff, execução do aplicativo e smoke test autorizado passam.
- [ ] Nenhum segredo, cookie, mídia de teste não licenciada ou arquivo parcial permanece.
- [ ] Human review and approval recorded before publication.
