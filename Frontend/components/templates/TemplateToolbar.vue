<script setup lang="ts">
import {
  mdiContentSaveEditOutline,
  mdiFileImagePlusOutline,
  mdiFileImportOutline,
  mdiFileUploadOutline,
  mdiFormatAlignCenter,
  mdiFormatAlignJustify,
  mdiFormatAlignLeft,
  mdiFormatAlignRight,
  mdiFormatBold,
  mdiFormatFont,
  mdiFormatHeader1,
  mdiFormatHeader2,
  mdiFormatItalic,
  mdiFormatListBulleted,
  mdiFormatListNumbered,
  mdiFormatPageBreak,
  mdiFormatSize,
  mdiFormatUnderline,
  mdiImageOutline,
  mdiImageSizeSelectLarge,
  mdiLinkOff,
  mdiLinkVariant,
  mdiTable,
  mdiTableColumnRemove,
  mdiTableColumnPlusAfter,
  mdiTableEyeOff,
  mdiTableRemove,
  mdiTableRowRemove,
  mdiTableRowPlusAfter
} from '@mdi/js'
import type { Editor } from '@tiptap/vue-3'

const props = defineProps<{
  editor: Editor | null
}>()

const IMPORT_PAGINATION_EVENT = 'template-editor:paginate-import'

const fileInput = ref<HTMLInputElement | null>(null)
const importInput = ref<HTMLInputElement | null>(null)
const linkDialog = ref(false)
const imageDialog = ref(false)
const resizeDialog = ref(false)
const linkUrl = ref('')
const imageUrl = ref('')
const imagePreview = ref('')
const imageWidth = ref('320')
const imageHeight = ref('')
const importing = ref(false)
const { show } = useAppToast()

const fontSizes = [
  { title: '10 pt', value: '10pt' },
  { title: '12 pt', value: '12pt' },
  { title: '14 pt', value: '14pt' },
  { title: '16 pt', value: '16pt' },
  { title: '18 pt', value: '18pt' },
  { title: '24 pt', value: '24pt' },
  { title: '32 pt', value: '32pt' }
]

const fontFamilies = [
  { title: 'Arial', value: 'Arial, Helvetica, sans-serif' },
  { title: 'Times New Roman', value: '"Times New Roman", Times, serif' },
  { title: 'Calibri', value: 'Calibri, Arial, sans-serif' },
  { title: 'Georgia', value: 'Georgia, serif' },
  { title: 'Verdana', value: 'Verdana, Geneva, sans-serif' },
  { title: 'Courier New', value: '"Courier New", Courier, monospace' }
]

const isInTable = computed(() => props.editor?.isActive('table') || false)
const isImageSelected = computed(() => props.editor?.isActive('image') || false)
const transparentTableActive = computed(() => props.editor?.getAttributes('table').transparent === true)

function canRun(command: () => boolean) {
  if (!props.editor) return false
  try {
    return command()
  } catch {
    return false
  }
}

function openLinkDialog() {
  if (!props.editor) return
  linkUrl.value = props.editor.getAttributes('link').href || ''
  linkDialog.value = true
}

function applyLink() {
  if (!props.editor) return
  const url = linkUrl.value.trim()
  if (!url) {
    props.editor.chain().focus().unsetLink().run()
  } else {
    props.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }
  linkDialog.value = false
}

function removeLink() {
  if (!props.editor) return
  props.editor.chain().focus().extendMarkRange('link').unsetLink().run()
  linkUrl.value = ''
  linkDialog.value = false
}

function openImageDialog() {
  imageUrl.value = ''
  imagePreview.value = ''
  imageDialog.value = true
}

function pickImage() {
  fileInput.value?.click()
}

function uploadImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    imagePreview.value = String(reader.result || '')
    imageUrl.value = imagePreview.value
    input.value = ''
  }
  reader.readAsDataURL(file)
}

function applyImage() {
  if (!props.editor) return
  const src = imageUrl.value.trim() || imagePreview.value
  if (!src) return
  props.editor.chain().focus().setImage({ src }).run()
  imageDialog.value = false
}

function openResizeDialog() {
  if (!props.editor || !isImageSelected.value) return
  const attrs = props.editor.getAttributes('image')
  imageWidth.value = String(attrs.width || '320').replace('px', '')
  imageHeight.value = String(attrs.height || '').replace('px', '')
  resizeDialog.value = true
}

function applyImageSize() {
  if (!props.editor) return
  props.editor
    .chain()
    .focus()
    .updateAttributes('image', {
      width: imageWidth.value ? String(Number.parseInt(imageWidth.value, 10)) : null,
      height: imageHeight.value ? String(Number.parseInt(imageHeight.value, 10)) : null
    })
    .run()
  resizeDialog.value = false
}

