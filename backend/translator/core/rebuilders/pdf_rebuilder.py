from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from jobs.models import Chunk, ChunkStatus

# Language groups
RTL_LANGS = {'ur', 'ar', 'fa', 'he', 'ps'}
CJK_LANGS = {'zh', 'ja', 'ko'}
LTR_LANGS = {'fr', 'de', 'es', 'it', 'pt', 'nl', 'tr', 'en'}

# Font paths
FONT_RTL = '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf'
FONT_LTR = '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'

# Register fonts
pdfmetrics.registerFont(TTFont('NotoArabic', FONT_RTL))
pdfmetrics.registerFont(TTFont('NotoSans', FONT_LTR))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))


def _get_font(target_lang):
    if target_lang in RTL_LANGS:
        return 'NotoArabic'
    elif target_lang in CJK_LANGS:
        return 'STSong-Light'
    else:
        return 'NotoSans'


def _prepare_text(text, target_lang):
    if not text or not text.strip():
        return None
    if target_lang in RTL_LANGS:
        reshaped = reshape(text)
        return get_display(reshaped)
    return text


def _draw_chunk(c, chunk, page_height, target_lang):
    text = _prepare_text(chunk.translated_text, target_lang)
    if not text:
        return

    bbox = chunk.layout_metadata
    x0 = bbox.get('x0', 0)
    x1 = bbox.get('x1', 500)
    bottom = bbox.get('bottom', 0)

    reportlab_y = page_height - bottom
    available_width = x1 - x0
    font_name = _get_font(target_lang)

    # Start at font size 12, scale down if text overflows bbox width
    font_size = 12
    c.setFont(font_name, font_size)
    text_width = c.stringWidth(text, font_name, font_size)

    if text_width > available_width and available_width > 0:
        font_size = max(6, int(font_size * available_width / text_width))
        c.setFont(font_name, font_size)

    if target_lang in RTL_LANGS:
        c.drawRightString(x1, reportlab_y, text)
    else:
        c.drawString(x0, reportlab_y, text)


def rebuild_pdf(job, output_path):
    """
    Rebuild translated PDF supporting:
    RTL:  Urdu, Arabic, Farsi, Hebrew, Pashto
    CJK:  Chinese, Japanese, Korean
    LTR:  French, German, Spanish, Italian, Portuguese, Dutch, Turkish, English
    """
    target_lang = job.target_lang

    chunks = Chunk.objects.filter(
        job=job, status=ChunkStatus.DONE
    ).order_by('page_start', 'chunk_index')

    chunk_group = {}
    for chunk in chunks:
        page = chunk.page_start
        if page not in chunk_group:
            chunk_group[page] = []
        chunk_group[page].append(chunk)

    if not chunk_group:
        raise ValueError(f"No DONE chunks found for job {job.id}")

    c = Canvas(output_path, pagesize=A4)
    page_width, page_height = A4

    for page_num in sorted(chunk_group.keys()):
        for chunk in chunk_group[page_num]:
            try:
                _draw_chunk(c, chunk, page_height, target_lang)
            except Exception as e:
                print(f"Skipping chunk {chunk.id} on page {page_num}: {e}")
        c.showPage()

    c.save()
    job.output_file_path = output_path
    job.save()