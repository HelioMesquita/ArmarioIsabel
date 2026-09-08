# Projeto roupinhas da Isabel

Este diretório organiza e classifica fotos das roupas da Isabel por tamanho. A classificação inicial do usuário serviu como base, mas a regra atual é criar novos tipos quando necessário e, ao mesmo tempo, manter agrupamentos práticos para contar estoque.

## Estado Atual

- Pasta raiz: `/Users/mesquitahelio/Desktop/Isabel/MeuArmario/roupinhas`
- Pastas de tamanho existentes agora:
  - `RN/`
  - `0-3/`
  - `3-6/`
  - `6-9/`
  - `9-12/`
  - `Sem Idade/`
- Total de imagens classificadas: 160
- Arquivo detalhado: `classificacao_roupinhas_isabel.csv`
- Arquivo resumido: `resumo_classificacao_roupinhas_isabel.csv`
- Mapa da renomeação realizada: `mapa_renomeacao_roupinhas_isabel.csv`
- Tabela específica de laços: `classificacao_lacos_isabel.csv`

Observação histórica: a foto que antes era `RN/Image 3.jpeg` foi movida pelo usuário para `0-3/` e depois renomeada para `0-3/Vestido_Manga_Curta_Passeio_Saída.jpeg`.

Observação desta rodada: dois bodies do Snoopy/Woodstock que estavam registrados em `6-9/` foram movidos pelo usuário para `9-12/`; o CSV detalhado, o resumo e o mapa de renomeação já foram atualizados.

Observação desta rodada: a pasta temporária `Sem Classificação/` foi organizada como `Sem Idade/` para itens de enxoval, banho, sono, meias e acessórios que não pertencem a uma faixa única de roupa. Quando a embalagem mostrar idade específica, registrar essa informação em `tamanho_identificado`.

Observação desta rodada: a pasta `Laços/` também foi incorporada a `Sem Idade/`, com acessórios individuais classificados como `Acessório` e kits com vários laços/faixas classificados como `Conjunto`.

Observação desta rodada: em 2026-09-06 foram classificadas e renomeadas as fotos adicionadas hoje, totalizando 160 imagens no CSV detalhado. O resumo, a tabela específica de laços e o mapa de renomeação foram atualizados.

Observação sobre `classificacao_lacos_isabel.csv`: esta tabela é específica para acessórios de cabelo. Diferente do CSV geral, a coluna `quantidade` conta os laços/faixas individuais visíveis dentro de kits/cartelas, agrupados por `detalhe` e `cor`.

## Princípios de Classificação

1. Manter uma linha por imagem/peça no CSV detalhado.
2. Sempre começar revisando se existem imagens novas, removidas ou movidas nas pastas.
3. Usar a pasta como `tamanho_pasta`.
4. Para itens sem faixa de roupa, usar `Sem Idade` como `tamanho_pasta`.
5. Usar etiqueta visível na roupa ou embalagem como `tamanho_identificado`.
6. Se a etiqueta não estiver legível, preencher `tamanho_identificado` como `Não Visível`; se idade/tamanho não se aplicar, usar `Não Aplicável`.
7. Se a etiqueta visível divergir da pasta, não mover automaticamente; registrar a etiqueta em `tamanho_identificado` e explicar em `observacoes`.
8. Usar acentos corretamente em todos os campos textuais.
9. Manter `grupo`, `tipo_classificacao` e `subtipo` com aparência capitalizada e consistente. Exemplos: `Macacão`, `Calça`, `Calçado`, `Body Manga Curta`, `Macacão com Pezinho`.
10. O campo `grupo` deve ser amplo e estável para contagem:
   - `Body`
   - `Macacão`
   - `Vestido`
   - `Frio/Linha`
   - `Conjunto`
   - `Calça`
   - `Calçado`
   - `Acessório`
   - `Meia`
   - `Macaquinho/Jardineira`
   - `Enxoval/Banho`
   - `Sono/Enxoval`
   - novos grupos podem ser criados se aparecerem peças diferentes, como `Shorts`, `Babador`, `Luva`, `Naninha`, `Escova/Pente`, etc.
