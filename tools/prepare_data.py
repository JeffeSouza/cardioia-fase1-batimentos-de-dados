"""Gera os dados da atividade CardioIA Fase 1.

O script é intencionalmente determinístico para a parte numérica e registra a
proveniência dos sinais ECG derivados. Ele usa apenas a biblioteca padrão e
Pillow, disponível no runtime de trabalho usado nesta atividade.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import urllib.request
from datetime import date
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - mensagem de ambiente
    raise SystemExit("Pillow é necessário para gerar as imagens ECG.") from exc


ROOT = Path(__file__).resolve().parents[1]
NUMERICAL_DIR = ROOT / "data" / "numerical"
VISUAL_DIR = ROOT / "data" / "visual"
IMAGE_DIR = VISUAL_DIR / "imagens_ecg"
DOCS_DIR = ROOT / "docs"
METADATA_DIR = ROOT / "metadata"
RAW_DIR = ROOT / "data" / "raw" / "physionet_mitdb"

NUMERICAL_FILE = NUMERICAL_DIR / "pacientes_cardiacos_simulados.csv"
DICTIONARY_FILE = METADATA_DIR / "dicionario_dados.csv"
MANIFEST_FILE = VISUAL_DIR / "manifest_ecg.csv"

NUMERIC_SEED = 20260901
MITDB_BASE = "https://physionet.org/files/mitdb/1.0.0"
MITDB_RECORDS = [str(number) for number in range(100, 110)]
SAMPLE_RATE_HZ = 360
WINDOW_SECONDS = 5
WINDOW_SAMPLES = SAMPLE_RATE_HZ * WINDOW_SECONDS
WINDOWS_PER_RECORD = 10


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def weighted_choice(rng: random.Random, options: list[tuple[str, float]]) -> str:
    total = sum(weight for _, weight in options)
    needle = rng.random() * total
    cursor = 0.0
    for value, weight in options:
        cursor += weight
        if needle <= cursor:
            return value
    return options[-1][0]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_numeric_dataset() -> None:
    rng = random.Random(NUMERIC_SEED)
    fields = [
        "id_caso",
        "idade_anos",
        "sexo",
        "pressao_sistolica_mmhg",
        "pressao_diastolica_mmhg",
        "colesterol_total_mg_dl",
        "glicemia_jejum_mg_dl",
        "diabetes_historico",
        "historico_doenca_cardiaca",
        "historico_familiar_cardiopatia",
        "tabagista",
        "atividade_fisica",
        "nivel_estresse",
        "imc",
        "frequencia_cardiaca_repouso_bpm",
        "saturacao_oxigenio_spo2",
        "sintoma_dor_toracica",
        "sintoma_falta_ar",
        "sintoma_palpitacoes",
        "sintoma_fadiga",
        "padrao_ecg",
        "rotulo_risco_cardiovascular_simulado",
    ]

    rows: list[dict[str, object]] = []
    for number in range(1, 201):
        age = int(round(clamp(rng.gauss(56, 14), 18, 88)))
        sex = rng.choice(["F", "M"])
        family_history = int(rng.random() < 0.36)
        smoker = int(rng.random() < (0.18 if sex == "F" else 0.27))
        diabetes = int(rng.random() < clamp(0.08 + max(age - 40, 0) * 0.004, 0.08, 0.30))
        activity = weighted_choice(
            rng,
            [
                ("sedentario", 0.38 if age >= 60 else 0.25),
                ("moderado", 0.42),
                ("regular", 0.33 if age < 60 else 0.20),
            ],
        )
        stress = weighted_choice(rng, [("baixo", 0.25), ("moderado", 0.50), ("alto", 0.25)])
        bmi = round(clamp(rng.gauss(27.0 + (1.2 if activity == "sedentario" else 0), 4.1), 18.0, 43.0), 1)

        history_probability = clamp(0.035 + max(age - 45, 0) * 0.004 + 0.05 * diabetes + 0.04 * smoker, 0.03, 0.35)
        cardiac_history = int(rng.random() < history_probability)

        hypertension_effect = 17 if rng.random() < clamp(0.12 + (age - 40) * 0.006, 0.12, 0.42) else 0
        systolic = int(round(clamp(108 + age * 0.43 + (bmi - 25) * 1.4 + hypertension_effect + rng.gauss(0, 10), 90, 220)))
        diastolic = int(round(clamp(67 + (systolic - 110) * 0.30 + rng.gauss(0, 7), 55, min(125, systolic - 25))))
        cholesterol = int(round(clamp(148 + age * 0.65 + (bmi - 24) * 3.0 + 12 * smoker + rng.gauss(0, 30), 105, 360)))
        glucose = int(round(clamp(78 + age * 0.22 + (bmi - 24) * 2.5 + 38 * diabetes + rng.gauss(0, 13), 65, 240)))
        resting_hr = int(round(clamp(67 + (8 if activity == "sedentario" else 0) + (4 if stress == "alto" else 0) + rng.gauss(0, 9), 45, 125)))
        spo2 = int(round(clamp(98 - 2 * smoker - (1 if bmi >= 35 else 0) + rng.gauss(0, 1.1), 91, 100)))

        symptom_load = 0.07 + 0.08 * cardiac_history + 0.05 * diabetes + max(age - 55, 0) * 0.002
        chest_pain = weighted_choice(
            rng,
            [
                ("nenhuma", max(0.45, 1.0 - symptom_load * 3.0)),
                ("pressao", 0.45 + symptom_load),
                ("queimacao", 0.18),
                ("aperto", 0.27 + symptom_load),
            ],
        )
        shortness_of_breath = int(rng.random() < clamp(0.08 + 0.05 * (age >= 65) + 0.04 * (bmi >= 30) + 0.10 * cardiac_history, 0.04, 0.45))
        palpitations = int(rng.random() < clamp(0.08 + 0.06 * (resting_hr >= 95) + 0.05 * (stress == "alto"), 0.04, 0.35))
        fatigue = int(rng.random() < clamp(0.12 + 0.06 * (age >= 65) + 0.05 * diabetes + 0.07 * cardiac_history, 0.05, 0.42))

        ecg_pattern = weighted_choice(
            rng,
            [
                ("normal", max(0.25, 0.72 - 0.14 * cardiac_history - 0.10 * (resting_hr >= 100))),
                ("alteracao_st_t", 0.13 + 0.10 * cardiac_history + 0.06 * (systolic >= 150)),
                ("taquicardia_sinusal", 0.08 + 0.11 * (resting_hr >= 100)),
                ("arritmia_suspeita", 0.07 + 0.08 * palpitations + 0.05 * cardiac_history),
            ],
        )

        risk_score = 0
        risk_score += int(age >= 55) + int(age >= 70)
        risk_score += int(systolic >= 140) + int(systolic >= 160)
        risk_score += int(cholesterol >= 240)
        risk_score += diabetes + smoker + family_history + (2 * cardiac_history)
        risk_score += int(activity == "sedentario") + int(bmi >= 30)
        risk_score += int(chest_pain != "nenhuma") + shortness_of_breath + palpitations + fatigue
        risk_score += int(ecg_pattern != "normal") + int(resting_hr > 100)
        simulated_label = int(risk_score >= 7)

        rows.append(
            {
                "id_caso": f"SIM-{number:04d}",
                "idade_anos": age,
                "sexo": sex,
                "pressao_sistolica_mmhg": systolic,
                "pressao_diastolica_mmhg": diastolic,
                "colesterol_total_mg_dl": cholesterol,
                "glicemia_jejum_mg_dl": glucose,
                "diabetes_historico": diabetes,
                "historico_doenca_cardiaca": cardiac_history,
                "historico_familiar_cardiopatia": family_history,
                "tabagista": smoker,
                "atividade_fisica": activity,
                "nivel_estresse": stress,
                "imc": f"{bmi:.1f}",
                "frequencia_cardiaca_repouso_bpm": resting_hr,
                "saturacao_oxigenio_spo2": spo2,
                "sintoma_dor_toracica": chest_pain,
                "sintoma_falta_ar": shortness_of_breath,
                "sintoma_palpitacoes": palpitations,
                "sintoma_fadiga": fatigue,
                "padrao_ecg": ecg_pattern,
                "rotulo_risco_cardiovascular_simulado": simulated_label,
            }
        )

    write_csv(NUMERICAL_FILE, fields, rows)
    write_numeric_metadata(rows)


def write_numeric_metadata(rows: list[dict[str, object]]) -> None:
    dictionary_rows = [
        ("id_caso", "Identificador técnico de um caso simulado", "texto", "sem unidade", "Não representa prontuário."),
        ("idade_anos", "Idade simulada", "inteiro", "anos", "Faixa didática de 18 a 88."),
        ("sexo", "Sexo codificado para o exercício", "categórico", "F/M", "Não deve ser usado como atalho causal."),
        ("pressao_sistolica_mmhg", "Pressão arterial sistólica", "inteiro", "mmHg", "Medida simulada em repouso/admissão."),
        ("pressao_diastolica_mmhg", "Pressão arterial diastólica", "inteiro", "mmHg", "Medida simulada em repouso/admissão."),
        ("colesterol_total_mg_dl", "Colesterol total", "inteiro", "mg/dL", "Valor simulado para exploração."),
        ("glicemia_jejum_mg_dl", "Glicemia de jejum", "inteiro", "mg/dL", "Valor simulado para exploração."),
        ("diabetes_historico", "Histórico de diabetes", "binário", "0/1", "1 = sim; 0 = não."),
        ("historico_doenca_cardiaca", "Histórico de doença cardíaca", "binário", "0/1", "1 = sim; 0 = não."),
        ("historico_familiar_cardiopatia", "Histórico familiar de cardiopatia", "binário", "0/1", "1 = sim; 0 = não."),
        ("tabagista", "Tabagismo atual simulado", "binário", "0/1", "1 = sim; 0 = não."),
        ("atividade_fisica", "Nível categórico de atividade física", "categórico", "categoria", "sedentario, moderado ou regular."),
        ("nivel_estresse", "Nível de estresse autorrelatado simulado", "categórico", "categoria", "baixo, moderado ou alto."),
        ("imc", "Índice de massa corporal", "decimal", "kg/m²", "Valor simulado."),
        ("frequencia_cardiaca_repouso_bpm", "Frequência cardíaca em repouso", "inteiro", "bpm", "Sinal compatível com um sensor IoT."),
        ("saturacao_oxigenio_spo2", "Saturação periférica de oxigênio", "inteiro", "%", "Valor simulado de oximetria."),
        ("sintoma_dor_toracica", "Categoria de dor/desconforto torácico", "categórico", "categoria", "nenhuma, pressao, queimacao ou aperto."),
        ("sintoma_falta_ar", "Presença de falta de ar", "binário", "0/1", "1 = presente; 0 = ausente."),
        ("sintoma_palpitacoes", "Presença de palpitações", "binário", "0/1", "1 = presente; 0 = ausente."),
        ("sintoma_fadiga", "Presença de fadiga", "binário", "0/1", "1 = presente; 0 = ausente."),
        ("padrao_ecg", "Padrão ECG categórico simulado", "categórico", "categoria", "Não é laudo nem interpretação clínica."),
        ("rotulo_risco_cardiovascular_simulado", "Alvo binário gerado por regra didática", "binário", "0/1", "Não é diagnóstico nem probabilidade clínica."),
    ]
    write_csv(
        DICTIONARY_FILE,
        ["nome_variavel", "descricao", "tipo", "unidade", "observacao"],
        [dict(zip(["nome_variavel", "descricao", "tipo", "unidade", "observacao"], row)) for row in dictionary_rows],
    )

    metadata = {
        "dataset": "pacientes_cardiacos_simulados",
        "generator": "tools/prepare_data.py",
        "seed": NUMERIC_SEED,
        "rows": len(rows),
        "generated_on": "2026-09-01",
        "origin": "simulated",
        "target_rule": "risk_score >= 7, with score documented in the generator and not exported",
        "privacy": "no real patient identifiers or records",
    }
    (METADATA_DIR / "dataset_numerico.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download(url: str, destination: Path) -> bytes:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return destination.read_bytes()
    request = urllib.request.Request(url, headers={"User-Agent": "CardioIA-Fase1/1.0 academic"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
    destination.write_bytes(content)
    return content


def download_texts() -> None:
    sources = [
        (
            "https://www.gutenberg.org/ebooks/43780.txt.utf-8",
            DOCS_DIR / "texto_01_lettsomian_lectures_heart_arteries.txt",
        ),
        (
            "https://www.gutenberg.org/ebooks/3731.txt.utf-8",
            DOCS_DIR / "texto_02_disturbances_of_the_heart.txt",
        ),
    ]
    for url, destination in sources:
        content = download(url, destination)
        if len(content) < 1000:
            raise RuntimeError(f"Texto baixado parece incompleto: {url}")


def parse_header(header_text: str) -> dict[str, object]:
    lines = [line.strip() for line in header_text.splitlines() if line.strip()]
    first = lines[0].split()
    record = first[0]
    n_channels = int(first[1])
    sampling_frequency = float(first[2])
    n_samples = int(first[3]) if len(first) >= 4 else 0
    channel_lines = lines[1 : 1 + n_channels]
    leads: list[str] = []
    for index, line in enumerate(channel_lines, start=1):
        parts = line.split()
        leads.append(parts[8] if len(parts) >= 9 else f"canal_{index}")
    return {
        "record": record,
        "n_channels": n_channels,
        "sampling_frequency": sampling_frequency,
        "n_samples": n_samples,
        "leads": leads,
        "format": channel_lines[0].split()[1] if channel_lines else "unknown",
    }


def decode_212(data: bytes, n_channels: int, n_samples: int) -> list[list[int]]:
    if n_channels != 2:
        raise ValueError("O decodificador desta atividade espera registros de dois canais.")
    values: list[int] = []
    for offset in range(0, len(data) - 2, 3):
        first_byte, middle_byte, third_byte = data[offset : offset + 3]
        sample_a = first_byte | ((middle_byte & 0x0F) << 8)
        sample_b = third_byte | ((middle_byte & 0xF0) << 4)
        if sample_a >= 2048:
            sample_a -= 4096
        if sample_b >= 2048:
            sample_b -= 4096
        values.extend((sample_a, sample_b))

    channels = [[] for _ in range(n_channels)]
    expected = n_samples * n_channels if n_samples else len(values)
    values = values[:expected]
    for index, value in enumerate(values):
        channels[index % n_channels].append(value)
    return channels


def choose_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def render_ecg(signal: list[int], destination: Path, title: str, footer: str) -> None:
    width, height = 1200, 520
    image = Image.new("RGB", (width, height), "#fbfdff")
    draw = ImageDraw.Draw(image)

    plot_left, plot_top, plot_right, plot_bottom = 56, 82, width - 24, height - 48
    draw.rectangle((plot_left, plot_top, plot_right, plot_bottom), fill="#ffffff", outline="#aac2d4", width=2)
    minor_step = 12
    major_step = minor_step * 5
    for x in range(plot_left, plot_right + 1, minor_step):
        color = "#e9f0f5" if (x - plot_left) % major_step else "#d6e4ec"
        draw.line((x, plot_top, x, plot_bottom), fill=color, width=1)
    for y in range(plot_top, plot_bottom + 1, minor_step):
        color = "#e9f0f5" if (y - plot_top) % major_step else "#d6e4ec"
        draw.line((plot_left, y, plot_right, y), fill=color, width=1)

    if not signal:
        signal = [0]
    center = statistics.median(signal)
    deviations = [abs(value - center) for value in signal]
    scale = max(statistics.median(deviations) * 8.0, (max(signal) - min(signal)) / 2.0, 1.0)
    usable_height = plot_bottom - plot_top
    usable_width = plot_right - plot_left
    points: list[tuple[int, int]] = []
    for pixel_x in range(usable_width + 1):
        start = int(pixel_x * len(signal) / (usable_width + 1))
        end = max(start + 1, int((pixel_x + 1) * len(signal) / (usable_width + 1)))
        chunk = signal[start:end]
        value = sum(chunk) / len(chunk)
        normalized = clamp((value - center) / scale, -1.0, 1.0)
        pixel_y = int(plot_top + usable_height / 2 - normalized * usable_height * 0.43)
        points.append((plot_left + pixel_x, pixel_y))
    if len(points) >= 2:
        draw.line(points, fill="#087f8c", width=3, joint="curve")

    title_font = choose_font(24)
    small_font = choose_font(14)
    draw.text((plot_left, 22), title, fill="#17324d", font=title_font)
    draw.text((plot_left, height - 32), footer, fill="#4d6475", font=small_font)
    draw.text((plot_left + 8, plot_bottom + 8), "0 s", fill="#4d6475", font=small_font)
    draw.text((plot_right - 35, plot_bottom + 8), "5 s", fill="#4d6475", font=small_font)
    image.save(destination, format="PNG", optimize=True)


def generate_visual_dataset() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, object]] = []
    image_number = 1

    for record_index, record in enumerate(MITDB_RECORDS):
        header_path = RAW_DIR / f"{record}.hea"
        data_path = RAW_DIR / f"{record}.dat"
        header_bytes = download(f"{MITDB_BASE}/{record}.hea", header_path)
        data_bytes = download(f"{MITDB_BASE}/{record}.dat", data_path)
        header = parse_header(header_bytes.decode("utf-8", errors="replace"))
        if header["format"] != "212":
            raise RuntimeError(f"Formato inesperado no registro {record}: {header['format']}")
        channels = decode_212(data_bytes, int(header["n_channels"]), int(header["n_samples"]))
        n_samples = min(len(channel) for channel in channels)
        if n_samples < WINDOW_SAMPLES:
            raise RuntimeError(f"Registro {record} é menor que uma janela de {WINDOW_SECONDS}s.")

        for segment_index in range(WINDOWS_PER_RECORD):
            max_start = n_samples - WINDOW_SAMPLES
            start_sample = int(round(segment_index * max_start / (WINDOWS_PER_RECORD - 1)))
            channel_index = (segment_index + record_index) % len(channels)
            signal = channels[channel_index][start_sample : start_sample + WINDOW_SAMPLES]
            image_name = f"ecg_{image_number:04d}.png"
            image_path = IMAGE_DIR / image_name
            lead = str(header["leads"][channel_index])
            title = f"ECG | registro {record} | derivação {lead} | janela {segment_index + 1:02d}/{WINDOWS_PER_RECORD:02d}"
            footer = "Sinal público renderizado para fins acadêmicos; não é laudo diagnóstico."
            render_ecg(signal, image_path, title, footer)
            manifest_rows.append(
                {
                    "image_id": f"ECG-{image_number:04d}",
                    "file": f"imagens_ecg/{image_name}",
                    "source_dataset": "MIT-BIH Arrhythmia Database v1.0.0",
                    "source_record": record,
                    "lead": lead,
                    "segment_index": segment_index + 1,
                    "start_seconds": round(start_sample / float(header["sampling_frequency"]), 3),
                    "duration_seconds": WINDOW_SECONDS,
                    "sampling_frequency_hz": header["sampling_frequency"],
                    "source_signal_url": f"{MITDB_BASE}/{record}.dat",
                    "license": "Open Data Commons Attribution License v1.0",
                    "clinical_use": "educational_only",
                }
            )
            image_number += 1

    write_csv(
        MANIFEST_FILE,
        [
            "image_id",
            "file",
            "source_dataset",
            "source_record",
            "lead",
            "segment_index",
            "start_seconds",
            "duration_seconds",
            "sampling_frequency_hz",
            "source_signal_url",
            "license",
            "clinical_use",
        ],
        manifest_rows,
    )
    (METADATA_DIR / "dataset_visual.json").write_text(
        json.dumps(
            {
                "images": len(manifest_rows),
                "records": MITDB_RECORDS,
                "windows_per_record": WINDOWS_PER_RECORD,
                "window_seconds": WINDOW_SECONDS,
                "sampling_frequency_hz": SAMPLE_RATE_HZ,
                "derived_from": MITDB_BASE,
                "generated_on": "2026-09-01",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    print("[1/3] Gerando dataset numérico simulado...")
    generate_numeric_dataset()
    print("[2/3] Baixando textos em formato TXT...")
    download_texts()
    print("[3/3] Baixando sinais públicos e renderizando 100 imagens ECG...")
    generate_visual_dataset()
    print("Dados preparados em", ROOT)


if __name__ == "__main__":
    main()
