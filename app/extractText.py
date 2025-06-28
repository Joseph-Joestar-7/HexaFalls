import cv2
import numpy as np
import pytesseract
from symspellpy import SymSpell, Verbosity
import pkg_resources
import fitz  # PyMuPDF
import os

def render_pdf_to_images(pdf_path, zoom=2.0, rotation=0):
    """
    Render each page of a scanned PDF to a list of OpenCV BGR images.
    """
    doc = fitz.open(pdf_path)
    imgs = []
    mat = fitz.Matrix(zoom, zoom).prerotate(rotation)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8)
        img = arr.reshape(pix.height, pix.width, pix.n)
        # Convert to BGR if needed
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        imgs.append(img)
    return imgs

def preprocess_image(
    img,
    method='minimal',  # 'minimal', 'threshold', 'clahe'
    deskew=False,
    bilateral_ksize=9,
    adaptive_block=15,
    adaptive_C=3,
    clahe_clip=2.0,
    clahe_tile=(8,8)
):
    """
    Enhance and clean image for OCR. Methods:
      - minimal: grayscale + bilateral filter
      - threshold: adaptive threshold
      - clahe: apply CLAHE on L channel
    Deskew can be toggled on/off.
    """
    # Convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Choose method
    if method == 'minimal':
        proc = cv2.bilateralFilter(gray, bilateral_ksize, 75, 75)
    elif method == 'threshold':
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        proc = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, adaptive_block, adaptive_C
        )
    elif method == 'clahe':
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_tile)
        cl = clahe.apply(l)
        lab = cv2.merge((cl, a, b))
        proc = cv2.cvtColor(lab, cv2.COLOR_LAB2GRAY)
    else:
        proc = gray.copy()

    # Optional deskew
    if deskew:
        coords = np.column_stack(np.where(proc > 0))
        if coords.size:
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            (h, w) = proc.shape
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            proc = cv2.warpAffine(proc, M, (w, h), flags=cv2.INTER_CUBIC)
    return proc

# ----------------------
# 3. OCR WITH TESSERACT
# ----------------------
def ocr_image(img, psm=3, lang='eng'):  # img should be gray
    config = f"--oem 3 --psm {psm}"
    return pytesseract.image_to_string(img, lang=lang, config=config)

# ----------------------
# 4. SPELL-CORRECTION
# ----------------------
def load_symspell(max_edit_distance=2, prefix_length=7):
    sym = SymSpell(max_dictionary_edit_distance=max_edit_distance, prefix_length=prefix_length)
    dict_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
    sym.load_dictionary(dict_path, term_index=0, count_index=1)
    return sym


def correct_spelling_symspell(text, symspell, max_cost=2):
    corrected = []
    for w in text.split():
        sugg = symspell.lookup(w, Verbosity.CLOSEST, max_edit_distance=max_cost)
        corrected.append(sugg[0].term if sugg else w)
    return ' '.join(corrected)

# ----------------------
# 5. DOMAIN FILTERING
# ----------------------
def load_domain_vocab(vocab_path='domain_terms.txt'):
    if os.path.isfile(vocab_path):
        return set(line.strip().lower() for line in open(vocab_path, encoding='utf-8') if line.strip())
    return None

def filter_domain(text, vocab):
    if not vocab:
        return text
    return ' '.join(w for w in text.split() if w.lower() in vocab)

# ----------------------
# USAGE EXAMPLE
# ----------------------
if __name__ == '__main__':
    pdf = 'selina-class-10-physics-chapter-3-machines.pdf'
    pages = render_pdf_to_images(pdf, zoom=3.0)
    sym = load_symspell()
    vocab = load_domain_vocab()

    all_texts = []
    for i, pg in enumerate(pages, 1):
        # minimal preprocessing
        proc = preprocess_image(pg, method='minimal', deskew=False)

        # OCR and corrections
        raw = ocr_image(proc, psm=3)
        corrected = correct_spelling_symspell(raw, sym)
        filtered = filter_domain(corrected, vocab)

        # Append with page breaks
        all_texts.append(f" --- Page {i} ---")
        all_texts.append(filtered)

        print(f"Processed page {i}, chars: {len(filtered)}")

    # Write all pages into one combined file
    with open('chapter03.txt', 'w', encoding='utf-8') as out:
        out.write(''.join(all_texts))

    print("All pages saved to combined_output.txt")
