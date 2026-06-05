from io import BytesIO

from pypdf import PdfReader


def parse_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    texts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)

    return "\n".join(texts)


def parse_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def parse_file(filename: str, content: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return parse_pdf(content)

    elif filename.endswith(".txt"):
        return parse_txt(content)

    else:
        raise ValueError("暂不支持该文件类型")