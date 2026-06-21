<script setup lang="ts">
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { Extension, Node } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import TextAlign from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import Placeholder from '@tiptap/extension-placeholder'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TemplateToolbar from '~/components/templates/TemplateToolbar.vue'
import { TEMPLATE_MARKER_GROUPS, TEMPLATE_MARKERS, type TemplateMarkerDefinition } from '~/constants/templateMarkers'
import { createTemplateMarkerHtml, extractTemplateMarkers } from '~/utils/templateMarkers'

const TEMPLATE_MARKER_DRAG_MIME = 'application/x-syllabus-template-marker'

const props = defineProps<{
  modelValue: string
  title?: string
  description?: string
  sourceLanguage?: 'kz' | 'ru' | 'en'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:title': [value: string]
  'update:description': [value: string]
  'update:sourceLanguage': [value: 'kz' | 'ru' | 'en']
}>()

const A4_PAGE_HEIGHT = 1123
const A4_CONTENT_HEIGHT = 995
const A4_PAGE_GAP = 28
const IMPORT_PAGINATION_EVENT = 'template-editor:paginate-import'

const editorStage = ref<HTMLElement | null>(null)
const pageCount = ref(1)
const currentPage = ref(1)
const descriptionDialog = ref(false)
const draftDescription = ref(props.description || '')
const usedMarkerKeys = ref<Set<string>>(new Set())
const languageOptions = [
  { title: 'Русский', value: 'ru' },
  { title: 'Қазақша', value: 'kz' },
  { title: 'English', value: 'en' }
]
let paginationFrame = 0

const FontSize = Extension.create({
  name: 'fontSize',
  addGlobalAttributes() {
    return [
      {
        types: ['textStyle'],
        attributes: {
          fontSize: {
            default: null,
            parseHTML: element => element.style.fontSize || null,
            renderHTML: (attributes) => {
              if (!attributes.fontSize) return {}
              return { style: `font-size: ${attributes.fontSize}` }
            }
          }
        }
      }
    ]
  }
})

const FontFamily = Extension.create({
  name: 'fontFamily',
  addGlobalAttributes() {
    return [
      {
        types: ['textStyle'],
        attributes: {
          fontFamily: {
            default: null,
            parseHTML: element => element.style.fontFamily?.replace(/['"]/g, '') || null,
            renderHTML: (attributes) => {
              if (!attributes.fontFamily) return {}
              return { style: `font-family: ${attributes.fontFamily}` }
            }
          }
        }
      }
    ]
  }
})

const PageBreak = Node.create({
  name: 'pageBreak',
  group: 'block',
  atom: true,
  selectable: true,

  addAttributes() {
    return {
      auto: {
        default: false,
        parseHTML: element => element.getAttribute('data-auto-page-break') === 'true',
        renderHTML: (attributes) => {
          if (!attributes.auto) return {}
          return { 'data-auto-page-break': 'true' }
        }
      }
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-page-break="true"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', { ...HTMLAttributes, class: 'page-break', 'data-page-break': 'true' }]
  }
})

const TemplateMarker = Node.create({
  name: 'templateMarker',
  group: 'inline',
  inline: true,
  atom: true,
  selectable: true,
  draggable: true,

  addAttributes() {
    return {
      markerId: {
        default: null,
        parseHTML: element => element.getAttribute('data-marker-id'),
        renderHTML: attributes => attributes.markerId ? { 'data-marker-id': attributes.markerId } : {}
      },
      markerKey: {
        default: '',
        parseHTML: element => element.getAttribute('data-marker-key') || '',
        renderHTML: attributes => ({ 'data-marker-key': attributes.markerKey })
      },
      markerType: {
        default: 'text',
        parseHTML: element => element.getAttribute('data-marker-type') || 'text',
        renderHTML: attributes => ({ 'data-marker-type': attributes.markerType })
      },
      token: {
        default: '',
        parseHTML: element => element.getAttribute('data-marker-token') || '',
        renderHTML: attributes => attributes.token ? { 'data-marker-token': attributes.token } : {}
      },
      label: {
        default: 'Маркер',
        parseHTML: element => element.textContent?.trim() || 'Маркер',
        renderHTML: () => ({})
      }
    }
  },

  parseHTML() {
    return [{ tag: 'span[data-template-marker="true"]' }]
  },

  renderHTML({ node, HTMLAttributes }) {
    return [
      'span',
      {
        ...HTMLAttributes,
        class: `template-marker template-marker--${node.attrs.markerType}`,
        'data-template-marker': 'true',
        contenteditable: 'false',
        draggable: 'true',
        title: `${node.attrs.label} · ${node.attrs.token || node.attrs.markerKey} · ${node.attrs.markerKey}`
      },
      node.attrs.label
    ]
  }
})

const TemplateTable = Table.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      transparent: {
        default: false,
        parseHTML: element => element.getAttribute('data-transparent') === 'true',
        renderHTML: (attributes) => {
          if (!attributes.transparent) return {}
          return {
            'data-transparent': 'true',
            class: 'transparent-table'
          }
        }
      }
    }
  }
})