11. O campo `tipo_classificacao` deve agrupar itens semelhantes, sem excesso de categorias.
12. O campo `subtipo` guarda detalhes específicos sem quebrar demais os agrupamentos.
13. Quando uma imagem mostrar vários itens que formam um conjunto, classificar primeiro como `Conjunto` e descrever os itens que compõem o conjunto.
14. Materiais devem ser descritos como aparentes pela imagem, por exemplo `Algodão`, `Algodão Canelado`, `Linha/Tricô`, `Linha/Crochê`.
15. Se houver dúvida, usar `confianca` menor ou explicar em `observacoes`.
16. O CSV usa separador `;` para abrir melhor em Excel/Numbers com configuração brasileira.

## Padrão de Nomes dos Arquivos

As imagens classificadas devem seguir este padrão:

```text
Grupo_Subgrupo_Descrição.jpeg
Grupo_Subgrupo_Descrição_01.jpeg
Grupo_Subgrupo_Descrição_02.jpeg
```

Regras:

- Usar acentos e capitalização nos nomes dos arquivos, acompanhando a tabela.
- Usar `_` entre palavras, sem espaços.
- Manter cada arquivo dentro da pasta de tamanho correta, por exemplo `RN/`, `0-3/`, `3-6/`, `6-9/`, `9-12/` ou `Sem Idade/`.
- `Grupo` vem da coluna `grupo`.
- `Subgrupo` vem da coluna `tipo_classificacao`, removendo repetições óbvias do grupo. Exemplo: `Body Manga Curta` vira `Manga_Curta`.
- `Descrição` vem da coluna `subtipo`, também removendo repetições óbvias. Exemplo: `Body Básico Liso` vira `Básico_Liso`.
- Se houver mais de uma imagem com o mesmo grupo/tipo/subtipo, usar `estampa_ou_detalhes` e/ou `cor_predominante` para diferenciar quando as peças não forem iguais.
- Adicionar número no final somente quando ainda houver itens iguais na mesma pasta depois da descrição completa: `_01`, `_02`, `_03`.
- Se uma imagem for única naquele nome-base, não adicionar número.
- A numeração reinicia por pasta e por mesmo nome-base.
- A extensão deve ser mantida em minúsculo.

Exemplos reais:

- `RN/Macacão_com_Pezinho_Algodão_Manga_Longa.jpeg`
- `RN/Body_Manga_Curta_Básico_Liso_Branco_01.jpeg`
- `RN/Body_Manga_Curta_Básico_Liso_Branco_02.jpeg`
- `0-3/Calça_Básica_Cinza.jpeg`
- `6-9/Conjunto_Blusa_Manga_Longa_e_Calça_Branca_com_Coração.jpeg`

Sempre atualizar a coluna `arquivo` no CSV detalhado depois de renomear. Quando houver uma renomeação em lote, registrar o antes/depois em `mapa_renomeacao_roupinhas_isabel.csv`.

## Categorias de Base

Estas categorias foram dadas pelo usuário como ponto de partida. Elas não são uma lista fechada: devem orientar a classificação, mas podem ser agrupadas, renomeadas ou expandidas quando as imagens mostrarem um tipo novo.

- Macacão Algodão
- Macacão Inverno
- Body Manga Curta
- Body Manga Longa
- Body + Shorts
- Casaco/Blusa de Frio
- Vestido
- Vestido Manga Curta
- Conjunto Calça + Blusa + Body Manga Comprida
- Calça
- Shorts
- Tênis
- Meia
- Meia Longa
- Babador
- Luva
- Casaco de Lã
- Mantinha Algodão
- Mantinha Inverno
- Jardineira
- Conjunto Moletom
- Naninha
- Pano de Boca
- Conjunto Calça + Blusa Manga Comprida
- Escova/Pente
- Roupas de Linha
- Sapatinho de Linha
- Toalha
- Cueiro
- Saco de Dormir

