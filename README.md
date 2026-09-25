# Playlist Music

Aplicativo desktop local e open source para organizar listas de músicas de fontes autorizadas em uma pasta portátil com MP3s e playlists reproduzíveis. O MVP está em desenvolvimento; o pacote, as ferramentas de qualidade e todos os importadores de lista planejados já estão configurados.

## Estado atual

O comando abaixo abre a tela local inicial:

```powershell
py -m playlist_music
```

Ela permite informar o nome da playlist, colar consultas ou URLs, importar uma lista, escolher a pasta e a qualidade. Ao criar, o processamento local ocorre em segundo plano e a tela recebe atualizações de progresso sem ser manipulada pela thread de trabalho. No fim, ela informa quantas faixas foram concluídas, falharam, tiveram apenas avisos de metadados ou foram ignoradas como duplicadas e oferece abrir a pasta ou a playlist gerada quando os caminhos continuam válidos.

O escopo planejado, a ordem de implementação e os critérios de aceite estão em [SPEC.md](SPEC.md), [tasks/plan.md](tasks/plan.md) e [tasks/todo.md](tasks/todo.md).

### Importação disponível para desenvolvimento

O código já normaliza consultas e URLs HTTP(S) por texto colado, `.txt` UTF-8 (com ou sem BOM), `.csv`, `.m3u`, `.m3u8` e `.json`. Em CSV, `title`, `artist` e `url` podem aparecer em qualquer ordem; títulos entre aspas são aceitos. M3U ignora comentários e mantém caminhos relativos. JSON aceita uma lista de strings ou objetos simples com `title`, `artist` e `url`. Linhas vazias são ignoradas, a ordem e a origem são preservadas, e problemas por item são recuperáveis. A tela já aceita texto colado e importa esses cinco formatos, mostrando a contagem válida/inválida.

#### CSV recomendado

Para obter a correspondência e os nomes de arquivo mais confiáveis, informe uma URL de fonte autorizada junto com título e artista:

```csv
title,artist,url
Faint,Linkin Park,https://youtube.com/watch?v=SEU_ID_AUTORIZADO
```

Substitua o valor de exemplo pela URL que você tem permissão para baixar. Atualmente, o importador CSV entende somente `title`, `artist` e `url`; as demais colunas são ignoradas.

#### Validação de colunas CSV

Todo CSV abre uma janela de confirmação antes de substituir a lista atual. Ela mostra os cabeçalhos, até cinco linhas de prévia e permite vincular as três informações que o aplicativo entende: **Title**, **Artist** e **URL**. Cabeçalhos comuns em português e inglês são sugeridos automaticamente, mas a sugestão não é uma garantia: corrija os seletores quando necessário.

É obrigatório vincular ao menos **Title** ou **URL**; **Artist** é opcional. Deixe um seletor em branco para não importar aquele campo. Colunas extras, como álbum, gênero, identificadores ou anotações, não entram na importação. **Cancel**, fechar a janela ou pressionar `Esc` mantém a lista que já estava no aplicativo.

O fluxo não reconhece qualquer nome de coluna, não importa arquivos Excel (`.xlsx`/`.xls`) e não salva perfis de mapeamento.

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

Cada criação gera uma subpasta própria dentro da pasta escolhida, usando o nome da playlist. O código sanitiza nomes para Windows, bloqueia componentes de caminho inseguros, evita colisões com sufixos determinísticos (`Nome`, `Nome (2)`) e identifica duplicatas preservando a primeira ocorrência. Na execução unitária de uma faixa, só há sucesso depois que o MP3 final existe dentro dessa subpasta; arquivos parciais não contam como concluídos e um arquivo existente não é sobrescrito.

Exemplo de resultado:

```text
Pasta escolhida/
└── Rock para trabalhar/
    ├── 001 - Linkin Park - Faint.mp3
    ├── Rock para trabalhar.m3u
    ├── Rock para trabalhar.m3u8
    └── resultado.txt
```

Os caminhos das playlists são relativos à própria pasta. Por isso, você pode mover a pasta inteira sem precisar editar os arquivos `.m3u` e `.m3u8`.

### Pré-checagem, execução e fila interna

O código verifica se o FFmpeg está disponível e se o módulo instalado do `yt-dlp` responde à consulta de versão. Também monta comandos de extração MP3 com qualidade `recommended` (padrão), `balanced` ou `compact`; cada argumento permanece separado, sem shell. Já existe um executor interno para uma faixa, com timeout, erro limitado, proteção contra sobrescrita e validação do arquivo final. A fila interna processa itens em ordem, comunica progresso e continua após falhas; sucessos, falhas e duplicatas têm estados finais distintos.

### Metadados internos

O download pede ao `yt-dlp` para incorporar os metadados e a capa que a fonte disponibilizar no MP3. Em CSV ou JSON, `title` e `artist` explícitos substituem os valores conflitantes da fonte; álbum, data, gênero e capa já presentes são preservados. Cada faixa também recebe seu número de ordem. Metadados e capas são opcionais: se a etapa de pós-processamento falhar, um MP3 final válido é mantido e o aviso é registrado.

