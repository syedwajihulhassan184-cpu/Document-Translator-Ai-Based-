from jobs.models import Chunk, TranslationJob, ChunkStatus
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

RTL_LANGS = ['ur', 'ar', 'fa', 'he']

def rebuild_pdf(job, output_path):
    chunks = Chunk.objects.filter(
        job=job, status=ChunkStatus.DONE
    ).order_by('page_start', 'chunk_index')
    
    chunk_group = {}
    for chunk in chunks:
        page = chunk.page_start
        if page not in chunk_group:
            chunk_group[page] = []
        chunk_group[page].append(chunk)

    c = Canvas(output_path, pagesize=A4)
    page_width, page_height = A4

    pdfmetrics.registerFont(TTFont('NotoArabic', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('NotoSans', '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'))

    is_rtl = job.target_lang in RTL_LANGS

    for page_num, page_chunks in chunk_group.items():
        for chunk in page_chunks:
            reportlab_y = page_height - chunk.layout_metadata['bottom']
            reportlab_x = chunk.layout_metadata['x0']

            if is_rtl:
                reshaped = reshape(chunk.translated_text)
                text = get_display(reshaped)
                c.setFont('NotoArabic', 12)
            else:
                text = chunk.translated_text
                c.setFont('NotoSans', 12)

            c.drawString(reportlab_x, reportlab_y, text)
        c.showPage()

    c.save()
    job.output_file_path = output_path
    job.save()