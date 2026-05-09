from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = ROOT_DIR / 'template' / 'article.html'

CATEGORIES = [
    ('silvae', '随笔 / Silvae'),
    ('commentarii', '记录 / Commentarii'),
    ('versiones', '译文 / Versiones'),
    ('archivum', '存档 / Archivum'),
]

SECTION_MAP = {
    'silvae': '随笔',
    'commentarii': '记录',
    'versiones': '译文',
    'archivum': '存档',
}

PAGE_MAP = {
    'silvae': ROOT_DIR / 'pages' / 'silvae.html',
    'commentarii': ROOT_DIR / 'pages' / 'commentarii.html',
    'versiones': ROOT_DIR / 'pages' / 'versiones.html',
    'archivum': ROOT_DIR / 'pages' / 'archivum.html',
}

ENTRY_TEMPLATE = (
    '                <li>\n'
    '                    <a\n'
    '                        href="../content/%%CATEGORY%%/%%FOLDER%%/index.html"\n'
    '                        >%%TITLE%%</a\n'
    '                    >\n'
    '                    <p class="article-date">\n'
    '                        %%DATE%%\n'
    '                    </p>\n'
    '                </li>'
)