const ResizableImage = Image.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      width: {
        default: null,
        parseHTML: element => element.getAttribute('width') || element.style.width || null,
        renderHTML: (attributes) => {
          if (!attributes.width) return {}
          return { width: attributes.width }
        }
      },
      height: {
        default: null,
        parseHTML: element => element.getAttribute('height') || element.style.height || null,
        renderHTML: (attributes) => {
          if (!attributes.height) return {}
          return { height: attributes.height }
        }
      }
    }
  }
})

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Underline,
    TextStyle,
    FontSize,
    FontFamily,
    Link.configure({ openOnClick: false }),
    ResizableImage.configure({ allowBase64: true }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Placeholder.configure({ placeholder: 'Начните редактировать шаблон...' }),
    PageBreak,
    TemplateMarker,
    TemplateTable.configure({ resizable: true }),
    TableRow,
    TableHeader,
    TableCell
  ],
  onUpdate({ editor }) {
    emit('update:modelValue', editor.getHTML())
    refreshUsedMarkers()
    nextTick(updatePageMetrics)
  },
  editorProps: {
    attributes: {
      class: 'template-prose'
    },
    handleDrop(view, event, _slice, moved) {
      if (moved) return false

      const markerPayload = event.dataTransfer?.getData(TEMPLATE_MARKER_DRAG_MIME)
      if (!markerPayload) return false

      try {
        const marker = JSON.parse(markerPayload) as {
          key: string
          type: string
          label: string
          token: string
        }
        const position = view.posAtCoords({ left: event.clientX, top: event.clientY })
        if (!position) return false

        view.dispatch(
          view.state.tr.insert(position.pos, view.state.schema.nodes.templateMarker.create({
            markerId: `marker-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
            markerKey: marker.key,
            markerType: marker.type,
            token: marker.token,
            label: marker.label
          }))
        )
        setTimeout(refreshUsedMarkers)
        return true
      } catch {
        return false
      }
    }
  }
})

const toolbarEditor = computed(() => editor.value ?? null)
const markerGroups = computed(() => TEMPLATE_MARKER_GROUPS.map(group => ({
  group,
  markers: TEMPLATE_MARKERS.filter(marker => marker.group === group)
})).filter(group => group.markers.length))

function refreshUsedMarkers() {
  usedMarkerKeys.value = new Set(extractTemplateMarkers(editor.value?.getHTML() || props.modelValue).map(marker => marker.key))
}

function insertMarker(marker: TemplateMarkerDefinition) {
  editor.value?.chain().focus().insertContent(createTemplateMarkerHtml(marker)).run()
  refreshUsedMarkers()
}

function startMarkerDrag(event: DragEvent, marker: TemplateMarkerDefinition) {
  event.dataTransfer?.setData(TEMPLATE_MARKER_DRAG_MIME, JSON.stringify({
    key: marker.key,
    type: marker.type,
    label: marker.label,
    token: marker.token
  }))
  event.dataTransfer?.setData('text/html', createTemplateMarkerHtml(marker))
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'copy'
}

function updatePageMetrics() {
  const paper = editorStage.value?.querySelector('.template-prose') as HTMLElement | null
  if (!paper) return

  const manualBreaks = paper.querySelectorAll('[data-page-break="true"]').length
  const heightPages = Math.ceil(Math.max(1, paper.scrollHeight - 128) / A4_CONTENT_HEIGHT)
  pageCount.value = Math.max(1, manualBreaks + 1, heightPages)

  const scrollTop = editorStage.value?.scrollTop || 0
  currentPage.value = Math.min(pageCount.value, Math.max(1, Math.floor(scrollTop / (A4_PAGE_HEIGHT + A4_PAGE_GAP)) + 1))
}

function removeAutoPageBreaks(html: string) {
  if (!import.meta.client) return html

  const wrapper = document.createElement('div')
  wrapper.innerHTML = html
  wrapper.querySelectorAll('[data-auto-page-break="true"]').forEach(node => node.remove())
  return wrapper.innerHTML
}

function getBlockOuterHeight(node: HTMLElement) {
  const style = window.getComputedStyle(node)
  const marginTop = Number.parseFloat(style.marginTop || '0') || 0
  const marginBottom = Number.parseFloat(style.marginBottom || '0') || 0
  return node.offsetHeight + marginTop + marginBottom
}

async function paginateImportedContent() {
  if (!editor.value || !import.meta.client) return

  const cleanHtml = removeAutoPageBreaks(editor.value.getHTML())
  if (cleanHtml !== editor.value.getHTML()) {
    editor.value.commands.setContent(cleanHtml, { emitUpdate: false })
    await nextTick()
  }

  await new Promise(resolve => requestAnimationFrame(resolve))

  const paper = editorStage.value?.querySelector('.template-prose') as HTMLElement | null
  if (!paper) return

  const nodes = Array.from(paper.children) as HTMLElement[]
  const nextHtml: string[] = []
  let pageHeight = 0

  nodes.forEach((node) => {
    if (node.dataset.pageBreak === 'true') {
      nextHtml.push(node.outerHTML)
      pageHeight = 0
      return
    }

    const blockHeight = getBlockOuterHeight(node)
    if (pageHeight > 0 && pageHeight + blockHeight > A4_CONTENT_HEIGHT) {
      nextHtml.push('<div class="page-break" data-page-break="true" data-auto-page-break="true"></div>')
      pageHeight = 0
    }

    nextHtml.push(node.outerHTML)
    pageHeight += blockHeight
  })

  const paginatedHtml = nextHtml.join('')
  if (paginatedHtml && paginatedHtml !== editor.value.getHTML()) {
    editor.value.commands.setContent(paginatedHtml, { emitUpdate: true })
    await nextTick()
  }

  updatePageMetrics()
}

function scheduleImportedPagination() {
  if (paginationFrame) cancelAnimationFrame(paginationFrame)
  paginationFrame = requestAnimationFrame(() => {
    void paginateImportedContent()
    paginationFrame = 0
  })
}

const pageGuideStyle = computed(() => ({
  '--template-page-count': pageCount.value,
  '--template-page-height': `${A4_PAGE_HEIGHT}px`,
  '--template-content-height': `${A4_CONTENT_HEIGHT}px`,
  '--template-page-gap': `${A4_PAGE_GAP}px`,
  '--template-page-step': `${A4_PAGE_HEIGHT + A4_PAGE_GAP}px`
}))

watch(() => props.modelValue, (value) => {
  if (!editor.value || editor.value.getHTML() === value) return
  editor.value.commands.setContent(value, { emitUpdate: false })
  refreshUsedMarkers()
  nextTick(updatePageMetrics)
})

watch(() => props.description, value => {
  draftDescription.value = value || ''
})

function saveDescription() {
  emit('update:description', draftDescription.value)
  descriptionDialog.value = false
}

onMounted(() => nextTick(() => {
  refreshUsedMarkers()
  updatePageMetrics()
  window.addEventListener(IMPORT_PAGINATION_EVENT, scheduleImportedPagination)
}))
onBeforeUnmount(() => {
  window.removeEventListener(IMPORT_PAGINATION_EVENT, scheduleImportedPagination)
  if (paginationFrame) cancelAnimationFrame(paginationFrame)
  editor.value?.destroy()
})
</script>

<template>
  <v-card class="template-editor">
    <div class="editor-meta-bar">
      <div class="editor-title-block">
        <input
          class="template-title-input"
          :value="title"
          placeholder="Введите название шаблона"
          aria-label="Название шаблона"
          @input="emit('update:title', ($event.target as HTMLInputElement).value)"
        >
        <p class="text-sm text-medium-emphasis">A4 template / pages: {{ pageCount }}</p>
      </div>
      <div class="editor-meta-actions">
        <v-select
          class="source-language-select"
          density="compact"
          hide-details
          label="Исходный язык"
          :items="languageOptions"
          :model-value="sourceLanguage || 'ru'"
          variant="outlined"
          @update:model-value="emit('update:sourceLanguage', $event as 'kz' | 'ru' | 'en')"
        />
        <v-btn
          size="small"
          variant="tonal"
          class="text-none"
          @click="descriptionDialog = true"
        >
          Описание
        </v-btn>
        <v-chip color="primary" variant="tonal" size="small">
          Страница {{ currentPage }} из {{ pageCount }}
        </v-chip>
      </div>
    </div>
    <TemplateToolbar :editor="toolbarEditor" />
    <div class="editor-workspace">
      <div ref="editorStage" class="editor-stage" @scroll="updatePageMetrics">
        <div class="editor-paper" :style="pageGuideStyle">
          <EditorContent :editor="editor" />
        </div>
      </div>
      <aside class="marker-sidebar">
        <div class="marker-sidebar__header">
          <p class="marker-sidebar__eyebrow">Auto-fill</p>
          <h3>Маркеры</h3>
          <p>Перетащите маркер в нужное место на A4-листе. Один и тот же маркер можно использовать несколько раз.</p>
          <div class="marker-sidebar__help">
            Маркеры дисциплины заполняются один раз при создании дисциплины. Ручные маркеры берут данные из конструктора силлабуса.
            Табличные маркеры вставляют готовую таблицу в место, где стоит маркер.
          </div>
        </div>

        <div v-if="markerGroups.length" class="marker-sidebar__groups">
          <section
            v-for="group in markerGroups"
            :key="group.group"
            class="marker-sidebar__group"
          >
            <h4>{{ group.group }}</h4>
            <button
              v-for="marker in group.markers"
              :key="marker.key"
              class="marker-option"
              :class="`marker-option--${marker.type}`"
              type="button"
              draggable="true"
              @click="insertMarker(marker)"
              @dragstart="startMarkerDrag($event, marker)"
            >
              <span class="marker-option__top">
                <span class="marker-option__label">{{ marker.label }}</span>
                <span class="marker-option__badge">{{ marker.type }}</span>
              </span>
              <span class="marker-option__token">{{ marker.token }}</span>
              <span class="marker-option__description">{{ marker.description }}</span>
              <span class="marker-option__insert">Вставить</span>
            </button>
          </section>
        </div>

        <div v-else class="marker-sidebar__empty">
          Все доступные маркеры уже добавлены в шаблон.
        </div>
      </aside>
    </div>

    <v-dialog v-model="descriptionDialog" max-width="560">
      <v-card class="pa-2">
        <v-card-title class="font-weight-black">Описание шаблона</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="draftDescription"
            label="Описание"
            rows="5"
            auto-grow
            placeholder="Например: основной шаблон силлабуса для бакалавриата"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="descriptionDialog = false">Отмена</v-btn>
          <v-btn color="primary" class="text-none font-weight-bold" @click="saveDescription">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style>
.template-editor {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), .1);
}
.editor-meta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  padding: 12px 14px;
}
.editor-title-block {
  min-width: 0;
  flex: 1;
}
.editor-meta-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.source-language-select {
  width: 150px;
}
.template-title-input {
  width: min(620px, 100%);
  border: 0;
  border-bottom: 1px solid transparent;
  background: transparent;
  color: rgb(var(--v-theme-on-surface));
  font-size: clamp(20px, 2.2vw, 30px);
  font-weight: 950;
  line-height: 1.15;
  outline: none;
  padding: 2px 0 4px;
}
.template-title-input:hover,
.template-title-input:focus {
  border-bottom-color: rgba(var(--v-theme-primary), .65);
}
.template-title-input::placeholder {
  color: rgba(var(--v-theme-on-surface), .42);
}
.editor-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  min-height: 0;
}
.editor-stage {
  overflow: auto;
  max-height: calc(100vh - 270px);
  background:
    radial-gradient(circle at top left, rgba(var(--v-theme-primary), .08), transparent 30%),
    rgb(var(--v-theme-surface-bright));
  padding: 28px;
}
.editor-paper {
  position: relative;
  width: 794px;
  min-height: calc(var(--template-page-count, 1) * var(--template-page-height, 1123px) + (var(--template-page-count, 1) - 1) * var(--template-page-gap, 28px));
  max-width: 100%;
  margin: 0 auto;
  border: 0;
  background: #fff;
  color: #111827;
  box-shadow: 0 24px 70px rgba(0, 0, 0, .22);
}
.template-prose {
  position: relative;
  z-index: 1;
  min-height: 1123px;
  padding: 64px 72px;
  background: transparent;
  outline: none;
  overflow-wrap: anywhere;
  word-break: normal;
  font-family: Arial, Helvetica, sans-serif;
}
.template-prose h1 {
  font-size: 28px;
  font-weight: 900;
}
.template-prose h2 {
  margin-top: 18px;
  font-size: 22px;
  font-weight: 900;
}
.template-prose h3 {
  margin-top: 14px;
  font-size: 18px;
  font-weight: 800;
}
.template-prose p,
.template-prose li {
  line-height: 1.7;
}
.template-prose p {
  margin: 0 0 10px;
}
.template-prose ul,
.template-prose ol {
  margin: 10px 0;
  padding-left: 28px;
}
.template-prose ul {
  list-style: disc;
}
.template-prose ol {
  list-style: decimal;
}
.template-prose a {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.template-prose .template-marker {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  margin: 0 3px;
  border: 1px solid rgba(16, 185, 129, .42);
  border-radius: 999px;
  background: rgba(16, 185, 129, .12);
  color: #047857;
  cursor: grab;
  font-size: .88em;
  font-weight: 800;
  line-height: 1.2;
  padding: 3px 9px;
  user-select: none;
  vertical-align: baseline;
  white-space: nowrap;
}
.template-prose .template-marker::before {
  margin-right: 5px;
  content: '◆';
  font-size: .72em;
}
.template-prose .template-marker--table {
  border-color: rgba(37, 99, 235, .42);
  background: rgba(37, 99, 235, .12);
  color: #1d4ed8;
}
.template-prose .template-marker--list {
  border-color: rgba(5, 150, 105, .42);
  background: rgba(5, 150, 105, .12);
  color: #047857;
}
.template-prose .template-marker--rich_text,
.template-prose .template-marker--link,
.template-prose .template-marker--block {
  border-color: rgba(16, 185, 129, .42);
  background: rgba(16, 185, 129, .12);
  color: #047857;
}
.template-prose .template-marker--image {
  border-color: rgba(124, 58, 237, .42);
  background: rgba(124, 58, 237, .12);
  color: #6d28d9;
}
.template-prose .template-marker.ProseMirror-selectednode {
  outline: 3px solid rgba(16, 185, 129, .35);
  outline-offset: 2px;
}
.template-prose table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  margin: 14px 0;
  break-inside: avoid;
  page-break-inside: avoid;
}
.template-prose h1,
.template-prose h2,
.template-prose h3,
.template-prose p,
.template-prose ul,
.template-prose ol,
.template-prose blockquote,
.template-prose img {
  break-inside: avoid;
  page-break-inside: avoid;
}
.template-prose th,
.template-prose td {
  border: 1px solid #cbd5e1;
  padding: 8px;
  vertical-align: top;
  max-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.template-prose table.transparent-table th,
.template-prose table.transparent-table td {
  border: 1px dashed #cbd5e1;
}
.template-prose table.imported-table th,
.template-prose table.imported-table td {
  border-style: dashed;
}
.template-prose table.transparent-table:hover th,
.template-prose table.transparent-table:hover td,
.template-prose table.transparent-table .selectedCell {
  outline: 1px dashed rgba(37, 99, 235, .6);
  outline-offset: -1px;
}
.template-prose img {
  max-width: 100%;
  object-fit: contain;
}
.template-prose td img,
.template-prose th img {
  display: block;
  max-width: 100%;
  height: auto;
}
.template-prose img.ProseMirror-selectednode {
  outline: 3px solid rgba(16, 185, 129, .55);
  outline-offset: 4px;
}
.template-prose .page-break {
  position: relative;
  height: var(--template-page-gap, 28px);
  margin: 22px -72px 30px;
  background: linear-gradient(90deg, rgba(226, 232, 240, .7), rgba(241, 245, 249, .95), rgba(226, 232, 240, .7));
  border-top: 0;
  break-after: page;
  page-break-after: always;
}
.template-prose .page-break::before {
  position: absolute;
  top: 50%;
  right: 0;
  left: 0;
  z-index: 1;
  border-top: 2px dashed #94a3b8;
  content: '';
  transform: translateY(-50%);
}
.template-prose .page-break::after {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  transform: translate(-50%, -50%);
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background: #fff;
  color: #64748b;
  content: 'Разрыв страницы';
  font-size: 11px;
  font-weight: 800;
  padding: 4px 12px;
}
.marker-sidebar {
  overflow: auto;
  max-height: calc(100vh - 270px);
  border-left: 1px solid rgba(var(--v-border-color), .1);
  background: rgba(var(--v-theme-surface), .9);
  padding: 18px;
}
.marker-sidebar__header {
  position: sticky;
  top: 0;
  z-index: 2;
  margin: -18px -18px 14px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  background: rgb(var(--v-theme-surface));
  padding: 18px;
}
.marker-sidebar__eyebrow {
  color: rgb(var(--v-theme-primary));
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}
.marker-sidebar h3 {
  margin-top: 3px;
  color: rgb(var(--v-theme-on-surface));
  font-size: 21px;
  font-weight: 950;
}
.marker-sidebar p {
  margin-top: 5px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 12px;
  line-height: 1.5;
}
.marker-sidebar__help {
  margin-top: 12px;
  border: 1px solid rgba(var(--v-theme-primary), .22);
  border-radius: 14px;
  background: rgba(var(--v-theme-primary), .08);
  color: rgba(var(--v-theme-on-surface), .78);
  font-size: 12px;
  line-height: 1.55;
  padding: 10px 12px;
}
.marker-sidebar__groups {
  display: grid;
  gap: 14px;
}
.marker-sidebar__group h4 {
  margin-bottom: 8px;
  color: rgba(var(--v-theme-on-surface), .7);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.marker-option {
  display: grid;
  width: 100%;
  gap: 6px;
  margin-bottom: 8px;
  border: 1px solid rgba(16, 185, 129, .24);
  border-radius: 14px;
  background: rgba(16, 185, 129, .08);
  color: rgb(var(--v-theme-on-surface));
  cursor: grab;
  padding: 10px 12px;
  text-align: left;
  transition: border-color .16s, background .16s, transform .16s;
}
.marker-option:hover {
  border-color: rgba(var(--v-theme-primary), .55);
  background: rgba(var(--v-theme-primary), .14);
  transform: translateY(-1px);
}
.marker-option--table {
  border-color: rgba(37, 99, 235, .28);
  background: rgba(37, 99, 235, .08);
}
.marker-option--image {
  border-color: rgba(124, 58, 237, .28);
  background: rgba(124, 58, 237, .08);
}
.marker-option__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.marker-option__label {
  font-size: 13px;
  font-weight: 850;
}
.marker-option__badge {
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), .08);
  color: rgba(var(--v-theme-on-surface), .76);
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  padding: 4px 7px;
  text-transform: uppercase;
}
.marker-option__token {
  color: rgba(var(--v-theme-on-surface), .58);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 11px;
}
.marker-option__description {
  color: rgba(var(--v-theme-on-surface), .66);
  font-size: 11px;
  line-height: 1.45;
}
.marker-option__insert {
  justify-self: start;
  color: rgb(var(--v-theme-primary));
  font-size: 11px;
  font-weight: 900;
}
.marker-sidebar__empty {
  border: 1px dashed rgba(var(--v-border-color), .22);
  border-radius: 16px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 13px;
  line-height: 1.6;
  padding: 18px;
  text-align: center;
}
@media (max-width: 768px) {
  .editor-workspace {
    grid-template-columns: 1fr;
  }
  .editor-stage {
    padding: 12px;
  }
  .marker-sidebar {
    max-height: none;
    border-top: 1px solid rgba(var(--v-border-color), .1);
    border-left: 0;
  }
  .template-prose {
    padding: 24px;
  }
  .template-prose .page-break {
    margin-right: -24px;
    margin-left: -24px;
  }
  .editor-meta-bar,
  .editor-meta-actions {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
