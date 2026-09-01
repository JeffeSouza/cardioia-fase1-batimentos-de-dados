import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const numericCsvPath = path.join(root, "data", "numerical", "pacientes_cardiacos_simulados.csv");
const dictionaryCsvPath = path.join(root, "metadata", "dicionario_dados.csv");
const outputDir = path.join(root, "outputs", "atividade-cap01");
const outputPath = path.join(outputDir, "cardioia_pacientes.xlsx");

const numericCsv = await fs.readFile(numericCsvPath, "utf8");
const dictionaryCsv = await fs.readFile(dictionaryCsvPath, "utf8");
const workbook = await Workbook.fromCSV(numericCsv, { sheetName: "Dados_Raw" });
const raw = workbook.worksheets.getItem("Dados_Raw");
const dictionaryBook = await Workbook.fromCSV(dictionaryCsv, { sheetName: "Dicionario" });
const dictionarySource = dictionaryBook.worksheets.getItem("Dicionario");
const dictionaryValues = dictionarySource.getUsedRange().values;

const rowCount = raw.getUsedRange().values.length;
const columnCount = raw.getUsedRange().values[0].length;
const lastColumn = String.fromCharCode("A".charCodeAt(0) + columnCount - 1);
const lastRow = rowCount;

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange(`A1:${lastColumn}1`).format = {
  fill: "#123B5D",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
raw.getRange(`A1:${lastColumn}${lastRow}`).format.font = { name: "Aptos", size: 10 };
raw.getRange(`A1:${lastColumn}1`).format.font = { name: "Aptos", size: 10, bold: true, color: "#FFFFFF" };
raw.getRange(`A2:A${lastRow}`).format.horizontalAlignment = "left";
raw.getRange(`B2:B${lastRow}`).format.numberFormat = "0";
raw.getRange(`D2:G${lastRow}`).format.numberFormat = "0";
raw.getRange(`N2:N${lastRow}`).format.numberFormat = "0.0";
raw.getRange(`O2:P${lastRow}`).format.numberFormat = "0";
raw.getRange(`V2:V${lastRow}`).format.numberFormat = "0";
raw.getRange(`A1:A${lastRow}`).format.columnWidth = 13;
raw.getRange(`B1:B${lastRow}`).format.columnWidth = 12;
raw.getRange(`C1:C${lastRow}`).format.columnWidth = 9;
raw.getRange(`D1:G${lastRow}`).format.columnWidth = 17;
raw.getRange(`H1:K${lastRow}`).format.columnWidth = 14;
raw.getRange(`L1:M${lastRow}`).format.columnWidth = 15;
raw.getRange(`N1:P${lastRow}`).format.columnWidth = 17;
raw.getRange(`Q1:U${lastRow}`).format.columnWidth = 18;
raw.getRange(`V1:V${lastRow}`).format.columnWidth = 24;
raw.getRange(`A1:${lastColumn}${lastRow}`).format.borders = {
  insideHorizontal: { style: "thin", color: "#D9E4EC" },
  bottom: { style: "thin", color: "#9DB5C6" },
};
raw.getRange(`D2:D${lastRow}`).conditionalFormats.add("cellIs", {
  operator: "greaterThanOrEqual",
  formula: 140,
  format: { fill: "#FFF1E6", font: { color: "#9A3412" } },
});
raw.getRange(`V2:V${lastRow}`).conditionalFormats.add("cellIs", {
  operator: "equal",
  formula: 1,
  format: { fill: "#FEE2E2", font: { color: "#991B1B", bold: true } },
});
raw.getRange(`V2:V${lastRow}`).conditionalFormats.add("cellIs", {
  operator: "equal",
  formula: 0,
  format: { fill: "#DCFCE7", font: { color: "#166534" } },
});
raw.tables.add(`A1:${lastColumn}${lastRow}`, true, "DadosCardioIA");

const summary = workbook.worksheets.add("Resumo");
summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["CardioIA — resumo de qualidade e exploração"]];
summary.getRange("A1:H1").format = {
  fill: "#123B5D",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
summary.getRange("A3:B9").values = [
  ["Indicador", "Valor"],
  ["Linhas no dataset", null],
  ["Casos com rótulo 1", null],
  ["Proporção do rótulo 1", null],
  ["Idade média (anos)", null],
  ["Pressão sistólica média (mmHg)", null],
  ["Colesterol médio (mg/dL)", null],
];
summary.getRange("B4:B9").formulas = [
  [`=COUNTA('Dados_Raw'!$A$2:$A$${lastRow})`],
  [`=COUNTIF('Dados_Raw'!$V$2:$V$${lastRow},1)`],
  ["=B5/B4"],
  [`=AVERAGE('Dados_Raw'!$B$2:$B$${lastRow})`],
  [`=AVERAGE('Dados_Raw'!$D$2:$D$${lastRow})`],
  [`=AVERAGE('Dados_Raw'!$F$2:$F$${lastRow})`],
];
summary.getRange("A3:B3").format = { fill: "#1C6E8C", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("A4:A9").format.font = { bold: true, color: "#17324D" };
summary.getRange("B4:B9").format = { fill: "#EEF7FA", horizontalAlignment: "right" };
summary.getRange("B6").format.numberFormat = "0.0%";
summary.getRange("B7:B9").format.numberFormat = "0.0";
summary.getRange("A3:B9").format.borders = { preset: "all", style: "thin", color: "#C8D8E2" };
summary.getRange("D3:H3").merge();
summary.getRange("D3").values = [["Interpretação e limites"]];
summary.getRange("D3:H3").format = { fill: "#1C6E8C", font: { bold: true, color: "#FFFFFF" } };
for (let row = 4; row <= 9; row += 1) {
  summary.getRange(`D${row}:H${row}`).merge();
}
summary.getRange("D4:D9").values = [
  ["A base é simulada e foi criada para testar um fluxo de dados, não para estimar risco clínico."],
  ["O rótulo foi calculado por uma regra didática e não equivale a diagnóstico."],
  ["A planilha mantém unidades no dicionário e separa dados brutos do resumo."],
  ["Atenção visual: laranja sinaliza pressão sistólica simulada >= 140 mmHg; vermelho/verde distinguem o rótulo."],
  ["Antes de qualquer modelo, revisar missingness, balanceamento, leakage e desempenho por subgrupo."],
  ["Uso permitido nesta entrega: estudo acadêmico e prototipação controlada."],
];
summary.getRange("D4:H9").format = { wrapText: true, verticalAlignment: "center", fill: "#F7FAFC", font: { color: "#334E68" } };
summary.getRange("A:A").format.columnWidth = 34;
summary.getRange("B:B").format.columnWidth = 17;
summary.getRange("C:C").format.columnWidth = 4;
summary.getRange("D:H").format.columnWidth = 19;
summary.getRange("A1:H1").format.rowHeight = 28;
summary.getRange("D4:H9").format.rowHeight = 32;

const dictionary = workbook.worksheets.add("Dicionario");
dictionary.showGridLines = false;
dictionary.getRangeByIndexes(0, 0, dictionaryValues.length, dictionaryValues[0].length).values = dictionaryValues;
dictionary.freezePanes.freezeRows(1);
dictionary.getRange("A1:E1").format = {
  fill: "#123B5D",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
dictionary.getRange(`A1:E${dictionaryValues.length}`).format.borders = {
  insideHorizontal: { style: "thin", color: "#D9E4EC" },
  bottom: { style: "thin", color: "#9DB5C6" },
};
dictionary.getRange("A:A").format.columnWidth = 31;
dictionary.getRange("B:B").format.columnWidth = 44;
dictionary.getRange("C:C").format.columnWidth = 14;
dictionary.getRange("D:D").format.columnWidth = 14;
dictionary.getRange("E:E").format.columnWidth = 50;
dictionary.getRange(`B2:E${dictionaryValues.length}`).format.wrapText = true;
dictionary.tables.add(`A1:E${dictionaryValues.length}`, true, "DicionarioCardioIA");

await fs.mkdir(outputDir, { recursive: true });
for (const sheetName of ["Resumo", "Dados_Raw", "Dicionario"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(outputDir, `preview_${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`Workbook criado: ${outputPath}`);
