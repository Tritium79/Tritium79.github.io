"""Generate site-wide LXGW Bright subsets (Light 300 全站 / Medium 700 粗体-only) from rendered HTML pages."""

from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import re

from config import ROOT_DIR


FONT_DIR = ROOT_DIR / 'assets' / 'fonts' / 'lxgw'
SUBSET_CSS = FONT_DIR / 'subset.css'
SUBSET_FAMILY = 'LXGW Bright Subset'
_FONT_FACES = [
    {
        'source': ROOT_DIR / 'assets' / 'fonts' / 'LXGWBright-Light.ttf',
        'weight': 300,
        'prefix': 'subset-',
        'bold_only': False,
    },
    {
        'source': ROOT_DIR / 'assets' / 'fonts' / 'LXGWBright-Medium.ttf',
        'weight': 700,
        'prefix': 'subset-medium-',
        'bold_only': True,
    },
]
_IGNORED_TAGS = {'script', 'style', 'template'}
_VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
_TEXT_ATTRIBUTES = {'alt', 'aria-label', 'placeholder', 'title', 'value'}
_BOLD_TAGS = {'b', 'strong', 'dt', 'th'}
_BOLD_CLASSES = {'link-list', 'callout-title', 'footnote-ref'}
_CSS_CONTENT_RE = re.compile(r'(?<![-\w])content\s*:\s*(["\'])(.*?)\1', re.DOTALL)