Em ordem de prioridade, título e artista informados no CSV ou JSON vencem os dados da fonte; os dados da fonte vencem a consulta textual usada como alternativa. Uma busca apenas por texto usa o primeiro resultado encontrado e pode selecionar uma versão incorreta. Quando a precisão importar, informe URL, título e artista.

### Playlists e relatório internos

O módulo interno gera `.m3u8` em UTF-8 e `.m3u` em UTF-8 com BOM, ambos com caminhos relativos para que a pasta possa ser movida inteira. Somente MP3s finais e confinados à pasta entram nas playlists. Quando houver falhas, `resultado.txt` começa com uma seção legível contendo a faixa e o motivo registrado; o resumo da tela também indica esse arquivo. Abaixo dela, o arquivo preserva os detalhes técnicos tabulados de toda a fila. Parâmetros e fragmentos de URLs são removidos antes do registro. Um aviso não exclui uma faixa já concluída. O serviço headless já conecta importação normalizada, preflight, fila, tags e artefatos à tela por uma thread de trabalho segura.

## Visão do MVP

Quando concluído, o aplicativo permitirá importar listas por texto, `.txt`, `.csv`, `.m3u`, `.m3u8` e `.json`; processar apenas fontes compatíveis, autorizadas e sem DRM; e gerar uma pasta com MP3s, metadados quando disponíveis, `resultado.txt`, `.m3u` e `.m3u8` com caminhos relativos.

O fluxo pretendido é simples: informar ou importar uma lista, escolher a pasta de destino e criar a playlist. As opções técnicas ficarão em uma seção avançada.

## Requisitos

- Python 3.11 ou mais recente.
- FFmpeg é necessário para a conversão/extração real para MP3 pelo fluxo headless.

Instale o FFmpeg pelo método indicado para seu sistema e confirme que ele está disponível no `PATH` antes de criar uma playlist:

```powershell
ffmpeg -version
```

## Instalação para desenvolvimento

No diretório do repositório, instale o pacote em modo editável com as ferramentas de desenvolvimento:

```powershell
py -m pip install -e ".[dev]"
```

Esse comando instala as dependências atuais do projeto: `yt-dlp`, Mutagen, Pytest e Ruff.

## Uso

1. Abra o aplicativo com `py -m playlist_music`.
2. Informe o nome da playlist e cole uma consulta ou URL HTTP(S) por linha — ou escolha **Import file** para usar `.txt`, `.csv`, `.m3u`, `.m3u8` ou `.json`. Para CSV, confira a prévia e os vínculos de coluna antes de confirmar.
3. Confira a contagem de itens válidos e inválidos. Corrija os itens inválidos antes de criar a playlist.
4. Escolha a pasta de saída, mantenha a qualidade **recommended** ou selecione **balanced** ou **compact** em **More options**.
5. Clique em **Create playlist**. A janela continua utilizável enquanto o progresso é exibido.
6. Ao terminar, leia o resumo e use **Open folder** ou **Open playlist** quando estiverem disponíveis. Se alguma faixa falhar, abra `resultado.txt` na pasta da playlist: a seção **FALHAS** informa o motivo de cada uma.

A pasta escolhida recebe uma nova subpasta com o nome da playlist. Ela contém os MP3s concluídos, `resultado.txt`, uma playlist `.m3u8` em UTF-8 e uma `.m3u` em UTF-8 com BOM. Os dois arquivos de playlist usam caminhos relativos; mova essa subpasta inteira para mantê-los reproduzíveis.

## Solução de problemas

| Situação | O que fazer |
| --- | --- |
| `FFmpeg was not found on PATH.` | Instale o FFmpeg, adicione-o ao `PATH` e confirme com `ffmpeg -version`. |
| `yt-dlp version check failed.` | Reinstale as dependências com `py -m pip install -e ".[dev]"` e tente novamente. |
| O CSV não deixa confirmar | Vincule pelo menos **Title** ou **URL** e não use a mesma coluna em mais de um campo. |
| A contagem mostra itens inválidos | Corrija ou remova as linhas indicadas antes de criar; o aplicativo não inicia uma lista parcialmente inválida. |
| Uma faixa falha | Abra `resultado.txt` na pasta da playlist. A seção **FALHAS** identifica a faixa e o motivo registrado; as outras continuam sendo processadas. |
| Nenhuma faixa é concluída | Revise `resultado.txt`, a disponibilidade da fonte e se ela é autorizada e sem DRM. |

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
- Nem toda fonte fornece capa ou metadados completos; o aplicativo preserva o que recebeu, mas não inventa informações ausentes.
- Fontes específicas com autenticação, integrações de streaming e outros formatos de áudio permanecem fora do escopo inicial.

## Como contribuir

Antes de alterar o código, consulte a [especificação](SPEC.md) e as [tarefas](tasks/todo.md). Cada tarefa deve ser implementada em uma mudança pequena, testada e verificável.
