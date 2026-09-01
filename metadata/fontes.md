# Fontes, licenças e decisões de procedência

Data de consulta registrada nesta atividade: 2026-09-01.

## Dados numéricos e contexto clínico

- UCI Machine Learning Repository — Heart Disease, dataset 45: <https://archive.ics.uci.edu/dataset/45/heart%2Bdisease>. A página informa 303 instâncias, variáveis clínicas, CC BY 4.0 e o DOI `10.24432/C52P4X`. Foi usado como referência para seleção de atributos; nenhum registro do UCI é necessário para reproduzir o CSV simulado.
- Organização Mundial da Saúde — Cardiovascular diseases (CVDs): <https://www.who.int/en/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)>. Usado para contextualizar fatores de risco e a importância de detecção precoce.
- Ministério da Saúde — Infarto: <https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto>. Usado como fonte do resumo textual em português e dos termos de urgência/sintomas.

## Textos

- J. Mitchell Bruce, *The Lettsomian Lectures on Diseases and Disorders of the Heart and Arteries in Middle and Advanced Life*: página da obra <https://www.gutenberg.org/ebooks/43780>; texto UTF-8 baixado de <https://www.gutenberg.org/ebooks/43780.txt.utf-8>. A página identifica a obra como domínio público nos EUA.
- Oliver T. Osborne, *Disturbances of the Heart*: página da obra <https://www.gutenberg.org/ebooks/3731>; texto UTF-8 baixado de <https://www.gutenberg.org/ebooks/3731.txt.utf-8>. A página identifica a obra como domínio público nos EUA.

Os textos históricos são preservados como dados para NLP, não como recomendações clínicas atuais. O resumo em `docs/texto_03_resumo_infarto_ministerio_saude.txt` é uma produção autoral baseada no conteúdo da fonte oficial.

## Imagens ECG

- PhysioNet — MIT-BIH Arrhythmia Database v1.0.0: <https://physionet.org/content/mitdb/1.0.0/>.
- DOI da versão: <https://doi.org/10.13026/C2F305>.
- O PhysioNet descreve 48 trechos de ECG ambulatorial de meia hora, digitalizados a 360 amostras por segundo, com anotações revisadas por cardiologistas. A página informa Open Data Commons Attribution License v1.0.
- Os arquivos `.dat` e `.hea` dos registros são baixados pelo script apenas para derivar os PNGs. A pasta `data/raw/` é ignorada pelo Git; cada imagem entregue mantém registro, derivação, janela e URL no `manifest_ecg.csv`.

## Reprodutibilidade

- Script de geração: `tools/prepare_data.py`.
- Semente da base numérica: `20260901`.
- Registros visuais usados: `100` a `109` do MIT-BIH; 10 janelas de 5 segundos por registro.
- O conjunto visual não deve ser interpretado como 100 pacientes independentes.