Ao evoluir a taxonomia, preferir:

- `grupo`: nível amplo para contagem, como `Body`, `Macacão`, `Vestido`, `Frio/Linha`, `Conjunto`, `Calça`, `Calçado`, `Acessório`, `Macaquinho/Jardineira`, `Meia`, `Enxoval/Banho`, `Sono/Enxoval`.
- `tipo_classificacao`: tipo prático, como `Body Manga Curta`, `Macacão com Pezinho`, `Casaco/Cardigã de Linha`, `Conjunto Calça e Blusa`, `Conjunto Body e Shorts`, `Faixa de Cabelo`, `Toalha com Capuz`, `Saco de Dormir`.
- `subtipo`: detalhe visual, como `Body Básico Liso`, `Body Transpassado Estampado`, `Macacão Algodão Canelado`, `Conjunto Body Manga Longa e Calça`.

Para conjuntos, tentar agrupar pelo conjunto inteiro em vez de abrir uma linha separada para cada item, desde que a foto represente o conjunto como uma unidade. Exemplo:

- `grupo`: `Conjunto`
- `tipo_classificacao`: `Conjunto Calça, Blusa e Body`
- `subtipo`: `Body Manga Longa, Calça Comprida e Blusa Manga Comprida`
- `observacoes`: incluir detalhes como material, estampa, cor e se alguma peça do conjunto estiver parcialmente escondida.

## Taxonomia Atual

Resumo atual por tamanho e tipo:

