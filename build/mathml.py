"""LaTeX → 浏览器原生 MathML（构建时转换）。

文章发布与模板重建时，把正文中的数学定界符替换为 MathML，由浏览器原生渲染，
不再引入 KaTeX 等客户端脚本。

支持定界符：
    $$...$$ / \\[...\\]  → 块级（display="block"）
    $...$   / \\(...\\)  → 行内（display="inline"）
"""

import re
import xml.etree.ElementTree as ET

from latex2mathml.converter import convert as _latex2mathml_convert

_MATHML_NS = 'http://www.w3.org/1998/Math/MathML'
ET.register_namespace('', _MATHML_NS)

# 行内与块级定界符的统一匹配（块级在前，避免被行内规则抢先）。
MATH_DELIM_RE = re.compile(
    r'\$\$(?P<dollar_block>.+?)\$\$'
    r'|\\\[(?P<bracket_block>.+?)\\\]'
    r'|(?<!\$)\$(?!\$)(?P<dollar_inline>.+?)(?<!\$)\$(?!\$)'
    r'|\\\((?P<paren_inline>.+?)\\\)',
    re.DOTALL,
)

# 这些区域内的 $ / \[ 不应被当作数学，重建扫描时整体跳过。
_PROTECTED_HTML_RE = re.compile(
    r'<pre\b.*?</pre>'
    r'|<code\b.*?</code>'
    r'|<script\b.*?</script>'
    r'|<style\b.*?</style>'
    r'|<math\b.*?</math>',
    re.DOTALL | re.IGNORECASE,
)


# latex2mathml 输出 mathvariant，但 MathML Core（Chrome 109+）已移除该属性，
# 需在构建时改写为可渲染形式：Unicode 数学字母（拉丁/数字）或 CSS 字体样式。
# 值为 (大写基准, 小写基准, 数字基准或 None, 例外映射)。
_VARIANT_UNICODE = {
    'bold': (0x1D400, 0x1D41A, 0x1D7CE, {}),
    'italic': (0x1D434, 0x1D44E, None, {'h': 0x210E}),
    'bold-italic': (0x1D468, 0x1D482, None, {}),
    'script': (0x1D49C, 0x1D4B6, None, {
        'B': 0x212C, 'E': 0x2130, 'F': 0x2131, 'H': 0x210B, 'I': 0x2110,
        'L': 0x2112, 'M': 0x2133, 'R': 0x211B,
        'e': 0x212F, 'g': 0x210A, 'o': 0x2134,
    }),
    'bold-script': (0x1D4D0, 0x1D4EA, None, {}),
    'fraktur': (0x1D504, 0x1D51E, None, {
        'C': 0x212D, 'H': 0x210C, 'I': 0x2111, 'R': 0x211C, 'Z': 0x2128,
    }),
    'bold-fraktur': (0x1D56C, 0x1D586, None, {}),
    'double-struck': (0x1D538, 0x1D552, 0x1D7D8, {
        'C': 0x2102, 'H': 0x210D, 'N': 0x2115, 'P': 0x2119, 'Q': 0x211A,
        'R': 0x211D, 'Z': 0x2124,
    }),
    'sans-serif': (0x1D5A0, 0x1D5BA, 0x1D7E2, {}),
    'sans-serif-bold': (0x1D5D4, 0x1D5EE, 0x1D7EC, {}),
    'sans-serif-italic': (0x1D608, 0x1D622, None, {}),
    'sans-serif-bold-italic': (0x1D63C, 0x1D656, None, {}),
    'monospace': (0x1D670, 0x1D68A, 0x1D7F6, {}),
}

# 变体别名（LaTeX 字体命令的其它叫法）。
_VARIANT_ALIASES = {
    'calligraphic': 'script',
    'initial': 'script',
    'tailed': 'script',
    'looped': 'script',
    'stretched': 'script',
    'blackboard': 'double-struck',
}

# Unicode 无法覆盖（如中文）时改用的 CSS 回退样式。
_VARIANT_CSS = {
    'bold': 'font-weight: bold',
    'italic': 'font-style: italic',
    'bold-italic': 'font-weight: bold; font-style: italic',
    'sans-serif': 'font-family: sans-serif',
    'sans-serif-bold': 'font-family: sans-serif; font-weight: bold',
    'sans-serif-italic': 'font-family: sans-serif; font-style: italic',
    'sans-serif-bold-italic': 'font-family: sans-serif; font-weight: bold; font-style: italic',
    'monospace': 'font-family: monospace',
    'script': 'font-family: cursive',
}