function setFontSize(value: string) {
  props.editor?.chain().focus().setMark('textStyle', { fontSize: value }).run()
}

function setFontFamily(value: string) {
  props.editor?.chain().focus().setMark('textStyle', { fontFamily: value }).run()
}

function clearFontFamily() {
  props.editor?.chain().focus().setMark('textStyle', { fontFamily: null }).removeEmptyTextStyle().run()
}

function clearFontSize() {
  props.editor?.chain().focus().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run()
}

function insertPageBreak() {
  props.editor?.chain().focus().insertContent({ type: 'pageBreak' }).run()
}

function insertTable() {
  props.editor?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

function toggleTransparentTable() {
  if (!props.editor || !isInTable.value) return
  props.editor.chain().focus().updateAttributes('table', { transparent: !transparentTableActive.value }).run()
}

function pickImportFile() {
  importInput.value?.click()
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function splitPlainTextToParagraphs(text: string) {
  const normalized = text.replace(/\s+/g, ' ').trim()
  if (normalized.length <= 260) return [normalized]

  const chunks: string[] = []
  const words = normalized.split(' ')
  let current = ''

  words.forEach((word) => {
    const next = current ? `${current} ${word}` : word
    if (next.length > 210 && current.length > 80) {
      chunks.push(current)
      current = word
    } else {
      current = next
    }
  })

  if (current) chunks.push(current)
  return chunks
}

function splitLongImportedParagraphs(html: string) {
  if (!import.meta.client) return html

  const wrapper = document.createElement('div')
  wrapper.innerHTML = html

  wrapper.querySelectorAll('p').forEach((paragraph) => {
    const hasRichChildren = paragraph.querySelector('img, table, ul, ol')
    const text = paragraph.textContent?.replace(/\s+/g, ' ').trim() || ''

    if (hasRichChildren || text.length <= 260) return

    const chunks = splitPlainTextToParagraphs(text)
    if (chunks.length < 2) return

    const fragment = document.createDocumentFragment()
    chunks.forEach((chunk) => {
      const clone = paragraph.cloneNode(false) as HTMLParagraphElement
      clone.textContent = chunk
      clone.setAttribute('data-import-split', 'true')
      fragment.appendChild(clone)
    })
    paragraph.replaceWith(fragment)
  })

  return wrapper.innerHTML
}

function normalizeImportedHtml(html: string) {
  const normalized = html
    .replace(/<body[^>]*>/i, '')
    .replace(/<\/body>/i, '')
    .replace(/<table(?![^>]*data-transparent)([^>]*)>/gi, '<table$1 data-transparent="true" class="transparent-table imported-table">')
    .replace(/<br[^>]*style="[^"]*page-break-(before|after)\s*:\s*always[^"]*"[^>]*>/gi, '<div class="page-break" data-page-break="true"></div>')
    .replace(/<p[^>]*style="[^"]*page-break-(before|after)\s*:\s*always[^"]*"[^>]*>\s*<\/p>/gi, '<div class="page-break" data-page-break="true"></div>')
    .replace(/style="([^"]*)page-break-before\s*:\s*always;?([^"]*)"/gi, 'style="$1$2" data-import-page-break-before="true"')
    .replace(/style="([^"]*)page-break-after\s*:\s*always;?([^"]*)"/gi, 'style="$1$2" data-import-page-break-after="true"')
    .replace(/<([a-z0-9]+)([^>]*)data-import-page-break-before="true"([^>]*)>/gi, '<div class="page-break" data-page-break="true"></div><$1$2$3>')
    .replace(/<\/([a-z0-9]+)><([a-z0-9]+)([^>]*)data-import-page-break-after="true"([^>]*)>/gi, '</$1><div class="page-break" data-page-break="true"></div><$2$3$4>')
    .trim()

  return splitLongImportedParagraphs(normalized)
}

async function convertDocx(file: File) {
  const mammoth = await import('mammoth')
  const buffer = await file.arrayBuffer()
  const result = await mammoth.convertToHtml(
    { arrayBuffer: buffer },
    {
      convertImage: mammoth.images.imgElement(async (image) => {
        const base64 = await image.read('base64')
        return {
          src: `data:${image.contentType};base64,${base64}`
        }
      }),
      includeDefaultStyleMap: true,
      styleMap: [
        'p[style-name="Title"] => h1:fresh',
        'p[style-name="Heading 1"] => h1:fresh',
        'p[style-name="Heading 2"] => h2:fresh',
        'p[style-name="Heading 3"] => h3:fresh'
      ]
    }
  )
  return normalizeImportedHtml(result.value)
}

async function convertPdf(file: File) {
  const pdfjs = await import('pdfjs-dist')
  pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/build/pdf.worker.mjs', import.meta.url).toString()

  const pdf = await pdfjs.getDocument({ data: new Uint8Array(await file.arrayBuffer()) }).promise
  const pages: string[] = []

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
    const page = await pdf.getPage(pageNumber)
    const textContent = await page.getTextContent()
    const lines = textContent.items
      .map((item) => ('str' in item ? item.str : ''))
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()

    pages.push(`
      <h2>Страница ${pageNumber}</h2>
      <p>${escapeHtml(lines || 'Текст на странице не распознан.')}</p>
    `)
  }

  return pages.join('<div class="page-break" data-page-break="true"></div>')
}

async function importDocument(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !props.editor) return

  importing.value = true
  try {
    const extension = file.name.split('.').pop()?.toLowerCase()
    let html = ''

    if (extension === 'docx') {
      html = await convertDocx(file)
    } else if (extension === 'pdf') {
      html = await convertPdf(file)
    } else {
      show('Поддерживаются только DOCX и PDF.', 'error')
      return
    }

    props.editor.commands.setContent(html || '<p></p>', { emitUpdate: true })
    await nextTick()
    window.dispatchEvent(new CustomEvent(IMPORT_PAGINATION_EVENT))
    show(`Файл "${file.name}" импортирован`, 'success')
  } catch (error) {
    console.error(error)
    show('Не удалось импортировать файл. Проверьте формат документа.', 'error')
  } finally {
    importing.value = false
    input.value = ''
  }
}
</script>

