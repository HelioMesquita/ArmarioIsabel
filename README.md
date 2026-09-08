# O Armario da Isabel

Aplicativo para navegar pelas pastinhas de `Roupinhas`, ampliar fotos e adicionar novas imagens pelo celular ou computador.

O projeto tem dois modos:

- Raiz do repositorio: versao estatica para GitHub Pages, somente leitura.
- `project/`: versao Docker completa, com API, upload e renomear.

A pasta `Roupinhas/` fica na raiz e alimenta os dois modos. A interface fonte fica em
`project/public/`; o script de publicacao copia essa interface para a raiz e injeta
a configuracao de modo estatico.

## Rodar com Docker

```bash
cd project
docker compose up --build
```

Depois abra:

```text
http://localhost:8080
```

Para acessar de outro aparelho na mesma rede, descubra o IP do computador que esta rodando o Docker e abra:

```text
http://SEU-IP:8080
```

## Instalar como app no celular

O projeto ja tem manifest, icones e service worker para funcionar como PWA.

- No Android/Chrome, abra o site e toque em `Instalar app`, quando o navegador permitir.
- No iPhone/Safari, abra o site, toque em compartilhar e escolha `Adicionar a Tela de Inicio`.
- Para PWA completo acessando por `http://SEU-IP:8080`, o celular pode exigir HTTPS. Sem HTTPS, alguns navegadores deixam criar apenas um atalho na tela inicial.

## Publicar no GitHub Pages

A publicacao usa a raiz do repositorio como site estatico. A cada push em `main` ou `master`, o GitHub Pages publica uma nova versao.

Antes do primeiro deploy, no GitHub, abra `Settings` > `Pages` e configure:

- Source: `Deploy from a branch`
- Branch: `main` ou `master`
- Folder: `/ (root)`

Importante: se o GitHub Pages abrir este README, a fonte esta apontando para uma pasta sem `index.html`. Use `/ (root)`, porque o script abaixo gera `index.html`, `catalog.json`, `app-config.json`, `manifest.webmanifest` e `sw.js` na raiz.

Sempre que mudar a interface em `project/public/`, fotos, nomes ou CSVs, rode na raiz do projeto:

```bash
python3 scripts/publish_static.py
```

Esse script pega o que esta em `project/public/`, gera os arquivos da raiz e injeta
`window.ARMARIO_APP_CONFIG` no `index.html` publicado. Essa variavel coloca o site
em modo estatico, usa `catalog.json` como fonte de dados e desliga upload/renomear.
Ele tambem gera icones proprios da versao online em `icons/web-icon-*`, para o PWA
instalado pelo GitHub Pages ficar diferente do app local.

O comando antigo continua funcionando como atalho:

```bash
python3 scripts/export_static.py
```

Para testar a versao estatica gerada:

```bash
python3 -m http.server 8081
```

Depois abra:

```text
http://localhost:8081
```

Se quiser que o service worker tente salvar todas as imagens no cache offline durante a instalacao, gere com:

```bash
python3 scripts/publish_static.py --precache-images
```

Sem essa opcao, o GitHub Pages salva o app e o catalogo para abrir offline, e as imagens vao sendo cacheadas conforme forem abertas no navegador.

## Como funciona

- Cada subpasta dentro de `Roupinhas` vira um botao na pagina inicial.
- Ao abrir uma pastinha, as imagens aparecem lado a lado.
- Ao clicar em uma imagem, ela abre maior.
- O botao `Renomear` altera o nome do arquivo mantendo a extensao da imagem.
- O botao `Adicionar foto` usa o seletor do aparelho, que em celular costuma oferecer camera ou biblioteca.
- Todo upload ganha um nome com data e hora atuais, por exemplo `2026-09-06_17-40-12-123456_foto.jpeg`, para evitar nomes duplicados.
- O botao `Relatorio` abre um resumo do armario e permite alternar para a tabela detalhada.
- O Docker monta `../Roupinhas` como volume, entao os uploads entram direto nas pastas locais do projeto.
- Na versao estatica do GitHub Pages, `Adicionar foto` e `Renomear` ficam desativados porque nao existe servidor Python rodando.

## Pastas

As pastas atuais sao:

- `RN`
- `0-3`
- `3-6`
- `6-9`
- `9-12`
- `Sem Idade`
