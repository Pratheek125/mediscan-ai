from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Canonical names used by the ML engine and UI. Aliases are deliberately broad
# because laboratory PDFs commonly split a table row across several lines.
ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hgb", "hb"],
    "WBC": ["white blood cell", "wbc", "total wbc count", "total leucocyte"],
    "RBC": ["red blood cell", "rbc"],
    "Platelets": ["platelet count", "platelets", "platelet", "plt"],
    "Hematocrit": ["hematocrit", "hct", "pcv"],
    "MCV": ["mean corpuscular volume", "mean cell volume", "mcv"],
    "MCH": ["mean corpuscular hemoglobin", "mean cellhemoglobin", "mch"],
    "MCHC": ["mean corpuscular hb concentration", "mean corpuscular hb", "mchc"],
    "RDW": ["red cell distribution width", "rdw"],
    "Neutrophils": ["neutrophils", "neutrophil"],
    "Lymphocytes": ["lymphocytes", "lymphocyte"],
    "Monocytes": ["monocytes", "monocyte"],
    "Eosinophils": ["eosinophils", "eosinophil"],
    "Basophils": ["basophils", "basophil"],
    "Fasting Glucose": ["fasting glucose", "fasting blood sugar", "fbs"],
    "Postprandial Glucose": ["postprandial glucose", "plasma glucose - pp", "pp glucose", "ppbs"],
    "HbA1c": ["hba1c", "hb a1c", "glyco hemoglobin", "glycated hemoglobin"],
    "eAG": ["eag", "estimated average glucose", "estimated avg glucose"],
    "Total Cholesterol": ["total cholesterol", "cholesterol"],
    "Triglycerides": ["triglycerides", "triglyceride"],
    "HDL": ["hdl cholesterol", "hdl"],
    "LDL": ["ldl-c", "ldl"],
    "VLDL": ["vldl"],
    "Cholesterol Ratio": ["cholesterol/hdl-c", "cholesterol/hdl ratio", "cholesterol ratio"],
    "Non HDL-C": ["non hdl-c", "non hdl"],
    "Creatinine": ["creatinine"],
    "Blood Urea": ["blood urea", "urea"],
    "Uric Acid": ["uric acid"],
    "eGFR": ["egfr", "estimated gfr"],
    "BUN": ["bun"],
    "Sodium": ["sodium"],
    "Potassium": ["potassium"],
    "Chloride": ["chloride"],
    "Bilirubin Total": ["bilirubin total", "total bilirubin"],
    "Bilirubin Direct": ["bilirubin direct", "direct bilirubin"],
    "Bilirubin Indirect": ["bilirubin indirect", "indirect bilirubin"],
    "SGOT": ["sgot", "ast", "ast (sgot)", "ast sgpt"],
    "SGPT": ["sgpt", "alt", "alt (sgpt)"],
    "ALP": ["alp", "alkaline phosphatase"],
    "Albumin": ["albumin"],
    "Globulin": ["globulin"],
    "A/G Ratio": ["albumin / globulin ratio", "a/g ratio", "ag ratio"],
    "Total Protein": ["proteins (total)", "total protein"],
    "TSH": ["tsh"],
    "T3": ["triiodothyronine (t3)", "t3"],
    "T4": ["thyroxine (t4)", "t4"],
    "Free T3": ["free t3"],
    "Free T4": ["free t4"],
    "CRP": ["c- reactive protein", "c-reactive protein", "crp"],
    "Calcium": ["adjusted calcium", "calcium"],
    "Iron": ["iron"],
    "TIBC": ["total iron binding capacity", "tibc"],
    "UIBC": ["unsaturated iron binding capacity", "uibc"],
    "Transferrin Saturation": ["transferrin saturation"],
    "Serum Transferrin": ["serum transferrin", "transferrin"],
    "Ferritin": ["ferritin"],
    "Vitamin D": ["vitamin d"],
    "Active B12": ["active - b12", "active b12", "holotranscobalamin"],
}

# Reference intervals used by the application. The original project stores
# these in CSVs; the fallback ranges below cover additional tests present in
# common reports such as the supplied 14-page report.
RANGES = {}
for f in (ROOT / "dataset" / "normal_ranges").glob("*.csv"):
    df = pd.read_csv(f)
    for _, r in df.iterrows():
        RANGES[str(r.parameter)] = (float(r["min"]), float(r["max"]), str(r.get("unit", "")))

