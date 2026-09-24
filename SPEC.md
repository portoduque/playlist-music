# Spec: Playlist Music MVP

## Objective

Criar um aplicativo desktop local, gratuito e open source para transformar uma lista de músicas ou links em uma pasta portátil e organizada. O usuário informa uma lista, escolhe onde salvar e recebe arquivos MP3, metadados e playlists compatíveis com players comuns.

O produto é para pessoas não técnicas: o fluxo principal deve caber em importar, escolher a pasta e clicar em criar. Configurações técnicas ficam ocultas em “Mais opções”.

### Capability Map

| Module id | Responsibility | Depends on |
|---|---|---|
| `entrada` | Importar e normalizar listas | — |
| `aquisicao` | Obter conteúdo de fontes autorizadas e não-DRM | `entrada` |
| `biblioteca` | Organizar arquivos, tags, capas e duplicatas | `aquisicao` |
| `playlist` | Gerar playlists e relatório | `biblioteca` |
| `interface` | Coordenar o fluxo para o usuário | `entrada`, `aquisicao`, `biblioteca`, `playlist` |

Build order: `entrada` → `aquisicao` → `biblioteca` → `playlist` → `interface`.

## Scope

### Included in the MVP

- Entrada por texto colado, `.txt`, `.csv`, `.m3u`, `.m3u8` e `.json` simples.
- Uma música ou URL por linha quando não houver estrutura de colunas.
- Normalização de cada item em ordem, consulta e URL opcional.
- Download apenas de fontes compatíveis, autorizadas e sem DRM.
- MP3 como único formato de áudio inicial, com qualidade padrão “Recomendada”.
- Metadados de título, artista, álbum e capa quando a fonte disponibilizar esses dados.
- Nomes seguros e numerados, deduplicação dentro da mesma execução, `.m3u8`, `.m3u` e `resultado.txt`.
- Tela local para importar, escolher pasta, selecionar qualidade, acompanhar progresso e abrir a pasta final.

### Explicitly out of scope

- DRM, bypass de proteção, cookies compartilhados ou automação de contas de terceiros.
- Servidor, login, sincronização em nuvem, telemetria, anúncios e banco de dados.
- Integrações específicas de Spotify, Apple Music ou outros serviços de streaming no primeiro lançamento.
- Formatos de áudio além de MP3 e importação nativa de `.xlsx`.

## Tech Stack

- Python 3.11+.
- Tkinter, incluído no Python, para a interface desktop local.
- `yt-dlp` como ferramenta de aquisição de fontes compatíveis.
- FFmpeg instalado pelo usuário para extração/conversão de áudio.
- Mutagen para gravar tags e capas em MP3.
- Pytest e Ruff para testes e qualidade de código.

## Commands

Após a implementação e instalação das dependências:

```powershell
py -m pip install -e ".[dev]"
py -m pytest
py -m ruff check .
py -m playlist_music
```

## Project Structure

```text
src/playlist_music/  aplicativo e regras de negócio
tests/               testes automatizados
tasks/               plano e lista de tarefas
SPEC.md              especificação viva do MVP
README.md            instalação, uso e limites do projeto
```

## Code Style

- Funções pequenas, nomes em inglês e tipos explícitos em limites de entrada e saída.
- Biblioteca padrão antes de novas dependências.
- Um único fluxo de execução; sem interfaces, factories ou plugins especulativos.
- Erros por faixa não encerram todo o trabalho.

```python
def safe_filename(value: str) -> str:
    return "".join(char for char in value if char not in '<>:"/\\|?*').strip()
```

## User Flow

1. Usuário informa um nome, cola/importa uma lista e escolhe a pasta de destino.
2. O programa mostra quantidade de itens válidos e inválidos antes de iniciar.
3. O programa processa cada item sem interromper a fila por falha individual.
4. Cada resultado é salvo em uma pasta autocontida:

```text
Minha Playlist/
├── Minha Playlist.m3u8
├── Minha Playlist.m3u
├── resultado.txt
├── 001 - Artista - Música.mp3
└── 002 - Artista - Música.mp3
```

5. Ao finalizar, o usuário pode abrir a pasta ou revisar os itens não processados.

## Settings

Padrões: MP3, qualidade recomendada, capa e metadados ativados, deduplicação ativada, abrir pasta ao terminar.

“Mais opções” permite trocar qualidade, desativar capa/metadados, definir pasta e escolher se duplicatas são ignoradas. Nenhuma configuração avançada é necessária para o fluxo principal.

## Testing Strategy

- Testes unitários para cada parser de entrada, limpeza de nomes, deduplicação e geração de playlists.
- Testes com subprocesso simulado para a integração com yt-dlp e FFmpeg; testes não baixam mídia real.
- Teste de integração usando arquivos temporários para confirmar estrutura final, relatório e caminhos relativos em `.m3u8`.
- Verificação manual da interface: importar, escolher pasta, iniciar, visualizar progresso e abrir resultado.

## Boundaries

### Always

- Validar caminhos, extensões e dados vindos do usuário.
- Preservar o melhor áudio disponibilizado pela fonte; nunca alegar melhoria por aumento artificial de bitrate.
- Continuar a fila após falhas individuais e registrar motivo no relatório.
- Executar testes e Ruff antes de marcar uma tarefa como concluída.

### Ask first

- Adicionar dependência além das listadas nesta especificação.
- Mudar a forma de aquisição, integrar serviços com autenticação ou alterar o formato padrão de saída.
- Criar instalador, releases, CI ou publicar no GitHub.

### Never

- Contornar DRM, proteções, termos de acesso ou usar credenciais/cookies de terceiros.
- Enviar lista, arquivos ou dados do usuário para serviços externos sem pedido explícito.
- Armazenar chaves, senhas ou tokens no repositório.

## Success Criteria

- O usuário consegue importar cada formato suportado e recebe erros claros por item inválido.
- Uma lista válida gera uma pasta autocontida com MP3s, `resultado.txt`, `.m3u8` e `.m3u`.
- As playlists usam caminhos relativos e funcionam quando a pasta inteira é movida.
- Falhar uma música não cancela as demais.
- A tela principal é utilizável sem abrir configurações avançadas.
- Testes de parsers, saída e falhas do downloader passam sem acesso à internet.
- O README explica instalação, uso, dependências externas e limites legais.

## Open Questions

- Nenhuma bloqueia o MVP. O suporte a Spotify, Excel e outros formatos será avaliado depois de uso real.
