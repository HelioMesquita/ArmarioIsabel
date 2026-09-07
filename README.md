# O Armario da Isabel

Site local para navegar pelas pastinhas de `Roupinhas`, ampliar fotos e adicionar novas imagens pelo celular ou computador.

## Rodar com Docker

```bash
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

## Como funciona

- Cada subpasta dentro de `Roupinhas` vira um botao na pagina inicial.
- Ao abrir uma pastinha, as imagens aparecem lado a lado.
- Ao clicar em uma imagem, ela abre maior.
- O botao `Renomear` altera o nome do arquivo mantendo a extensao da imagem.
- O botao `Adicionar foto` usa o seletor do aparelho, que em celular costuma oferecer camera ou biblioteca.
- Todo upload ganha um nome com data e hora atuais, por exemplo `2026-09-06_17-40-12-123456_foto.jpeg`, para evitar nomes duplicados.
- O botao `Relatorio` abre um resumo do armario e permite alternar para a tabela detalhada.
- O Docker monta `./Roupinhas` como volume, entao os uploads entram direto nas pastas locais do projeto.

## Pastas

As pastas atuais sao:

- `RN`
- `0-3`
- `3-6`
- `6-9`
- `9-12`
- `Sem Idade`