def _map_char(char, variant):
    """把单个字符映射为该变体的 Unicode 数学字母；无对应时原样返回。"""
    spec = _VARIANT_UNICODE.get(variant)
    if not spec:
        return char
    upper, lower, digit, exceptions = spec
    if char in exceptions:
        return chr(exceptions[char])
    code = ord(char)
    if 'A' <= char <= 'Z':
        return chr(upper + code - 0x41)
    if 'a' <= char <= 'z':
        return chr(lower + code - 0x61)
    if digit is not None and '0' <= char <= '9':
        return chr(digit + code - 0x30)
    return char


def _apply_variants(mathml):
    """把 MathML 中的 mathvariant 改写为 Unicode 数学字母或 CSS 样式。

    MathML Core 浏览器（Chrome）不渲染 mathvariant，仅 normal 例外。
    """
    try:
        root = ET.fromstring(mathml)
    except ET.ParseError:
        return mathml

    for element in root.iter():
        variant = element.get('mathvariant')
        if not variant:
            continue
        variant = _VARIANT_ALIASES.get(variant, variant)

        if variant == 'normal':
            # Chrome 仍识别 normal（用于取消 <mi> 默认斜体），保留属性。
            continue

        needs_css = False
        if element.text:
            mapped_chars = []
            for char in element.text:
                mapped = _map_char(char, variant)
                # 非 ASCII 字母数字（如中文、希腊字母）无 Unicode 数学字母时退回 CSS。
                if mapped == char and char.isalnum() and not char.isascii():
                    needs_css = True
                mapped_chars.append(mapped)
            element.text = ''.join(mapped_chars)

        css = _VARIANT_CSS.get(variant)
        if css and needs_css:
            existing = element.get('style')
            element.set('style', f'{existing}; {css}' if existing else css)

        element.attrib.pop('mathvariant', None)

    return ET.tostring(root, encoding='unicode')


def _normalize_latex(tex):
    r"""把 latex2mathml 易出错的写法改写为等价稳定形式。

    - `\color{name}{...}`（两参数式）在矩阵/对齐环境内会生成畸形 MathML，
      改写为标准命令 `\textcolor{name}{...}`。
    - `aligned` 环境不会被识别，`&` 会以字面 `&` 残留在输出中；改写为
      等价的 `array{rl}`，使 `&` 正确成为表格列分隔。
    """
    tex = re.sub(r'\\color\{([^}]*)\}\{', r'\\textcolor{\1}{', tex)
    tex = tex.replace(r'\begin{aligned}', r'\begin{array}{rl}')
    tex = tex.replace(r'\end{aligned}', r'\end{array}')
    return tex


def latex_to_mathml(tex, display=False):
    """把 LaTeX 源码转换为 MathML 字符串；不支持或出错时返回 None。"""
    tex = _normalize_latex(tex)
    try:
        out = _latex2mathml_convert(tex, display='block' if display else 'inline')
    except Exception:
        return None
    # 未知宏（如 mhchem 的 \ce）不会被识别，会以字面反斜杠残留在 MathML 中，
    # 此时视为转换失败，回退为原样文本，避免输出乱码。
    if '\\' in out:
        return None
    return _apply_variants(out)


def _mathml_for_match(matched):
    """根据定界符匹配对象返回（转换后的）MathML；失败时返回原始文本。"""
    if matched.group('dollar_block') is not None:
        tex, display = matched.group('dollar_block'), True
    elif matched.group('bracket_block') is not None:
        tex, display = matched.group('bracket_block'), True
    elif matched.group('dollar_inline') is not None:
        tex, display = matched.group('dollar_inline'), False
    else:
        tex, display = matched.group('paren_inline'), False

    mathml = latex_to_mathml(tex, display)
    return mathml if mathml is not None else matched.group(0)


def convert_math_text(text):
    """把纯文本/Markdown 中的数学定界符替换为 MathML。"""
    return MATH_DELIM_RE.sub(_mathml_for_match, text)


def protect_math(text):
    """把数学定界符替换为占位符，占位符对应转换后的 MathML。

    用于 Markdown 渲染流水线：先保护数学再交给 Markdown，最后回填 MathML。
    返回 (masked_text, {placeholder: mathml})；转换失败时保留原始定界符文本。
    """
    tokens = {}

    def _save(matched):
        key = f'\x00MATH_{len(tokens)}\x00'
        tokens[key] = _mathml_for_match(matched)
        return key

    return MATH_DELIM_RE.sub(_save, text), tokens


def convert_math_html(html):
    """替换 HTML 片段中的数学定界符，跳过 code/pre/script/style 区域。

    已存在的 <math> 块会就地重新规范化（升级历史 mathvariant，保证幂等）。
    """
    result = []
    pos = 0
    for matched in _PROTECTED_HTML_RE.finditer(html):
        result.append(convert_math_text(html[pos:matched.start()]))
        segment = matched.group(0)
        if segment.lstrip()[:5].lower() == '<math':
            segment = _apply_variants(segment)
        result.append(segment)
        pos = matched.end()
    result.append(convert_math_text(html[pos:]))
    return ''.join(result)
