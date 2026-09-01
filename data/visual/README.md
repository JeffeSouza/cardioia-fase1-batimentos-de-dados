# Coleção visual ECG

Esta pasta contém 100 imagens PNG derivadas de sinais do MIT-BIH Arrhythmia Database, disponibilizado pelo PhysioNet. Cada imagem é uma janela de 5 segundos renderizada pelo script `tools/prepare_data.py`.

- `imagens_ecg/`: 100 arquivos PNG;
- `manifest_ecg.csv`: uma linha por imagem, com registro de origem, derivação, janela, frequência de amostragem, URL e licença;
- `metadata/dataset_visual.json`: resumo da construção do conjunto.

As imagens não são 100 pacientes independentes: são 10 janelas de cada um dos registros 100 a 109, alternando as derivações disponíveis. Essa dependência deve ser respeitada em qualquer experimento para evitar vazamento entre treino e teste.

Fonte: <https://physionet.org/content/mitdb/1.0.0/>  
Licença informada pelo PhysioNet: Open Data Commons Attribution License v1.0.  
Uso: somente educacional; não é laudo nem ferramenta de diagnóstico.