FALLBACK_RANGES = {
    "Hematocrit": (34.0, 48.0, "%"),
    "Neutrophils": (40.0, 75.0, "%"),
    "Lymphocytes": (20.0, 45.0, "%"),
    "Monocytes": (1.0, 10.0, "%"),
    "Eosinophils": (1.0, 6.0, "%"),
    "Basophils": (0.0, 1.0, "%"),
    "HbA1c": (4.0, 5.6, "%"),
    "Postprandial Glucose": (0.0, 140.0, "mg/dL"),
    "Creatinine": (0.55, 1.02, "mg/dL"),
    "Blood Urea": (0.0, 42.8, "mg/dL"),
    "Uric Acid": (2.5, 6.2, "mg/dL"),
    "Sodium": (136.0, 145.0, "mEq/L"),
    "Potassium": (3.5, 5.1, "mEq/L"),
    "Chloride": (98.0, 107.0, "mEq/L"),
    "Bilirubin Indirect": (0.0, 0.8, "mg/dL"),
    "SGOT": (5.0, 34.0, "U/L"),
    "SGPT": (0.0, 55.0, "U/L"),
    "ALP": (46.0, 122.0, "U/L"),
    "Albumin": (3.2, 4.6, "g/dL"),
    "Globulin": (2.0, 3.5, "g/dL"),
    "A/G Ratio": (1.0, 2.5, "ratio"),
    "Total Protein": (6.4, 8.3, "g/dL"),
    "TSH": (0.5, 8.9, "µIU/mL"),
    "T3": (0.4, 1.8, "ng/mL"),
    "T4": (5.0, 10.7, "µg/dL"),
    "CRP": (0.0, 0.5, "mg/dL"),
    "Calcium": (8.4, 10.2, "mg/dL"),
    "Iron": (65.0, 175.0, "µg/dL"),
    "TIBC": (265.0, 497.0, "µg/dL"),
    "UIBC": (70.0, 310.0, "mcg/dL"),
    "Transferrin Saturation": (22.0, 55.0, "%"),
    "Serum Transferrin": (175.0, 320.0, "mg/dL"),
    "Ferritin": (22.0, 439.0, "ng/mL"),
    "Vitamin D": (30.0, 100.0, "ng/mL"),
    "Active B12": (25.1, 165.0, "pmol/L"),
    "eAG": (70.0, 126.0, "mg/dL"),
    "BUN": (0.0, 20.0, "mg/dL"),
    "Non HDL-C": (0.0, 130.0, "mg/dL"),
    "Cholesterol Ratio": (0.0, 4.5, "Ratio"),
}
for k, v in FALLBACK_RANGES.items():
    RANGES.setdefault(k, v)

# Numeric token supports values such as 12,345.6, but deliberately excludes
# numbers embedded in words/IDs and dates.
NUM_RE = re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?![A-Za-z0-9])")
RANGE_RE = re.compile(r"(?:<=|>=|</=|>/=|<|>)?\s*\d+(?:\.\d+)?\s*(?:-|–|—)\s*\d+(?:\.\d+)?|(?:<=|>=|</=|>/=|<|>)\s*\d+(?:\.\d+)?", re.I)


def _numbers(s):
    return [float(x.replace(",", "")) for x in NUM_RE.findall(s)]


