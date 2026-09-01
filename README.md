# CardioIA — Fase 1: Batimentos de Dados

Repositório acadêmico da atividade do Capítulo 1. O objetivo é preparar uma base inicial para o ecossistema CardioIA, combinando dados numéricos, textuais e visuais com atenção à governança, à rastreabilidade e aos riscos de viés.

> **Aviso de uso:** este material é educacional. Os casos numéricos são simulados e o rótulo de risco foi criado por uma regra didática; as imagens são sinais ECG públicos renderizados em PNG. Nenhum arquivo deve ser usado para diagnóstico, triagem real ou decisão clínica.

## Situação da entrega

Os arquivos estão organizados e publicados no repositório público do GitHub. Os links abaixo apontam para a branch `atividade-cap01`, que contém a versão entregue.

| Conjunto | Arquivo local | Link público para preencher antes do envio |
|---|---|---|
| Numérico | [`data/numerical/pacientes_cardiacos_simulados.csv`](data/numerical/pacientes_cardiacos_simulados.csv) | [CSV público no GitHub](https://github.com/JeffeSouza/cardioia-fase1-batimentos-de-dados/blob/atividade-cap01/data/numerical/pacientes_cardiacos_simulados.csv) |
| Workbook | [`outputs/atividade-cap01/cardioia_pacientes.xlsx`](outputs/atividade-cap01/cardioia_pacientes.xlsx) | [XLSX público no GitHub](https://github.com/JeffeSouza/cardioia-fase1-batimentos-de-dados/blob/atividade-cap01/outputs/atividade-cap01/cardioia_pacientes.xlsx) |
| Textual | [`docs/`](docs/) | [Textos públicos no GitHub](https://github.com/JeffeSouza/cardioia-fase1-batimentos-de-dados/tree/atividade-cap01/docs) |
| Visual | [`data/visual/imagens_ecg/`](data/visual/imagens_ecg/) | [Imagens públicas no GitHub](https://github.com/JeffeSouza/cardioia-fase1-batimentos-de-dados/tree/atividade-cap01/data/visual/imagens_ecg) |

Os links foram testados como referências da branch publicada. Caso a branch seja definida como padrão ou receba uma versão posterior, os links podem ser simplificados para apontar para `main` ou para a nova branch.

## 1. Dados numéricos — IoT

### Conteúdo

- **200 casos simulados**, uma linha por caso, em CSV UTF-8.
- [`data/numerical/pacientes_cardiacos_simulados.csv`](data/numerical/pacientes_cardiacos_simulados.csv): dataset principal.
- [`metadata/dicionario_dados.csv`](metadata/dicionario_dados.csv): significado, tipo e unidade de cada coluna.
- [`outputs/atividade-cap01/cardioia_pacientes.xlsx`](outputs/atividade-cap01/cardioia_pacientes.xlsx): versão em Excel com abas `Dados_Raw`, `Resumo` e `Dicionario`.

### Origem e preparação

Os valores foram gerados pelo script [`tools/prepare_data.py`](tools/prepare_data.py), com semente fixa `20260901`. Portanto, o conjunto pode ser recriado sem coletar dados pessoais. As faixas foram escolhidas para formar registros plausíveis de demonstração, mas **não representam pacientes reais, prevalência populacional ou uma coorte clínica**.

A seleção das variáveis foi orientada pelo dicionário do dataset Heart Disease do UCI Machine Learning Repository e por materiais de saúde cardiovascular da OMS e do Ministério da Saúde. Essas fontes são referências de modelagem e contexto; o CSV entregue nesta pasta é simulado.

Variáveis que considero mais relevantes para uma futura solução de IA:

- `pressao_sistolica_mmhg` e `pressao_diastolica_mmhg`: representam um fator de risco mensurável e podem ser acompanhadas por sensores/telemonitoramento;
- `colesterol_total_mg_dl`, `glicemia_jejum_mg_dl` e `imc`: ajudam a representar fatores metabólicos associados ao risco cardiovascular;
- `idade_anos`, `sexo`, `tabagista`, `atividade_fisica` e `historico_familiar_cardiopatia`: permitem estratificar perfis, mas exigem auditoria para que o modelo não transforme grupos demográficos em atalho injusto;
- `frequencia_cardiaca_repouso_bpm`, `saturacao_oxigenio_spo2` e `padrao_ecg`: aproximam sinais que poderiam chegar de dispositivos IoT ou exames;
- sintomas (`sintoma_dor_toracica`, `sintoma_falta_ar`, `sintoma_palpitacoes` e `sintoma_fadiga`) e `historico_doenca_cardiaca`: podem apoiar uma triagem assistida, sempre com validação e supervisão de profissionais.

O campo `rotulo_risco_cardiovascular_simulado` é um **alvo artificial** calculado a partir de uma regra documentada no script. Ele existe para permitir testes de classificação nas próximas fases, não para afirmar a presença de doença.

## 2. Dados textuais — NLP

A pasta [`docs/`](docs/) contém três arquivos `.txt`:

1. `texto_01_lettsomian_lectures_heart_arteries.txt`: download em texto puro de *The Lettsomian Lectures on Diseases and Disorders of the Heart and Arteries in Middle and Advanced Life*, de J. Mitchell Bruce, Project Gutenberg, domínio público nos EUA;
2. `texto_02_disturbances_of_the_heart.txt`: download em texto puro de *Disturbances of the Heart*, de Oliver T. Osborne, Project Gutenberg, domínio público nos EUA;
3. `texto_03_resumo_infarto_ministerio_saude.txt`: resumo autoral curto, em português, elaborado a partir de fontes oficiais contemporâneas para facilitar testes de NLP nesse idioma.

Os dois primeiros textos são históricos. Eles são úteis para experimentar vocabulário, entidades e mudança de linguagem, mas não devem ser tratados como orientação médica atual.

Aplicações possíveis de NLP:

- **extração de sintomas e entidades clínicas:** localizar termos como dor, falta de ar, pressão, arritmia, vasos e tratamentos;
- **classificação de tópicos:** separar prevenção, sintomas, fisiologia, diagnóstico e tratamento;
- **reconhecimento de negação e contexto temporal:** diferenciar “não apresenta dor” de “apresenta dor” e separar histórico de estado atual;
- **sumarização e busca semântica:** apoiar uma equipe na localização de trechos relevantes, com revisão humana;
- **detecção de linguagem desatualizada ou incerta:** especialmente importante ao comparar textos históricos com recomendações oficiais atuais.

Essas análises podem reduzir o tempo de organização de informação, mas um sistema de saúde não deve converter automaticamente um texto em diagnóstico ou recomendação terapêutica.

## 3. Dados visuais — Visão Computacional

A pasta [`data/visual/imagens_ecg/`](data/visual/imagens_ecg/) contém **100 imagens PNG** de ECG, e [`data/visual/manifest_ecg.csv`](data/visual/manifest_ecg.csv) registra a origem de cada arquivo.

As imagens foram produzidas de forma reprodutível a partir de 10 registros do **MIT-BIH Arrhythmia Database**, disponibilizado pelo PhysioNet. Para cada registro foram selecionadas 10 janelas de 5 segundos, alternando as derivações disponíveis. Assim, são 100 imagens, mas não 100 pacientes independentes: a unidade visual é uma janela de sinal.

Possíveis análises de Visão Computacional:

- detecção de traçado, linhas de grade e regiões de interesse;
- extração de características de morfologia, intervalos e amplitude após uma etapa apropriada de processamento de sinal;
- classificação exploratória de padrões de ritmo, desde que as anotações e a divisão entre treino e teste sejam feitas por paciente/registro;
- controle de qualidade de imagens, como recorte incorreto, ruído, saturação ou baixa resolução.

O arquivo `manifest_ecg.csv` evita que a imagem seja tratada como observação independente sem considerar o registro de origem. Para um estudo sério, também seriam necessários particionamento por paciente, validação externa, métricas por subgrupo e avaliação de especialistas.

## Governança, privacidade e viés

- **Proveniência:** URLs, licenças, DOI e procedimento de geração estão em [`metadata/fontes.md`](metadata/fontes.md) e nos manifests.
- **Privacidade:** a base numérica não contém dados pessoais; os sinais visuais são derivados de uma base pública e não devem ser reidentificados.
- **Licenças:** os textos do Gutenberg são domínio público conforme as páginas das obras; o MIT-BIH informa Open Data Commons Attribution License v1.0; o UCI é usado como referência e informa CC BY 4.0.
- **Qualidade:** o validador verifica contagem, colunas, arquivos vazios, duplicidades básicas e correspondência entre manifest e imagens.
- **Viés:** a base visual histórica foi coletada em um contexto específico e não representa a população brasileira; o dataset numérico simulado não estima prevalência nem desempenho real. Idade e sexo podem gerar disparidades se forem usados como atalhos.
- **Segurança:** os arquivos só devem alimentar experimentos acadêmicos isolados, com controle de acesso, versionamento, registro de alterações e revisão antes de qualquer uso fora da sala de aula.

## Estrutura

```text
CardioIA_Fase1/
├── README.md
├── data/
│   ├── numerical/
│   │   └── pacientes_cardiacos_simulados.csv
│   └── visual/
│       ├── imagens_ecg/          # 100 PNGs derivados
│       └── manifest_ecg.csv
├── docs/
│   ├── texto_01_*.txt
│   ├── texto_02_*.txt
│   └── texto_03_resumo_infarto_ministerio_saude.txt
├── metadata/
│   ├── dicionario_dados.csv
│   └── fontes.md
├── outputs/atividade-cap01/
│   └── cardioia_pacientes.xlsx
└── tools/
    ├── prepare_data.py
    ├── build_workbook.mjs
    └── validate_activity.py
```

## Reprodução e validação

Na raiz do repositório:

```powershell
python tools/prepare_data.py
node tools/build_workbook.mjs
python tools/validate_activity.py
```

O primeiro comando gera a base simulada, baixa os dois textos em formato `.txt` e busca os registros públicos necessários para renderizar as imagens. O segundo cria o workbook. O terceiro confere os entregáveis e informa qualquer placeholder de link público que ainda estiver pendente.

## Checklist da atividade

- [x] Dataset numérico com mais de 100 linhas.
- [x] Dataset em `.csv` e workbook em `.xlsx`.
- [x] Dicionário de dados, unidades e origem documentados.
- [x] Pelo menos dois textos `.txt` relacionados à saúde cardiovascular.
- [x] Pelo menos 100 imagens `.png` de ECG.
- [x] Justificativa de uso em IoT, NLP e Visão Computacional.
- [x] Considerações iniciais de governança, privacidade e viés.
- [x] Publicar os arquivos e substituir os quatro placeholders por links públicos testados.
