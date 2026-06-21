import { defineStore } from 'pinia'
import { SYLLABUS_TEMPLATE_CATALOG } from '~/constants/syllabusTemplates'
import type { TemplateMarkerInstance } from '~/utils/templateMarkers'
import { extractTemplateMarkers, validateTemplatePayload } from '~/utils/templateMarkers'

export type TemplateValidationStatus = 'valid' | 'invalid'
export type TemplateSourceLanguage = 'kz' | 'ru' | 'en'
export type TemplateTranslationStatus = 'not_translated' | 'translating' | 'completed' | 'failed'

export interface TemplateRecord {
  id: string
  owner?: string
  title: string
  description: string
  content: string
  markers: TemplateMarkerInstance[]
  validationStatus: TemplateValidationStatus
  isDefault: boolean
  sourceLanguage: TemplateSourceLanguage
  contentKz: string
  contentRu: string
  contentEn: string
  translationStatus: TemplateTranslationStatus
  translationError: string
  translatedAt: string | null
  translationTaskId: string
  createdAt?: string
  updatedAt: string
}

export interface TemplateTranslationResponse {
  id: string
  sourceLanguage: TemplateSourceLanguage
  translationStatus: TemplateTranslationStatus
  translationError: string
  translatedAt: string | null
  translationTaskId: string
  contentKz: string
  contentRu: string
  contentEn: string
}

const LEGACY_STORAGE_KEY = 'sgs-template-builder-v2'
const LEGACY_ACTIVE_KEY = 'sgs-active-template-id-v2'

function now() {
  return new Date().toISOString()
}

function defaultContent() {
  return `
    <h2>Default AlmaU Syllabus Template</h2>
    <p>This local template is used for future template experiments. The backend PDF currently uses the Django WeasyPrint template.</p>
    <h3>Sections</h3>
    <ul>
      <li>Title information</li>
      <li>Course description and learning outcomes</li>
      <li>16-week thematic plan</li>
      <li>Assessment system</li>
      <li>Course policy and signatures</li>
    </ul>
    <table>
      <tbody>
        <tr><th>Block</th><th>Purpose</th></tr>
        <tr><td>Policy</td><td>Academic integrity, communication and exam ethics.</td></tr>
        <tr><td>Assessment</td><td>Rubrics and final point calculation.</td></tr>
      </tbody>
    </table>
  `
}

function createDefaults(): TemplateRecord[] {
  return SYLLABUS_TEMPLATE_CATALOG.map((item, index) => normalizeTemplate({
    ...item,
    content: index === 0 ? defaultContent() : `<h2>${item.title}</h2><p>${item.description}</p>`,
    markers: [],
    validationStatus: 'valid',
    isDefault: index === 0,
    sourceLanguage: 'ru',
    contentKz: '',
    contentRu: '',
    contentEn: '',
    translationStatus: 'not_translated',
    translationError: '',
    translatedAt: null,
    translationTaskId: '',
    updatedAt: now()
  }))
}

function normalizeTemplate(template: Partial<TemplateRecord> & { id?: string }): TemplateRecord {
  const content = template.content || ''
  const markers = Array.isArray(template.markers) ? template.markers : extractTemplateMarkers(content)
  const validation = validateTemplatePayload(template.title || '', template.description || '', content)

  return {
    id: String(template.id || ''),
    owner: template.owner,
    title: template.title || '',
    description: template.description || '',
    content,
    markers,
    validationStatus: template.validationStatus || (validation.valid ? 'valid' : 'invalid'),
    isDefault: Boolean(template.isDefault),
    sourceLanguage: template.sourceLanguage || 'ru',
    contentKz: template.contentKz || '',
    contentRu: template.contentRu || '',
    contentEn: template.contentEn || '',
    translationStatus: template.translationStatus || 'not_translated',
    translationError: template.translationError || '',
    translatedAt: template.translatedAt || null,
    translationTaskId: template.translationTaskId || '',
    createdAt: template.createdAt,
    updatedAt: template.updatedAt || now()
  }
}