class _VisibleTextParser(HTMLParser):
    """Collect rendered text and text-like attributes with bold-context flags."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._ignored_depth = 0
        self._bold_stack = []

    def _is_bold_element(self, tag, attrs):
        if tag in _BOLD_TAGS:
            return True
        for name, value in attrs:
            if name == 'class' and value and _BOLD_CLASSES & set(value.split()):
                return True
        return False

    def handle_starttag(self, tag, attrs):
        if tag in _IGNORED_TAGS:
            self._ignored_depth += 1
            return
        bold = self._is_bold_element(tag, attrs)
        in_bold = any(self._bold_stack) or bold
        if tag not in _VOID_TAGS:
            self._bold_stack.append(bold)
        if self._ignored_depth:
            return
        for name, value in attrs:
            if name in _TEXT_ATTRIBUTES and value:
                self.parts.append((value, in_bold))

    def handle_startendtag(self, tag, attrs):
        if self._ignored_depth or tag in _IGNORED_TAGS:
            return
        in_bold = any(self._bold_stack)
        for name, value in attrs:
            if name in _TEXT_ATTRIBUTES and value:
                self.parts.append((value, in_bold))

    def handle_endtag(self, tag):
        if self._bold_stack:
            self._bold_stack.pop()
        if tag in _IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data):
        if not self._ignored_depth:
            self.parts.append((data, any(self._bold_stack)))


def _site_html_files():
    paths = sorted(ROOT_DIR.glob('*.html'))
    paths.extend(sorted((ROOT_DIR / 'pages').glob('*.html')))
    paths.extend(sorted((ROOT_DIR / 'content').glob('**/index.html')))
    return [path for path in paths if path.is_file()]


def _site_css_files():
    paths = [ROOT_DIR / 'style.css']
    paths.extend(sorted((ROOT_DIR / 'assets' / 'css').glob('**/*.css')))
    return [path for path in paths if path.is_file()]


def _keep_character(character):
    codepoint = ord(character)
    return codepoint >= 0x20 or character in ('\u00a0', '\u200b', '\u200c', '\u200d')


def _parse_site_text():
    """Yield (text, is_bold) tuples from all site HTML pages."""
    for path in _site_html_files():
        parser = _VisibleTextParser()
        parser.feed(path.read_text(encoding='utf-8'))
        parser.close()
        yield from parser.parts


def collect_site_chars():
    """Return a deterministic, de-duplicated set of characters used by the site."""
    characters = set()
    for text, _ in _parse_site_text():
        characters.update(character for character in text if _keep_character(character))
    for path in _site_css_files():
        css = path.read_text(encoding='utf-8')
        for match in _CSS_CONTENT_RE.finditer(css):
            characters.update(character for character in match.group(2) if _keep_character(character))
    return ''.join(sorted(characters))


def collect_bold_chars():
    """Return a deterministic, de-duplicated set of characters appearing in bold text."""
    characters = set()
    for text, is_bold in _parse_site_text():
        if is_bold:
            characters.update(character for character in text if _keep_character(character))
    return ''.join(sorted(characters))


def _source_signature(chars, source_path):
    digest = sha256(chars.encode('utf-8'))
    with source_path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()[:12]


def _unicode_range(chars):
    codepoints = sorted({ord(character) for character in chars})
    ranges = []
    start = previous = codepoints[0]
    for codepoint in codepoints[1:]:
        if codepoint == previous + 1:
            previous = codepoint
            continue
        ranges.append((start, previous))
        start = previous = codepoint
    ranges.append((start, previous))

    formatted = []
    for start, end in ranges:
        if start == end:
            formatted.append(f'U+{start:04X}')
        else:
            formatted.append(f'U+{start:04X}-{end:04X}')
    return ','.join(formatted)


def _write_subset_font(chars, source_path, output_path):
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise RuntimeError(
            '缺少 fonttools 或 brotli，请先运行: '
            'build/venv/bin/pip install -r build/requirements.txt'
        ) from exc

    options = subset.Options()
    options.flavor = 'woff2'
    options.hinting = False
    options.layout_features = ['*']

    temporary_path = output_path.with_name(output_path.name + '.tmp')
    if temporary_path.exists():
        temporary_path.unlink()

    font = TTFont(str(source_path))
    try:
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=chars)
        subsetter.subset(font)
        font.flavor = 'woff2'
        font.save(str(temporary_path))
    finally:
        font.close()

    temporary_path.replace(output_path)


def _font_face_css(chars, source_name, filename, family, weight, signature):
    return f'''/* Source: assets/fonts/{source_name}; characters: {len(chars)}; signature: {signature} */
@font-face {{
    font-family: "{family}";
    src: url("./{filename}") format("woff2");
    font-weight: {weight};
    font-style: normal;
    font-display: block;
    unicode-range: {_unicode_range(chars)};
}}
'''


def _write_subset_css(faces):
    css = '/* Generated by build/font_subset.py */\n'
    for face in faces:
        css += _font_face_css(
            face['chars'],
            face['source'].name,
            face['filename'],
            SUBSET_FAMILY,
            face['weight'],
            face['signature'],
        )
    temporary_path = SUBSET_CSS.with_name(SUBSET_CSS.name + '.tmp')
    temporary_path.write_text(css, encoding='utf-8')
    temporary_path.replace(SUBSET_CSS)


def _existing_subset_matches(filename):
    if not SUBSET_CSS.exists() or not (FONT_DIR / filename).exists():
        return False
    return filename in SUBSET_CSS.read_text(encoding='utf-8')


def run_font_subset(force=False):
    """Update the site-wide subsets (Light 300 全站 / Medium 700 粗体-only) when the collected characters change."""
    chars = collect_site_chars()
    if not chars:
        raise RuntimeError('未从全站 HTML 收集到可用字符，已取消字体子集生成')
    bold_chars = collect_bold_chars()

    faces = []
    changed = False
    for face in _FONT_FACES:
        if not face['source'].exists():
            raise FileNotFoundError(f'字体源文件不存在: {face["source"]}')

        face_chars = bold_chars if face['bold_only'] else chars
        if not face_chars:
            print(f"  {face['source'].name}: 未收集到粗体字符，跳过")
            continue

        signature = _source_signature(face_chars, face['source'])
        filename = f"{face['prefix']}{signature}.woff2"
        if force or not _existing_subset_matches(filename):
            FONT_DIR.mkdir(parents=True, exist_ok=True)
            _write_subset_font(face_chars, face['source'], FONT_DIR / filename)
            label = '粗体字符' if face['bold_only'] else '全站字符'
            print(f"  {face['source'].name}: 子集已生成 {filename}（{label}: {len(face_chars)} 个）")
            changed = True
        else:
            label = '粗体字符' if face['bold_only'] else '全站字符'
            print(f"  {face['source'].name}: 子集无变化，跳过（{label}: {len(face_chars)} 个）")

        faces.append({
            'filename': filename,
            'signature': signature,
            'weight': face['weight'],
            'source': face['source'],
            'chars': face_chars,
        })

    if changed or force:
        _write_subset_css(faces)

    for old_path in FONT_DIR.glob('subset-*.woff2'):
        current = [face['filename'] for face in faces]
        if old_path.name not in current:
            old_path.unlink()

    return changed
