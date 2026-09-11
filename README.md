# O Armario da Isabel

Projeto para identificar as roupinhas da Isabel, acompanhar o que ja foi usado
e otimizar o armario para ela aproveitar o maximo possivel antes de perder por
crescimento.

- Raiz: site estatico do GitHub Pages, somente leitura.
- `project/`: app Docker completo, com API, upload e renomear.
- Fonte da interface: `project/public/`.
- Publicacao: `scripts/publish_static.py` gera a raiz, `catalog.json` e os icones web.
- Marcador "Ja usou": salvo apenas no navegador.
- Imagem do topo: aleatoria e rotacionada automaticamente.

## Rodar Local

```bash
cd project
docker compose up --build
```

```text
http://localhost:8080
http://SEU-IP:8080
```

## Gerar Online

```bash
python3 scripts/publish_static.py
```

Esse comando copia `project/public/` para a raiz, injeta `window.ARMARIO_APP_CONFIG`
com `upload: false` e `rename: false`, e gera `icons/web-icon-*`.

## Testar Online

```bash
python3 -m http.server 8081
```

```text
http://localhost:8081
```

## Publicar

No GitHub Pages, configure:

- Source: `Deploy from a branch`
- Branch: `main` ou `master`
- Folder: `/ (root)`

Depois de gerar a versao estatica:

```bash
git add -A
git commit -m "Publica versao estatica"
git push
```

O atalho antigo `python3 scripts/export_static.py` continua funcionando.

## Publicar Foto Nova

Depois de adicionar uma ou mais fotos dentro de `roupinhas/`, rode:

```bash
python3 scripts/publish_new_photos.py
```

Esse comando detecta imagens novas ou alteradas, regenera a versao estatica,
faz o commit com a mensagem `nova foto adicionada` e executa `git push`.

Para commitar sem subir:

```bash
python3 scripts/publish_new_photos.py --no-push
```

## Estrutura

```text
.
|-- index.html
|-- app.js
|-- styles.css
|-- catalog.json
|-- icons/
|-- project/
|   |-- docker-compose.yml
|   |-- Dockerfile
|   |-- server.py
|   `-- public/
|-- roupinhas/
`-- scripts/
```

Detalhes de classificacao das roupas ficam em `roupinhas/README.md`.