| tamanho_pasta | grupo | tipo_classificacao | quantidade |
|---|---|---|---:|
| 0-3 | Acessório | Touca | 1 |
| 0-3 | Body | Body Manga Curta | 8 |
| 0-3 | Body | Body Manga Longa | 8 |
| 0-3 | Body | Body Sem Manga | 6 |
| 0-3 | Calça | Calça | 2 |
| 0-3 | Conjunto | Conjunto 2 Bodies Manga Curta e Calça | 1 |
| 0-3 | Conjunto | Conjunto 2 Bodies Manga Longa e Calça | 1 |
| 0-3 | Conjunto | Conjunto Body Manga Curta e Calça | 1 |
| 0-3 | Conjunto | Conjunto Body Manga Curta, Casaco com Capuz e Calça | 1 |
| 0-3 | Conjunto | Conjunto Body Manga Longa e Calça | 1 |
| 0-3 | Conjunto | Conjunto Body e Shorts | 1 |
| 0-3 | Conjunto | Conjunto Moletom | 1 |
| 0-3 | Conjunto | Conjunto Vestido e Tapa-Fralda | 1 |
| 0-3 | Conjunto | Conjunto de Meias | 1 |
| 0-3 | Macacão | Macacão Inverno com Pezinho | 2 |
| 0-3 | Macacão | Macacão com Pezinho | 8 |
| 0-3 | Macaquinho/Jardineira | Macaquinho Curto Sem Manga | 1 |
| 0-3 | Meia | Meia com Babado | 1 |
| 0-3 | Vestido | Vestido Body Sem Manga | 1 |
| 0-3 | Vestido | Vestido Manga Curta | 1 |
| 0-3 | Vestido | Vestido Manga Longa | 1 |
| 3-6 | Body | Body Manga Curta | 15 |
| 3-6 | Body | Body Manga Longa | 4 |
| 3-6 | Calçado | Tênis/Sapatinho | 1 |
| 3-6 | Conjunto | Conjunto Body Manga Curta, Blusa com Capuz e Calça | 1 |
| 3-6 | Conjunto | Conjunto Body Manga Longa e Calça | 4 |
| 3-6 | Conjunto | Conjunto Casaco, Calça e Sapatinho de Linha | 1 |
| 3-6 | Conjunto | Conjunto Macacão, Body e Babador | 1 |
| 3-6 | Conjunto | Conjunto Vestido e Body Manga Longa | 1 |
| 3-6 | Frio/Linha | Casaco/Cardigã de Linha | 1 |
| 3-6 | Frio/Linha | Casaco/Jaqueta de Frio | 1 |
| 3-6 | Macacão | Macacão Inverno com Pezinho | 1 |
| 3-6 | Macaquinho/Jardineira | Macaquinho Curto Manga Curta | 4 |
| 3-6 | Macaquinho/Jardineira | Macaquinho Curto Sem Manga | 1 |
| 6-9 | Body | Body Manga Curta | 5 |
| 6-9 | Conjunto | Conjunto Blusa Manga Longa e Calça | 1 |
| 6-9 | Conjunto | Conjunto Vestido e Body Manga Longa | 1 |
| 6-9 | Conjunto | Conjunto Vestido, Tapa-Fralda e Faixa | 1 |
| 6-9 | Vestido | Vestido Manga Longa | 1 |
| 9-12 | Body | Body Manga Curta | 2 |
| 9-12 | Conjunto | Conjunto Moletom | 1 |
| 9-12 | Conjunto | Conjunto Vestido, Blusa e Faixa | 1 |
| RN | Body | Body Manga Curta | 11 |
| RN | Body | Body Manga Longa | 9 |
| RN | Calçado | Sapatinho de Linha | 1 |
| RN | Conjunto | Conjunto de Meias | 1 |
| RN | Frio/Linha | Blusa de Frio de Linha | 1 |
| RN | Frio/Linha | Casaco/Cardigã de Linha | 2 |
| RN | Macacão | Macacão com Pezinho | 9 |
| Sem Idade | Acessório | Faixa de Cabelo | 3 |
| Sem Idade | Calçado | Meia/Sapatinho Antiderrapante | 4 |
| Sem Idade | Conjunto | Conjunto Babadores Bandana | 1 |
| Sem Idade | Conjunto | Conjunto Faixas de Cabelo | 3 |
| Sem Idade | Conjunto | Conjunto Manta e Naninha | 1 |
| Sem Idade | Conjunto | Conjunto Paninhos de Boca, Paninhos de Ombro e Cueiros | 1 |
| Sem Idade | Conjunto | Conjunto Pano de Boca e Babinha | 1 |
| Sem Idade | Enxoval/Banho | Cueiro | 1 |
| Sem Idade | Enxoval/Banho | Roupão com Capuz | 1 |
| Sem Idade | Enxoval/Banho | Toalha com Capuz | 3 |
| Sem Idade | Meia | Meia Longa | 4 |
| Sem Idade | Sono/Enxoval | Jogo de Lençol | 1 |
| Sem Idade | Sono/Enxoval | Manta Inverno | 1 |
| Sem Idade | Sono/Enxoval | Manta Soft | 1 |
| Sem Idade | Sono/Enxoval | Saco de Dormir | 2 |
## Colunas do CSV Detalhado

`classificacao_roupinhas_isabel.csv` contém:

- `arquivo`: caminho relativo da imagem.
- `diretorio`: pasta onde a imagem está.
- `tamanho_pasta`: tamanho inferido pelo nome da pasta.
- `tamanho_identificado`: tamanho lido na etiqueta, quando visível.
- `grupo`: agrupamento principal.
- `tipo_classificacao`: classificação prática para contagem.
- `subtipo`: detalhe mais específico.
- `material_aparente`: material estimado pela imagem.
- `cor_predominante`: cor principal da peça.
- `manga`: manga curta, manga longa, sem manga, etc.
- `perna_ou_pezinho`: informação de perna/pezinho quando aplicável.
- `fechamento`: botões, zíper, pressão, etc.
- `estampa_ou_detalhes`: estampas, bordados, gola, renda.
- `quantidade`: normalmente `1`.
- `confianca`: nível de confiança da classificação.
- `observacoes`: notas livres.

## Tabela Específica de Laços

`classificacao_lacos_isabel.csv` contém uma visão agrupada somente dos acessórios de cabelo.

