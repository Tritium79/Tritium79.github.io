from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = ROOT_DIR / 'archetypes' / 'article.html'

CATEGORIES = [
    ('sylvae', '随笔 / Sylvae'),
    ('commentarii', '记录 / Commentarii'),
    ('interpretationes', '译文 / Interpretationes'),
    ('tabularium', '存档 / Tabularium'),
]

SECTION_MAP = {
    'sylvae': '随笔',
    'commentarii': '记录',
    'interpretationes': '译文',
    'tabularium': '存档',
}

PAGE_MAP = {
    'sylvae': ROOT_DIR / 'pages' / 'sylvae.html',
    'commentarii': ROOT_DIR / 'pages' / 'commentarii.html',
    'interpretationes': ROOT_DIR / 'pages' / 'interpretationes.html',
    'tabularium': ROOT_DIR / 'pages' / 'tabularium.html',
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
