from pathlib import Path
import re

FILES = [
    Path("frontend/index.html"),
    Path("frontend/app.js"),
]

NON_ASCII_RUN = re.compile(r"[^\x00-\x7F]+")


def cp1252_bytes(text):
    data = bytearray()

    for ch in text:
        code = ord(ch)

        # Preserve the original byte value for C1 control characters
        # that came from incorrectly decoded Windows-1252 bytes.
        if 0x80 <= code <= 0x9F:
            data.append(code)
        else:
            try:
                data.extend(ch.encode("cp1252"))
            except UnicodeEncodeError:
                return None

    return bytes(data)


def repair_run(match):
    text = match.group(0)

    raw = cp1252_bytes(text)

    if raw is None:
        return text

    try:
        repaired = raw.decode("utf-8")
    except UnicodeDecodeError:
        return text

    before = sum(
        text.count(x)
        for x in ("â", "ð", "Â", "Ã", "Ÿ")
    )

    after = sum(
        repaired.count(x)
        for x in ("â", "ð", "Â", "Ã", "Ÿ")
    )

    if after < before:
        return repaired

    return text


for path in FILES:
    original = path.read_text(encoding="utf-8")
    repaired = NON_ASCII_RUN.sub(repair_run, original)

    if repaired != original:
        path.write_text(repaired, encoding="utf-8")
        print(f"REPAIRED: {path}")
    else:
        print(f"NO CHANGE: {path}")

print("Final mojibake repair complete.")