- `tipo_acessorio`: tipo amplo, como `Faixa de Cabelo`.
- `modelo`: formato prático, como `Faixa Elástica com Laço`.
- `detalhe`: característica principal, como `Laço Gorgurão Liso`, `Laço com Flor Bordada` ou `Laço Personalizado com Nome e Flores`.
- `cor`: cor ou família de cor usada para agrupar.
- `quantidade`: quantidade de laços/faixas individuais visíveis, não quantidade de fotos.
- `arquivos_origem`: uma ou mais imagens de onde a contagem veio.
- `material_aparente`: material estimado pela imagem.
- `confianca`: confiança da contagem e classificação.
- `observacoes`: nota sobre contagem, sobreposição no pacote ou detalhe visual.

Sugestão de manutenção: quando um kit estiver parcialmente sobreposto ou sem etiqueta de quantidade, contar apenas os itens visíveis, usar `confianca` como `Média` e explicar em `observacoes`.

## Como Continuar Quando Chegarem Novas Imagens

As pastas podem receber novas imagens a qualquer momento. Todo novo agente deve primeiro revarrer o disco e comparar com o CSV atual antes de classificar, renomear ou resumir.

1. Revarrer todas as imagens:

```bash
rg --files -g '*.jpg' -g '*.jpeg' -g '*.png' -g '*.heic' -g '*.HEIC' -g '*.JPG' -g '*.JPEG' -g '*.PNG'
```

2. Comparar o resultado com `classificacao_roupinhas_isabel.csv`.
3. Inspecionar visualmente cada imagem nova ou movida.
4. Se aparecer uma pasta temporária como `Sem Classificação/`, usar os nomes dos arquivos como pista, classificar o que for possível e organizar os itens em uma pasta final, como `Sem Idade/`.
5. Adicionar ou atualizar uma linha no CSV detalhado.
6. Renomear a imagem seguindo o padrão `Grupo_Subgrupo_Descrição.jpeg`.
7. Adicionar `_01`, `_02`, `_03` somente quando houver itens iguais na mesma pasta.
8. Atualizar a coluna `arquivo` no CSV detalhado com o caminho novo.
9. Atualizar `resumo_classificacao_roupinhas_isabel.csv` agrupando por:

```text
tamanho_pasta + grupo + tipo_classificacao
```

10. Validar que todas as imagens do disco estão no CSV e que o resumo bate com o detalhe.
11. Se houver novos laços/faixas de cabelo, atualizar também `classificacao_lacos_isabel.csv`, agrupando por `detalhe + cor` e contando os itens individuais visíveis.

Comando de validação usado:

```bash
python3 -c "import csv, pathlib, collections; root=pathlib.Path('.'); files={str(p) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.heic'}}; rows=list(csv.DictReader(open('classificacao_roupinhas_isabel.csv',encoding='utf-8'), delimiter=';')); paths={r['arquivo'] for r in rows}; print('imagens_no_disco',len(files)); print('linhas_detalhadas',len(rows)); print('faltando_no_csv',sorted(files-paths)); print('no_csv_sem_arquivo',sorted(paths-files)); print('resumo_calculado'); [print(';'.join(k),v) for k,v in sorted(collections.Counter((r['tamanho_pasta'],r['grupo'],r['tipo_classificacao']) for r in rows).items())]"
```

## Notas Para Outro Agente

- Não trate a lista original do usuário como fechada; ela é apenas uma referência.
- Use acentos e capitalização nos valores de classificação.
- Evite criar categorias muito específicas quando `subtipo`, `estampa_ou_detalhes` e `observacoes` resolverem.
- Atualize caminhos quando o usuário mover imagens entre pastas.
- Preserve uma linha por foto, mesmo quando várias peças forem idênticas, porque cada foto representa uma peça no inventário.
- Quando houver vários itens do mesmo tipo ou uma composição de look, classificar como `Conjunto` e descrever as peças no `subtipo`.
- Antes de entregar, confira:
  - total de imagens no disco;
  - total de linhas do CSV detalhado;
  - caminhos inexistentes no CSV;
  - imagens sem linha no CSV;
  - resumo coerente com a tabela detalhada.