<template>
  <div class="toolbar">
    <v-select
      class="font-family-select"
      density="compact"
      variant="outlined"
      hide-details
      label="Шрифт"
      :items="fontFamilies"
      :prepend-inner-icon="mdiFormatFont"
      @update:model-value="setFontFamily"
    />
    <v-select
      class="font-size-select"
      density="compact"
      variant="outlined"
      hide-details
      label="Размер"
      :items="fontSizes"
      :prepend-inner-icon="mdiFormatSize"
      @update:model-value="setFontSize"
    />
    <v-btn size="small" variant="text" class="text-none" @click="clearFontFamily">Шрифт auto</v-btn>
    <v-btn size="small" variant="text" class="text-none" @click="clearFontSize">Размер auto</v-btn>
    <v-divider vertical />

    <v-tooltip text="Импорт DOCX/PDF">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFileImportOutline" :loading="importing" :disabled="!editor" @click="pickImportFile" />
      </template>
    </v-tooltip>
    <v-divider vertical />

    <v-tooltip text="Жирный">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatBold" :active="editor?.isActive('bold')" :disabled="!canRun(() => editor!.can().chain().focus().toggleBold().run())" @click="editor?.chain().focus().toggleBold().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Курсив">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatItalic" :active="editor?.isActive('italic')" :disabled="!canRun(() => editor!.can().chain().focus().toggleItalic().run())" @click="editor?.chain().focus().toggleItalic().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Подчёркивание">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatUnderline" :active="editor?.isActive('underline')" :disabled="!editor" @click="editor?.chain().focus().toggleUnderline().run()" />
      </template>
    </v-tooltip>
    <v-divider vertical />

    <v-tooltip text="Заголовок 1">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatHeader1" :active="editor?.isActive('heading', { level: 1 })" :disabled="!editor" @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Заголовок 2">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatHeader2" :active="editor?.isActive('heading', { level: 2 })" :disabled="!editor" @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Маркированный список">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatListBulleted" :active="editor?.isActive('bulletList')" :disabled="!canRun(() => editor!.can().chain().focus().toggleBulletList().run())" @click="editor?.chain().focus().toggleBulletList().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Нумерованный список">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatListNumbered" :active="editor?.isActive('orderedList')" :disabled="!canRun(() => editor!.can().chain().focus().toggleOrderedList().run())" @click="editor?.chain().focus().toggleOrderedList().run()" />
      </template>
    </v-tooltip>
    <v-divider vertical />

    <v-tooltip text="Выровнять слева">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatAlignLeft" :disabled="!editor" @click="editor?.chain().focus().setTextAlign('left').run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="По центру">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatAlignCenter" :disabled="!editor" @click="editor?.chain().focus().setTextAlign('center').run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Выровнять справа">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatAlignRight" :disabled="!editor" @click="editor?.chain().focus().setTextAlign('right').run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="По ширине">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatAlignJustify" :disabled="!editor" @click="editor?.chain().focus().setTextAlign('justify').run()" />
      </template>
    </v-tooltip>
    <v-divider vertical />

    <v-tooltip text="Ссылка">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiLinkVariant" :active="editor?.isActive('link')" :disabled="!editor" @click="openLinkDialog" />
      </template>
    </v-tooltip>
    <v-tooltip text="Изображение">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiImageOutline" :disabled="!editor" @click="openImageDialog" />
      </template>
    </v-tooltip>
    <v-tooltip text="Размер изображения">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiImageSizeSelectLarge" :disabled="!isImageSelected" @click="openResizeDialog" />
      </template>
    </v-tooltip>
    <v-tooltip text="Разрыв страницы">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiFormatPageBreak" :disabled="!editor" @click="insertPageBreak" />
      </template>
    </v-tooltip>
    <v-divider vertical />

    <v-tooltip text="Создать таблицу">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTable" :disabled="!editor" @click="insertTable" />
      </template>
    </v-tooltip>
    <v-tooltip text="Добавить строку">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableRowPlusAfter" :disabled="!isInTable" @click="editor?.chain().focus().addRowAfter().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Добавить колонку">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableColumnPlusAfter" :disabled="!isInTable" @click="editor?.chain().focus().addColumnAfter().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Удалить строку">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableRowRemove" :disabled="!isInTable" @click="editor?.chain().focus().deleteRow().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Удалить колонку">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableColumnRemove" :disabled="!isInTable" @click="editor?.chain().focus().deleteColumn().run()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Прозрачная таблица">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableEyeOff" :active="transparentTableActive" :disabled="!isInTable" @click="toggleTransparentTable" />
      </template>
    </v-tooltip>
    <v-tooltip text="Удалить таблицу">
      <template #activator="{ props: tooltipProps }">
        <v-btn v-bind="tooltipProps" size="small" variant="text" :icon="mdiTableRemove" :disabled="!isInTable" @click="editor?.chain().focus().deleteTable().run()" />
      </template>
    </v-tooltip>

    <input ref="fileInput" class="hidden-input" type="file" accept="image/*" @change="uploadImage">
    <input ref="importInput" class="hidden-input" type="file" accept=".docx,.pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf" @change="importDocument">

    <v-dialog v-model="linkDialog" max-width="520">
      <v-card class="pa-2">
        <v-card-title class="font-weight-black">Ссылка</v-card-title>
        <v-card-text>
          <v-text-field v-model="linkUrl" label="URL" placeholder="https://example.com" autofocus />
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" :prepend-icon="mdiLinkOff" @click="removeLink">Удалить ссылку</v-btn>
          <v-spacer />
          <v-btn variant="text" @click="linkDialog = false">Отмена</v-btn>
          <v-btn color="primary" :prepend-icon="mdiContentSaveEditOutline" @click="applyLink">Применить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="imageDialog" max-width="620">
      <v-card class="pa-2">
        <v-card-title class="font-weight-black">Изображение</v-card-title>
        <v-card-text class="space-y-4">
          <v-text-field v-model="imageUrl" label="URL или base64" placeholder="https://example.com/image.png" />
          <v-btn variant="tonal" :prepend-icon="mdiFileUploadOutline" class="text-none" @click="pickImage">
            Загрузить с компьютера
          </v-btn>
          <div v-if="imageUrl || imagePreview" class="image-preview">
            <img :src="imageUrl || imagePreview" alt="Preview">
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="imageDialog = false">Отмена</v-btn>
          <v-btn color="primary" :prepend-icon="mdiFileImagePlusOutline" :disabled="!(imageUrl || imagePreview)" @click="applyImage">
            Вставить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="resizeDialog" max-width="460">
      <v-card class="pa-2">
        <v-card-title class="font-weight-black">Размер изображения</v-card-title>
        <v-card-text>
          <div class="grid gap-3 sm:grid-cols-2">
            <v-text-field v-model="imageWidth" label="Ширина, px" type="number" min="40" />
            <v-text-field v-model="imageHeight" label="Высота, px" type="number" min="40" hint="Можно оставить пустым" persistent-hint />
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="resizeDialog = false">Отмена</v-btn>
          <v-btn color="primary" :prepend-icon="mdiImageSizeSelectLarge" @click="applyImageSize">
            Применить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  padding: 10px;
}
.toolbar :deep(.v-btn) {
  color: rgba(var(--v-theme-on-surface), .86);
}
.toolbar :deep(.v-btn--variant-text) {
  background: rgba(var(--v-theme-on-surface), .045);
}
.toolbar :deep(.v-btn:hover) {
  background: rgba(var(--v-theme-primary), .14);
  color: rgb(var(--v-theme-primary));
}
.toolbar :deep(.v-btn--active) {
  background: rgba(var(--v-theme-primary), .18);
  color: rgb(var(--v-theme-primary));
}
.toolbar :deep(.v-btn--disabled) {
  opacity: .42;
}
.font-size-select {
  max-width: 145px;
}
.font-family-select {
  max-width: 210px;
}
.hidden-input {
  display: none;
}
.image-preview {
  display: grid;
  max-height: 260px;
  place-items: center;
  overflow: auto;
  border: 1px dashed rgba(var(--v-border-color), .35);
  border-radius: 14px;
  padding: 12px;
}
.image-preview img {
  max-width: 100%;
  max-height: 220px;
}
</style>
