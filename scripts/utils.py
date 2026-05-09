import re


def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\u4e00-\u9fff-]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    words = text.split('-')
    def capitalize_word(word):
        return word if word.isupper() else word.capitalize()
    return '-'.join(capitalize_word(word) for word in words if word)


def ask(prompt, default=None):
    if default is not None:
        raw = input(f'{prompt} [{default}]: ').strip()
        return raw if raw else default
    return input(f'{prompt}: ').strip()


def confirm(prompt, default='y'):
    default_show = 'y' if default == 'y' else 'n'
    raw = input(f'{prompt} [{default_show}]: ').strip().lower()
    return raw if raw else default


def parse_front_matter(text):
    pattern = r'^---\n(.*?)\n---\n(.*)'
    match = re.match(pattern, text, re.DOTALL)
    if not match:
        return {}, text.strip()
    meta = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip()
    return meta, match.group(2).strip()
