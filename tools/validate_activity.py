"""Valida os entregáveis locais da atividade CardioIA."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "numerical" / "pacientes_cardiacos_simulados.csv"
DICT_PATH = ROOT / "metadata" / "dicionario_dados.csv"
MANIFEST_PATH = ROOT / "data" / "visual" / "manifest_ecg.csv"
IMAGE_DIR = ROOT / "data" / "visual" / "imagens_ecg"
XLSX_PATH = ROOT / "outputs" / "atividade-cap01" / "cardioia_pacientes.xlsx"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        if not CSV_PATH.exists():
            fail("CSV numérico não encontrado")
        with CSV_PATH.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fields = reader.fieldnames or []
        if len(rows) < 100:
            fail(f"CSV possui apenas {len(rows)} linhas; mínimo é 100")
        required = {
            "idade_anos",
            "sexo",
            "pressao_sistolica_mmhg",
            "colesterol_total_mg_dl",
            "historico_doenca_cardiaca",
            "sintoma_dor_toracica",
            "frequencia_cardiaca_repouso_bpm",
            "rotulo_risco_cardiovascular_simulado",
        }
        missing = required.difference(fields)
        if missing:
            fail(f"Colunas obrigatórias ausentes: {sorted(missing)}")
        ids = [row["id_caso"] for row in rows]
        if len(set(ids)) != len(ids):
            fail("Há ids_caso duplicados")
        labels = {row["rotulo_risco_cardiovascular_simulado"] for row in rows}
        if labels != {"0", "1"}:
            fail(f"Rótulo simulado não possui as duas classes: {sorted(labels)}")
        for row in rows:
            age = int(row["idade_anos"])
            systolic = int(row["pressao_sistolica_mmhg"])
            diastolic = int(row["pressao_diastolica_mmhg"])
            if not 18 <= age <= 88:
                fail(f"Idade fora da faixa didática: {row['id_caso']}")
            if not 90 <= systolic <= 220 or not 55 <= diastolic <= 125 or diastolic >= systolic:
                fail(f"Pressão inválida: {row['id_caso']}")
        print(json.dumps({"numeric_rows": len(rows), "numeric_columns": len(fields), "labels": sorted(labels)}, ensure_ascii=False))
    except (AssertionError, KeyError, ValueError) as exc:
        errors.append(str(exc))

    try:
        if not DICT_PATH.exists():
            fail("Dicionário de dados não encontrado")
        with DICT_PATH.open(encoding="utf-8", newline="") as handle:
            dictionary_rows = list(csv.DictReader(handle))
        if len(dictionary_rows) < 20:
            fail("Dicionário de dados está incompleto")
        print(json.dumps({"dictionary_rows": len(dictionary_rows)}, ensure_ascii=False))
    except (AssertionError, csv.Error) as exc:
        errors.append(str(exc))

    text_files = sorted((ROOT / "docs").glob("*.txt"))
    if len(text_files) < 2:
        errors.append(f"Há apenas {len(text_files)} arquivos .txt em docs; mínimo é 2")
    empty_texts = [path.name for path in text_files if path.stat().st_size < 500]
    if empty_texts:
        errors.append(f"Textos muito pequenos: {empty_texts}")
    print(json.dumps({"text_files": len(text_files), "text_names": [path.name for path in text_files]}, ensure_ascii=False))

    image_files = sorted(IMAGE_DIR.glob("*.png"))
    if len(image_files) < 100:
        errors.append(f"Há apenas {len(image_files)} PNGs; mínimo é 100")
    if Image is not None:
        for image_path in image_files:
            try:
                with Image.open(image_path) as image:
                    if image.size != (1200, 520):
                        errors.append(f"Dimensão inesperada em {image_path.name}: {image.size}")
                    image.verify()
            except Exception as exc:  # pragma: no cover - diagnóstico de arquivo
                errors.append(f"PNG inválido {image_path.name}: {exc}")
    else:
        warnings.append("Pillow não está disponível; dimensões PNG não foram inspecionadas")

    try:
        with MANIFEST_PATH.open(encoding="utf-8", newline="") as handle:
            manifest_rows = list(csv.DictReader(handle))
        if len(manifest_rows) != len(image_files):
            errors.append(f"Manifest possui {len(manifest_rows)} linhas e há {len(image_files)} imagens")
        manifest_files = {row["file"] for row in manifest_rows}
        actual_files = {f"imagens_ecg/{path.name}" for path in image_files}
        if manifest_files != actual_files:
            errors.append("Manifest e diretório de imagens não correspondem")
        print(json.dumps({"image_files": len(image_files), "manifest_rows": len(manifest_rows)}, ensure_ascii=False))
    except (FileNotFoundError, KeyError, csv.Error) as exc:
        errors.append(f"Manifest visual inválido: {exc}")

    if not XLSX_PATH.exists() or XLSX_PATH.stat().st_size < 10_000:
        errors.append("Workbook XLSX não encontrado ou muito pequeno")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "PREENCHER_COM_LINK_PUBLICO" in readme:
        warnings.append("Ainda existem placeholders de links públicos no README")

    if errors:
        print("\nERROS:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("\nVALIDAÇÃO OK")
    if warnings:
        print("AVISOS:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
