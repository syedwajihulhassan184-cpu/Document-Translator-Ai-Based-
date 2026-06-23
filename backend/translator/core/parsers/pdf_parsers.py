from jobs.models import ChunkStatus, Chunk



def group_words_into_lines(words, tolerence=2):
    lines = []
    current_line = []
    current_top = None

    for word in words:
        if current_top is None or (abs(word['top'] - current_top)) <= tolerence:
            current_line.append(word)
            current_top = word['top']
        else:
            lines.append(current_line)
            current_line = [word]
            current_top = word['top']

    if current_line:
        lines.append(current_line)

    return lines


def group_lines_into_blocks(lines, gap_threshold=10):
    if not lines:
        return []
    
    block = [[lines[0]]]

    for i in range(1,len(lines)):
        gap = lines[i]['top'] - lines[i-1]['bottom']
        if gap > gap_threshold:
            block.append([lines[i]])
        else:
            block[-1].append(lines[i])

    return block




def block_to_chunks(blocks, page_num, block_index) -> dict:
    chunked_blocks = {}

    left_edge = min(block['x0'] for block in blocks)
    right_edge = max(block['x1'] for block in blocks)
    top_edge = min(block['top'] for block in blocks)
    bottom_edge = max(block['bottom'] for block in blocks)

    chunked_blocks['text'] = ' '.join(block['text'] for block in blocks)


    chunked_blocks['bbox'] = {
    'x0': left_edge,
    'x1': right_edge,
    'top': top_edge,
    'bottom': bottom_edge
}



    chunked_blocks['page'] = page_num
    chunked_blocks['block_index'] = block_index

    return chunked_blocks



def extract_chunks(filepath) -> list:
    import pdfplumber
    all_chunks = []
    with pdfplumber.open(filepath) as pdf:
        pages = pdf.pages
        
        for page_idx ,page in enumerate(pages):
            lines = page.extract_text_lines()
            blocks = group_lines_into_blocks(lines)
            chunks = [block_to_chunks(block, page_num=page_idx, block_index=i) 
              for i, block in enumerate(blocks)]
            all_chunks.extend(chunks)
        
        return all_chunks
    

def save_chunks_to_db(chunks, job):
    for chunk in chunks:
        original_text = chunk['text']
        layout_metadata = chunk['bbox']
        page_start = chunk['page']
        page_end = chunk['page']
        chunk_index = chunk['block_index']
        status = ChunkStatus.PENDING

        Chunk.objects.create(
            job=job,
            chunk_index=chunk_index,
            page_start=page_start,
            page_end=page_end,
            original_text=original_text,
            status=status,
            layout_metadata=layout_metadata
        )
