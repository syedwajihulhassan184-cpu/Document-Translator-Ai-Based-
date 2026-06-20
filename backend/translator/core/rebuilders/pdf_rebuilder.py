from reportlab.pdfgen.canvas import Canvas
from jobs.models import Chunk, TranslationJob, ChunkStatus
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from arabic_reshaper import reshape
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display


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

    for page_num, page_chunks in chunk_group.items():
            for chunk in page_chunks:
                reportlab_y = page_height - chunk.layout_metadata['bottom']
                reportlab_x = chunk.layout_metadata['x0']
                reshaped = reshape(chunk.translated_text)
                bidi_text = get_display(reshaped)
                c.setFont('NotoArabic', 12)
                
                c.drawString(reportlab_x, reportlab_y, bidi_text)
            c.showPage()
    c.save()
    job.output_file_path = output_path
    job.save()