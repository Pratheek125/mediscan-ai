from pathlib import Path
import re
import fitz
import cv2
import numpy as np
import pytesseract


def _group_word_rows(words, tolerance=5.0):
    rows = []
    for word in sorted(words, key=lambda w: (w[1], w[0])):
        y = word[1]
        placed = False
        for row in rows:
            if abs(row[0] - y) <= tolerance:
                row[1].append(word)
                placed = True
                break
        if not placed:
            rows.append([y, [word]])
    for row in rows:
        row[1].sort(key=lambda w: w[0])
    return rows


def _native_table_rows(page):
    """Reconstruct table rows from PDF coordinates.

    The supplied laboratory report uses a stable four-column layout:
    test name -> result -> unit -> reference range. Native text extraction
    often loses this column order, so coordinate reconstruction is added as
    a second evidence stream for the medical parser.
    """
    words = page.get_text("words")
    rows = _group_word_rows(words)
    out = []

    for i, (_, ws) in enumerate(rows):
        left = [w[4] for w in ws if w[0] < 190]
        result = [w[4] for w in ws if 190 <= w[0] < 285]
        unit = [w[4] for w in ws if 285 <= w[0] < 345]
        ref = [w[4] for w in ws if w[0] >= 345 and w[0] < 460]
        if not left or not result:
            continue

        # If the test name wraps to a second line (e.g. MCHC), include the
        # immediately following left-column text when it has no result of its own.
        label = " ".join(left)
        if i + 1 < len(rows):
            next_ws = rows[i + 1][1]
            next_left = [w[4] for w in next_ws if w[0] < 190]
            next_result = [w[4] for w in next_ws if 190 <= w[0] < 285]
            if next_left and not next_result and rows[i + 1][0] - rows[i][0] <= 14:
                label += " " + " ".join(next_left)

        # Keep only rows that look like laboratory results, not headers or patient metadata.
        result_text = " ".join(result).strip()
        if not re.search(r"\d", result_text):
            continue
        row = f"{label} | {result_text} | {' '.join(unit)} | {' '.join(ref)}"
        out.append(row)
    return out


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []
    structured = []

    for page in doc:
        native = page.get_text("text").strip()
        if len(native) > 40:
            chunks.append(native)
            structured.extend(_native_table_rows(page))
            continue

        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        chunks.append(pytesseract.image_to_string(gray, config="--oem 3 --psm 6"))

    # The parser consumes these machine-generated row records before the
    # ordinary OCR/native text. This preserves compatibility with existing code.
    if structured:
        chunks.insert(0, "__MEDISCAN_TABLE_ROWS__\n" + "\n".join(structured))

    return "\n\n".join(chunks)