def _match_alias(line, alias):
    # Short aliases need word boundaries; longer aliases can be matched as
    # phrases because OCR often inserts punctuation/extra spaces.
    if len(alias) <= 4:
        return bool(re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", line))
    return alias in line


def _has_parameter(line, canonical):
    low = line.lower()
    return any(_match_alias(low, a.lower()) for a in ALIASES[canonical])


def _range_numbers(line):
    """Return numbers that belong to an explicit reference-range expression."""
    nums = []
    for m in RANGE_RE.finditer(line):
        nums.extend(_numbers(m.group(0)))
    return nums


def _clean_candidate(value):
    # Reject obvious dates, patient IDs and long identifier-like values.
    if value >= 1900 and value <= 2100:
        return False
    if value >= 10000000:
        return False
    return True


def _find_value(lines, start_idx, canonical):
    """Find a lab result in both inline and vertically split PDF table layouts."""
    lo, hi, _ = RANGES[canonical]
    max_lookahead = min(len(lines), start_idx + 22)
    saw_range = False
    range_values = []

    for j in range(start_idx, max_lookahead):
        line = lines[j].strip()
        if not line:
            continue

        # Stop before another supported parameter begins, except when the
        # current parameter's own multi-line name is being completed.
        if j > start_idx and any(_has_parameter(line.lower(), other) for other in ALIASES if other != canonical):
            break

        nums = _numbers(line)
        if not nums:
            continue

        explicit_range = _range_numbers(line)
        if explicit_range:
            saw_range = True
            range_values.extend(explicit_range)
            # A line such as "<150" or "1 - 10" is reference information,
            # never the patient's result.
            continue

        # Inline table rows are the easiest case: parameter + result + unit + range.
        if j == start_idx and nums:
            for v in nums:
                if _clean_candidate(v):
                    return v

        # In vertical PDFs the result may appear before or after the range.
        # Prefer a numeric-only line (e.g. "13.5", "153000", "1.50").
        non_date = [v for v in nums if _clean_candidate(v)]
        if not non_date:
            continue
        stripped = re.sub(r"[^0-9.,+\-]", "", line)
        if stripped and all(ch in "0123456789.,+-" for ch in stripped):
            # If this line is the range line, it was already skipped above.
            return non_date[0]

        # Some native PDF extractors put result, unit and range on one line.
        # If the value is not part of the explicit range, use the first sensible token.
        if any(u in line.lower() for u in ["mg/dl", "g/dl", "cells", "million", "%", "ratio", "fl", "pg", "meq/l", "ng/ml", "pmol/l", "u/l", "miu", "µiu"]):
            excluded = set(range_values)
            for v in non_date:
                if v not in excluded:
                    return v

    return None


def _parse_structured_rows(text):
    """Parse coordinate-reconstructed rows emitted by ocr.engine."""
    if "__MEDISCAN_TABLE_ROWS__" not in text:
        return {}
    block = text.split("__MEDISCAN_TABLE_ROWS__", 1)[1]
    candidates = []

    for line in block.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            continue
        label, value_text, unit_text, ref_text = parts
        nums = _numbers(value_text)
        if not nums:
            continue

        low = label.lower()
        matches = []
        for canonical in ALIASES:
            if canonical not in RANGES:
                continue
            for alias in ALIASES[canonical]:
                if _match_alias(low, alias.lower()):
                    matches.append((len(alias), canonical, alias))
        if not matches:
            continue
        matches.sort(reverse=True)
        score, canonical, _ = matches[0]

        # Parse a simple numeric reference interval from the same table row.
        # This keeps the analysis aligned with the laboratory report when its
        # interval differs from the application's generic fallback.
        ref_min = ref_max = None
        range_matches = list(re.finditer(r"(\d+(?:\.\d+)?)\s*(?:-|–|—)\s*(\d+(?:\.\d+)?)", ref_text))
        if range_matches:
            ref_min = float(range_matches[0].group(1))
            ref_max = float(range_matches[0].group(2))
        else:
            m = re.search(r"(?:<=|<=|</=|<)\s*(\d+(?:\.\d+)?)", ref_text)
            if m:
                ref_min = None
                ref_max = float(m.group(1))

        candidates.append((canonical, nums[0], score, ref_min, ref_max, unit_text))

    out = {}
    scores = {}
    for canonical, value, score, ref_min, ref_max, unit_text in candidates:
        if canonical not in out or score >= scores[canonical][0]:
            out[canonical] = {
                "value": value,
                "min": ref_min,
                "max": ref_max,
                "unit": unit_text,
            }
            scores[canonical] = (score,)
    return out


def _build_result(canonical, value, ref_min=None, ref_max=None, source_unit=None):
    configured_min, configured_max, configured_unit = RANGES[canonical]
    lo = configured_min if ref_min is None else ref_min
    hi = configured_max if ref_max is None else ref_max
    unit = configured_unit or source_unit or ""
    status = "NORMAL" if lo <= value <= hi else ("LOW" if value < lo else "HIGH")
    boundary = lo if value < lo else hi
    pct = 0 if status == "NORMAL" else abs(value - boundary) / max(abs(boundary), 1e-9) * 100
    severity = "Normal" if status == "NORMAL" else ("Critical" if pct > 40 else "Moderate" if pct > 20 else "Mild")
    return {
        "Parameter": canonical,
        "Value": value,
        "Unit": unit,
        "Min": lo,
        "Max": hi,
        "Status": status,
        "Severity": severity,
        "Deviation %": round(pct, 1),
    }


def parse(text):
    """Extract supported lab results from native/OCR text and table rows."""
    results = []
    structured = _parse_structured_rows(text)
    seen = set()

    # Coordinate-reconstructed rows are the most reliable source for native
    # laboratory PDFs. They also carry the report's own reference interval.
    for canonical in ALIASES:
        item = structured.get(canonical)
        if item is None or canonical not in RANGES:
            continue
        results.append(_build_result(
            canonical,
            item["value"],
            item.get("min"),
            item.get("max"),
            item.get("unit"),
        ))
        seen.add(canonical)

    # Fallback for scanned PDFs or reports without a reconstructable table.
    lines = text.splitlines()
    for canonical in ALIASES:
        if canonical in seen or canonical not in RANGES:
            continue
        best = None
        occurrences = [i for i, line in enumerate(lines) if _has_parameter(line, canonical)]
        for idx in occurrences:
            line_nums = _numbers(lines[idx])
            range_nums = _range_numbers(lines[idx])
            candidates = [v for v in line_nums if v not in range_nums and _clean_candidate(v)]
            if candidates:
                best = candidates[0]
                continue
            for j in range(idx + 1, min(len(lines), idx + 18)):
                line = lines[j].strip()
                if not line:
                    continue
                if j > idx and any(_has_parameter(line.lower(), other) for other in ALIASES if other != canonical):
                    break
                nums = _numbers(line)
                if not nums or _range_numbers(line):
                    continue
                vals = [v for v in nums if _clean_candidate(v)]
                if not vals:
                    continue
                compact = re.sub(r"[^0-9.,+\-]", "", line)
                if compact and all(ch in "0123456789.,+-" for ch in compact):
                    best = vals[0]
                    break
        if best is not None:
            results.append(_build_result(canonical, best))
            seen.add(canonical)

    return results