function api() {
  return useTemplateApi()
}

export const useTemplatesStore = defineStore('templates', () => {
  const templates = ref<TemplateRecord[]>([])
  const activeTemplateId = ref('')
  const initialized = ref(false)
  const loading = ref(false)
  const usingLocalFallback = ref(false)

  async function initialize(force = false) {
    if ((initialized.value && !force) || loading.value) return
    loading.value = true
    try {
      const response = await api().list()
      const records = Array.isArray(response) ? response : response.results || []
      templates.value = records.map(item => normalizeTemplate(item))
      await migrateLegacyTemplatesIfNeeded()
      activeTemplateId.value = templates.value.find(item => item.isDefault)?.id || ''
      initialized.value = true
      usingLocalFallback.value = false
    } catch {
      loadLocalFallback()
      usingLocalFallback.value = true
      initialized.value = true
    } finally {
      loading.value = false
    }
  }

  async function migrateLegacyTemplatesIfNeeded() {
    if (!import.meta.client || templates.value.length) return
    const saved = JSON.parse(localStorage.getItem(LEGACY_STORAGE_KEY) || 'null') as TemplateRecord[] | null
    if (!Array.isArray(saved) || !saved.length) return
    const activeId = localStorage.getItem(LEGACY_ACTIVE_KEY) || ''
    const migrated: TemplateRecord[] = []
    for (const template of saved.map(item => normalizeTemplate(item))) {
      const created = await api().create(toApiPayload({
        ...template,
        isDefault: false
      }))
      migrated.push(normalizeTemplate(created))
    }
    templates.value = migrated
    const activeTemplate = migrated.find(item => saved.some(old => old.id === activeId && old.title === item.title))
    if (activeTemplate?.validationStatus === 'valid') {
      const updated = await api().setDefault(activeTemplate.id)
      templates.value.forEach(item => { item.isDefault = item.id === updated.id })
      upsert(updated)
    }
  }

  function loadLocalFallback() {
    if (!import.meta.client) {
      templates.value = createDefaults()
      activeTemplateId.value = templates.value[0]?.id || ''
      return
    }
    const saved = JSON.parse(localStorage.getItem(LEGACY_STORAGE_KEY) || 'null') as TemplateRecord[] | null
    templates.value = Array.isArray(saved) && saved.length
      ? saved.map(item => normalizeTemplate(item))
      : createDefaults()
    const savedActiveId = localStorage.getItem(LEGACY_ACTIVE_KEY) || ''
    activeTemplateId.value = templates.value.some(template => template.id === savedActiveId)
      ? savedActiveId
      : templates.value.find(template => template.isDefault)?.id || ''
  }

  function persistFallback() {
    if (!import.meta.client || !usingLocalFallback.value) return
    localStorage.setItem(LEGACY_STORAGE_KEY, JSON.stringify(templates.value))
    localStorage.setItem(LEGACY_ACTIVE_KEY, activeTemplateId.value)
  }

  function toApiPayload(payload: Partial<TemplateRecord>) {
    return {
      title: payload.title,
      description: payload.description,
      content: payload.content,
      markers: payload.markers,
      validationStatus: payload.validationStatus,
      isDefault: payload.isDefault,
      sourceLanguage: payload.sourceLanguage || 'ru'
    }
  }

  function upsert(template: TemplateRecord) {
    const normalized = normalizeTemplate(template)
    const index = templates.value.findIndex(item => item.id === normalized.id)
    if (index === -1) templates.value.unshift(normalized)
    else templates.value[index] = normalized
    activeTemplateId.value = templates.value.find(item => item.isDefault)?.id || activeTemplateId.value
    return normalized
  }

  async function getTemplateById(id: string) {
    await initialize()
    const cached = templates.value.find(item => item.id === id)
    if (cached || usingLocalFallback.value) return cached || null
    return upsert(await api().get(id))
  }

  async function getDefaultTemplate() {
    await initialize()
    return templates.value.find(item => item.isDefault)
      || templates.value.find(item => item.validationStatus === 'valid')
      || templates.value[0]
      || null
  }

  async function createTemplate(payload: Pick<TemplateRecord, 'title' | 'description' | 'content'> & Partial<TemplateRecord>) {
    await initialize()
    const validation = validateTemplatePayload(payload.title, payload.description, payload.content)
    const draft = normalizeTemplate({
      ...payload,
      markers: validation.markers,
      validationStatus: validation.valid ? 'valid' : 'invalid',
      isDefault: false,
      sourceLanguage: payload.sourceLanguage || 'ru',
      updatedAt: now()
    })

    if (usingLocalFallback.value) {
      draft.id = `tpl-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
      if (draft.validationStatus === 'valid') templates.value.forEach(item => { item.isDefault = false })
      templates.value.unshift(draft)
      activeTemplateId.value = draft.isDefault ? draft.id : activeTemplateId.value
      persistFallback()
      return draft
    }

    const created = upsert(await api().create(toApiPayload(draft)))
    if (created.validationStatus === 'valid') {
      const updated = await api().setDefault(created.id)
      templates.value.forEach(item => { item.isDefault = item.id === updated.id })
      return upsert(updated)
    }
    return created
  }

  async function updateTemplate(id: string, payload: string | Partial<Pick<TemplateRecord, 'title' | 'description' | 'content' | 'sourceLanguage'>>) {
    await initialize()
    const item = templates.value.find(template => template.id === id)
    if (!item) return null

    const next = typeof payload === 'string'
      ? { ...item, content: payload }
      : { ...item, ...payload }
    const validation = validateTemplatePayload(next.title, next.description, next.content)
    next.markers = validation.markers
    next.validationStatus = validation.valid ? 'valid' : 'invalid'

    if (usingLocalFallback.value) {
      Object.assign(item, normalizeTemplate(next), { updatedAt: now() })
      persistFallback()
      return item
    }

    return upsert(await api().update(id, toApiPayload(next)))
  }

  async function setActive(id: string) {
    await initialize()
    const template = templates.value.find(item => item.id === id)
    if (!template || template.validationStatus !== 'valid') return false

    if (usingLocalFallback.value) {
      templates.value.forEach(item => { item.isDefault = item.id === id })
      activeTemplateId.value = id
      persistFallback()
      return true
    }

    const updated = await api().setDefault(id)
    templates.value.forEach(item => { item.isDefault = item.id === updated.id })
    upsert(updated)
    activeTemplateId.value = updated.id
    return true
  }

  async function translateTemplate(id: string) {
    if (usingLocalFallback.value) return null
    const response = await api().translate(id)
    const template = templates.value.find(item => item.id === id)
    if (template) {
      template.translationStatus = response.status
      template.translationTaskId = response.taskId
      template.translationError = ''
    }
    return response
  }

  async function refreshTranslations(id: string) {
    if (usingLocalFallback.value) return null
    const response = await api().translations(id)
    const template = templates.value.find(item => item.id === id)
    if (template) {
      template.sourceLanguage = response.sourceLanguage
      template.translationStatus = response.translationStatus
      template.translationError = response.translationError
      template.translatedAt = response.translatedAt
      template.translationTaskId = response.translationTaskId
      template.contentKz = response.contentKz
      template.contentRu = response.contentRu
      template.contentEn = response.contentEn
    }
    return response
  }

  async function removeTemplate(id: string) {
    await initialize()
    if (!usingLocalFallback.value) await api().remove(id)
    templates.value = templates.value.filter(item => item.id !== id)
    if (activeTemplateId.value === id) activeTemplateId.value = templates.value.find(item => item.isDefault)?.id || ''
    persistFallback()
  }

  return {
    templates,
    activeTemplateId,
    initialized,
    loading,
    usingLocalFallback,
    initialize,
    getTemplateById,
    getDefaultTemplate,
    createTemplate,
    updateTemplate,
    setActive,
    translateTemplate,
    refreshTranslations,
    removeTemplate
  }
})
