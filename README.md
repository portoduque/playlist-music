# Playlist Music

Aplicativo desktop local e open source para organizar listas de músicas de fontes autorizadas em uma pasta portátil com MP3s e playlists reproduzíveis. O MVP está em desenvolvimento; o pacote, as ferramentas de qualidade e todos os importadores de lista planejados já estão configurados, mas o fluxo de conclusão ainda será refinado.

## Estado atual

O comando abaixo abre a tela local inicial:

```powershell
py -m playlist_music
```

Ela permite informar o nome da playlist, colar consultas ou URLs, importar uma lista, escolher a pasta e a qualidade. Ao criar, o processamento local ocorre em segundo plano e a tela recebe atualizações de progresso sem ser manipulada pela thread de trabalho.

O escopo planejado, a ordem de implementação e os critérios de aceite estão em [SPEC.md](SPEC.md), [tasks/plan.md](tasks/plan.md) e [tasks/todo.md](tasks/todo.md).

### Importação disponível para desenvolvimento

O código já normaliza consultas e URLs HTTP(S) por texto colado, `.txt` UTF-8 (com ou sem BOM), `.csv`, `.m3u`, `.m3u8` e `.json`. Em CSV, `title`, `artist` e `url` podem aparecer em qualquer ordem; títulos entre aspas são aceitos. M3U ignora comentários e mantém caminhos relativos. JSON aceita uma lista de strings ou objetos simples com `title`, `artist` e `url`. Linhas vazias são ignoradas, a ordem e a origem são preservadas, e problemas por item são recuperáveis. A tela já aceita texto colado e importa esses cinco formatos, mostrando a contagem válida/inválida.

```python
from pathlib import Path

from playlist_music.imports import (
    parse_csv_file,
    parse_json_file,
    parse_m3u_file,
    parse_pasted_text,
    parse_txt_file,
)

result = parse_pasted_text("Artista - Música\nhttps://example.com/song")
txt_result = parse_txt_file(Path("minhas-musicas.txt"))
csv_result = parse_csv_file(Path("minhas-musicas.csv"))
m3u_result = parse_m3u_file(Path("minhas-musicas.m3u8"))
json_result = parse_json_file(Path("minhas-musicas.json"))
```

### Preparação segura da saída

O código sanitiza nomes para Windows, bloqueia componentes de caminho inseguros, mantém o arquivo calculado dentro da pasta selecionada, evita colisões com sufixos determinísticos e identifica duplicatas preservando a primeira ocorrência. Na execução unitária de uma faixa, só há sucesso depois que o MP3 final existe dentro dessa pasta; arquivos parciais não contam como concluídos e um arquivo existente não é sobrescrito.

### Pré-checagem, execução e fila interna

O código verifica se o FFmpeg está disponível e se o módulo instalado do `yt-dlp` responde à consulta de versão. Também monta comandos de extração MP3 com qualidade `recommended` (padrão), `balanced` ou `compact`; cada argumento permanece separado, sem shell. Já existe um executor interno para uma faixa, com timeout, erro limitado, proteção contra sobrescrita e validação do arquivo final. A fila interna processa itens em ordem, comunica progresso e continua após falhas; sucessos, falhas e duplicatas têm estados finais distintos.

### Metadados internos

O módulo interno grava título, artista e álbum em tags ID3 e pode incorporar uma capa PNG ou JPEG. Metadados e capas são opcionais: uma imagem inválida ou falha de escrita é relatada sem excluir nem invalidar o MP3 já existente. O serviço headless aplica o texto da solicitação como título; dados mais ricos da fonte serão conectados em uma etapa posterior.

### Playlists e relatório internos

O módulo interno gera `.m3u8` em UTF-8 e `.m3u` em UTF-8 com BOM, ambos com caminhos relativos para que a pasta possa ser movida inteira. Somente MP3s finais e confinados à pasta entram nas playlists. O `resultado.txt` mantém a ordem da fila e registra consulta, estado, origem, arquivo e erro; parâmetros e fragmentos de URLs são removidos antes do registro. O serviço headless já conecta importação normalizada, preflight, fila, tags e artefatos à tela por uma thread de trabalho segura.

## Visão do MVP

Quando concluído, o aplicativo permitirá importar listas por texto, `.txt`, `.csv`, `.m3u`, `.m3u8` e `.json`; processar apenas fontes compatíveis, autorizadas e sem DRM; e gerar uma pasta com MP3s, metadados quando disponíveis, `resultado.txt`, `.m3u` e `.m3u8` com caminhos relativos.

O fluxo pretendido é simples: informar ou importar uma lista, escolher a pasta de destino e criar a playlist. As opções técnicas ficarão em uma seção avançada.

## Requisitos

- Python 3.11 ou mais recente.
- FFmpeg é necessário para a conversão/extração real para MP3 pelo fluxo headless.

## Instalação para desenvolvimento

No diretório do repositório, instale o pacote em modo editável com as ferramentas de desenvolvimento:

```powershell
py -m pip install -e ".[dev]"
```

Esse comando instala as dependências atuais do projeto: `yt-dlp`, Mutagen, Pytest e Ruff.

## Verificação

```powershell
py -m pytest
py -m ruff check .
py -m playlist_music
```

## Estrutura

```text
src/playlist_music/  pacote do aplicativo
tests/               testes automatizados
tasks/               plano e tarefas atômicas
SPEC.md              especificação viva do MVP
```

## Limites legais e de segurança

- O projeto não deve contornar DRM, proteções de acesso, termos de uso ou usar cookies e credenciais de terceiros.
- O processamento será local; listas e arquivos do usuário não devem ser enviados a serviços externos sem solicitação explícita.
- Fontes específicas com autenticação, integrações de streaming e outros formatos de áudio permanecem fora do escopo inicial.

## Como contribuir

Antes de alterar o código, consulte a [especificação](SPEC.md) e as [tarefas](tasks/todo.md). Cada tarefa deve ser implementada em uma mudança pequena, testada e verificável.
