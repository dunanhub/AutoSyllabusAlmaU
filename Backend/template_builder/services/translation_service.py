import json
import re
from html import escape
from html.parser import HTMLParser
from dataclasses import dataclass

from django.conf import settings

from template_builder.marker_whitelist import SUPPORTED_TEMPLATE_MARKERS
from template_builder.models import SyllabusTemplate


MARKER_RE = re.compile(r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}')
PLACEHOLDER_RE = re.compile(r'(__SGS_MARKER_\d+__)')


@dataclass(frozen=True)
class ProtectedHtml:
    html: str
    placeholders: dict[str, str]


class TemplateTranslationService:
    language_names = {
        SyllabusTemplate.LANGUAGE_KZ: 'Kazakh',
        SyllabusTemplate.LANGUAGE_RU: 'Russian',
        SyllabusTemplate.LANGUAGE_EN: 'English',
    }

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')

    def translate_template(self, template: SyllabusTemplate) -> dict[str, str]:
        source = template.source_language or SyllabusTemplate.LANGUAGE_RU
        protected = self._protect_markers(template.content)
        translated = {
            SyllabusTemplate.LANGUAGE_KZ: '',
            SyllabusTemplate.LANGUAGE_RU: '',
            SyllabusTemplate.LANGUAGE_EN: '',
        }

        for language in translated:
            if language == source:
                translated[language] = template.content
            else:
                raw = self._translate_html(protected.html, source, language)
                translated[language] = self._restore_markers(raw, protected.placeholders)
            self._validate_markers(template.content, translated[language])

        return translated

    def translate_to_ru(self, html: str, source_language: str) -> str:
        return self._translate_standalone(html, source_language, SyllabusTemplate.LANGUAGE_RU)

    def translate_to_kz(self, html: str, source_language: str) -> str:
        return self._translate_standalone(html, source_language, SyllabusTemplate.LANGUAGE_KZ)

    def translate_to_en(self, html: str, source_language: str) -> str:
        return self._translate_standalone(html, source_language, SyllabusTemplate.LANGUAGE_EN)

    def _translate_standalone(self, html: str, source_language: str, target_language: str) -> str:
        protected = self._protect_markers(html)
        raw = self._translate_html(protected.html, source_language, target_language)
        translated = self._restore_markers(raw, protected.placeholders)
        self._validate_markers(html, translated)
        return translated

    def _protect_markers(self, html: str) -> ProtectedHtml:
        placeholders: dict[str, str] = {}

        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            token = f'__SGS_MARKER_{len(placeholders)}__'
            marker = f'{{{{{key}}}}}'
            placeholders[token] = marker
            return token

        return ProtectedHtml(MARKER_RE.sub(replace, html), placeholders)

    def _restore_markers(self, html: str, placeholders: dict[str, str]) -> str:
        restored = html
        for placeholder, marker in placeholders.items():
            restored = restored.replace(placeholder, marker)
        return restored

    def _validate_markers(self, source_html: str, translated_html: str) -> None:
        source_markers = sorted(MARKER_RE.findall(source_html))
        translated_markers = sorted(MARKER_RE.findall(translated_html))
        unsupported = [key for key in translated_markers if key not in SUPPORTED_TEMPLATE_MARKERS]
        if unsupported:
            raise ValueError(f'Unsupported marker after translation: {", ".join(unsupported)}')
        if source_markers != translated_markers:
            raise ValueError('Translated template does not preserve template markers.')

    def _translate_html(self, html: str, source_language: str, target_language: str) -> str:
        parser = HtmlTextPlaceholderParser()
        parser.feed(html)
        parser.close()
        translated = self._translate_text_batch(parser.texts, source_language, target_language)
        output = parser.output
        for placeholder, text in translated.items():
            output = output.replace(placeholder, escape(text, quote=False))
        return output

    def _translate_text_with_placeholders(self, text: str, source_language: str, target_language: str) -> str:
        if not text.strip():
            return text

        pieces = PLACEHOLDER_RE.split(text)
        translated: list[str] = []
        for piece in pieces:
            if not piece:
                continue
            if PLACEHOLDER_RE.fullmatch(piece):
                translated.append(piece)
            else:
                translated.append(self._translate_plain_text(piece, source_language, target_language))
        return ''.join(translated)

    def _translate_text_batch(self, texts: dict[str, str], source_language: str, target_language: str) -> dict[str, str]:
        prepared: list[dict[str, str]] = []
        passthrough: dict[str, str] = {}

        for placeholder, text in texts.items():
            leading = re.match(r'^\s*', text).group(0)
            trailing = re.search(r'\s*$', text).group(0)
            body = text[len(leading): len(text) - len(trailing) if trailing else len(text)]
            if not body or not re.search(r'[A-Za-zА-Яа-яӘәІіҢңҒғҮүҰұҚқӨөҺһ]', body):
                passthrough[placeholder] = text
                continue
            prepared.append({
                'id': placeholder,
                'leading': leading,
                'text': body,
                'trailing': trailing,
            })

        if not prepared:
            return passthrough

        translated_bodies = self._translate_json_segments(
            [{'id': item['id'], 'text': item['text']} for item in prepared],
            source_language,
            target_language,
        )
        result = dict(passthrough)
        for item in prepared:
            body = translated_bodies.get(item['id']) or item['text']
            result[item['id']] = f"{item['leading']}{body}{item['trailing']}"
        return result

    def _translate_json_segments(self, segments: list[dict[str, str]], source_language: str, target_language: str) -> dict[str, str]:
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            raise RuntimeError('GEMINI_API_KEY is not configured.')

        try:
            from google import genai
            from google.genai import types
        except ImportError as error:
            raise RuntimeError('google-genai package is not installed.') from error

        source_name = self.language_names.get(source_language, source_language)
        target_name = self.language_names.get(target_language, target_language)
        prompt = (
            f'Translate and normalize every "text" value to {target_name}. '
            f'The source hint is {source_name}, but the input may contain mixed Kazakh, Russian, and English text. '
            f'Every returned "text" value must be in {target_name}, except proper names, codes, numbers, and protected placeholders. '
            'Return only a valid JSON array. Keep each "id" exactly the same. '
            'Do not add markdown fences, comments, explanations, or extra keys. '
            'Schema: [{"id":"same id","text":"translated text"}]\n\n'
            f'{json.dumps(segments, ensure_ascii=False)}'
        )
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json'),
        )
        text = (getattr(response, 'text', '') or '').strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        if not text.startswith('['):
            start = text.find('[')
            end = text.rfind(']')
            if start != -1 and end != -1 and end > start:
                text = text[start:end + 1]
        if not text:
            return {item['id']: item['text'] for item in segments}

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            raise RuntimeError('Gemini returned invalid JSON for template translation.') from error
        if not isinstance(parsed, list):
            raise RuntimeError('Gemini translation response must be a JSON array.')

        translated: dict[str, str] = {}
        for item in parsed:
            if not isinstance(item, dict):
                continue
            segment_id = str(item.get('id', ''))
            if segment_id:
                translated[segment_id] = str(item.get('text', ''))
        return translated

    def _translate_plain_text(self, text: str, source_language: str, target_language: str) -> str:
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            raise RuntimeError('GEMINI_API_KEY is not configured.')

        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError('google-genai package is not installed.') from error

        source_name = self.language_names.get(source_language, source_language)
        target_name = self.language_names.get(target_language, target_language)
        leading = re.match(r'^\s*', text).group(0)
        trailing = re.search(r'\s*$', text).group(0)
        body = text[len(leading): len(text) - len(trailing) if trailing else len(text)]
        if not body:
            return text
        if not re.search(r'[A-Za-zА-Яа-яӘәІіҢңҒғҮүҰұҚқӨөҺһ]', body):
            return text

        prompt = (
            f'Translate this text from {source_name} to {target_name}. '
            'Return only the translated text. Do not add quotes, explanations, markdown, or formatting.\n\n'
            f'{body}'
        )
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=self.model_name, contents=prompt)
        text = getattr(response, 'text', '') or ''
        if not text:
            return text or f'{leading}{body}{trailing}'
        return f'{leading}{text.strip()}{trailing}'


class HtmlTextPlaceholderParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self.texts: dict[str, str] = {}
        self.skip_depth = 0

    @property
    def output(self) -> str:
        return ''.join(self.parts)

    def handle_starttag(self, tag, attrs):
        if self._is_marker_tag(attrs) or tag.lower() in {'script', 'style'}:
            self.skip_depth += 1
        self.parts.append(self._format_start_tag(tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self._format_start_tag(tag, attrs, close=True))

    def handle_endtag(self, tag):
        self.parts.append(f'</{tag}>')
        if self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth or not data.strip():
            self.parts.append(data)
            return
        placeholder = f'__SGS_TEXT_{len(self.texts)}__'
        self.texts[placeholder] = data
        self.parts.append(placeholder)

    def handle_entityref(self, name):
        self.parts.append(f'&{name};')

    def handle_charref(self, name):
        self.parts.append(f'&#{name};')

    def handle_comment(self, data):
        self.parts.append(f'<!--{data}-->')

    def _is_marker_tag(self, attrs) -> bool:
        return any(name == 'data-template-marker' and value == 'true' for name, value in attrs)

    def _format_start_tag(self, tag, attrs, close=False):
        attributes = ''.join(
            f' {name}' if value is None else f' {name}="{escape(str(value), quote=True)}"'
            for name, value in attrs
        )
        return f'<{tag}{attributes}{"/" if close else ""}>'
