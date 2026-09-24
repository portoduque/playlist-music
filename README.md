# Playlist Music

Aplicativo desktop local e open source para organizar listas de músicas de fontes autorizadas em uma pasta portátil com MP3s e playlists reproduzíveis. O MVP está em desenvolvimento; nesta versão inicial, o pacote e as ferramentas de qualidade já estão configurados, mas a criação de playlists ainda não foi implementada.

## Estado atual

O comando abaixo funciona e confirma que a base do aplicativo está instalada:

```powershell
py -m playlist_music
```

Saída atual:

```text
Playlist Music is not ready yet.
```

O escopo planejado, a ordem de implementação e os critérios de aceite estão em [SPEC.md](SPEC.md), [tasks/plan.md](tasks/plan.md) e [tasks/todo.md](tasks/todo.md).

## Visão do MVP

Quando concluído, o aplicativo permitirá importar listas por texto, `.txt`, `.csv`, `.m3u`, `.m3u8` e `.json`; processar apenas fontes compatíveis, autorizadas e sem DRM; e gerar uma pasta com MP3s, metadados quando disponíveis, `resultado.txt`, `.m3u` e `.m3u8` com caminhos relativos.

O fluxo pretendido é simples: informar ou importar uma lista, escolher a pasta de destino e criar a playlist. As opções técnicas ficarão em uma seção avançada.

## Requisitos

- Python 3.11 ou mais recente.
- FFmpeg será necessário quando a funcionalidade de conversão para MP3 for implementada.

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
