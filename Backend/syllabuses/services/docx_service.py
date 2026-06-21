import base64
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


DATA_IMAGE_RE = re.compile(
    r'(<img\b[^>]*?\bsrc=["\'])'
    r'(data:(image/([a-zA-Z0-9.+-]+));base64,([^"\']+))'
    r'(["\'][^>]*>)',
    re.IGNORECASE,
)


def html_to_docx_bytes(source_html: str) -> bytes:
    """Convert styled HTML to editable DOCX using headless LibreOffice."""
    if not shutil.which('soffice'):
        raise RuntimeError('LibreOffice soffice is not installed in the backend container')

    with tempfile.TemporaryDirectory(prefix='syllabus_docx_') as temp_dir:
        workdir = Path(temp_dir)
        assets_dir = workdir / 'assets'
        profile_dir = workdir / 'libreoffice-profile'
        assets_dir.mkdir()
        profile_dir.mkdir()

        html_path = workdir / 'syllabus.html'
        docx_path = workdir / 'syllabus.docx'
        html_path.write_text(_prepare_html(source_html or '', assets_dir), encoding='utf-8')

        command = [
            'soffice',
            '--headless',
            '--nologo',
            '--nodefault',
            '--nofirststartwizard',
            '--nolockcheck',
            f'-env:UserInstallation={profile_dir.as_uri()}',
            '--infilter=HTML (StarWriter)',
            '--convert-to',
            'docx:Office Open XML Text',
            '--outdir',
            str(workdir),
            str(html_path),
        ]
        result = subprocess.run(
            command,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        if result.returncode != 0 or not docx_path.exists():
            output = '\n'.join(part for part in [result.stdout, result.stderr] if part).strip()
            raise RuntimeError(f'LibreOffice DOCX conversion failed: {output or "unknown error"}')

        return docx_path.read_bytes()


def _prepare_html(source_html: str, assets_dir: Path) -> str:
    html = _extract_data_images(source_html, assets_dir)
    if '<html' in html[:500].lower():
        return html
    return f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
</head>
<body>{html}</body>
</html>'''


def _extract_data_images(source_html: str, assets_dir: Path) -> str:
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        prefix, _data_uri, _mime, subtype, payload, suffix = match.groups()
        try:
            image_bytes = base64.b64decode(re.sub(r'\s+', '', payload), validate=False)
        except Exception:
            return match.group(0)

        counter += 1
        extension = _image_extension(subtype)
        image_path = assets_dir / f'image_{counter}.{extension}'
        image_path.write_bytes(image_bytes)
        return f'{prefix}{image_path.as_uri()}{suffix}'

    return DATA_IMAGE_RE.sub(replace, source_html)


def _image_extension(subtype: str) -> str:
    subtype = (subtype or '').lower()
    if subtype in {'jpeg', 'pjpeg'}:
        return 'jpg'
    if subtype == 'svg+xml':
        return 'svg'
    if subtype in {'png', 'jpg', 'gif', 'webp', 'bmp'}:
        return subtype
    return 'png'
