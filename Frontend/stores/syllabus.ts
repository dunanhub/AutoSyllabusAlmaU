import { defineStore } from 'pinia'
import type { DocumentFormat, DocumentLanguage, Syllabus, SyllabusInput, SyllabusStatus } from '~/types/syllabus'
import { calculateCompletion, normalizeSyllabus } from '~/utils/mockSyllabuses'

export const useSyllabusStore = defineStore('syllabus', () => {
  const syllabuses = ref<Syllabus[]>([])
  const initialized = ref(false)
  const loading = ref(false)

  function api() {
    return useSyllabusApi()
  }

  function normalizeRecord(record: Syllabus): Syllabus {
    const next = normalizeSyllabus(structuredClone(record))
    next.completion = calculateCompletion(next)
    return next
  }

  function upsertRecord(record: Syllabus) {
    const index = syllabuses.value.findIndex(item => item.id === record.id)
    if (index === -1) syllabuses.value.unshift(record)
    else syllabuses.value[index] = record
  }

  async function initialize(force = false) {
    if ((initialized.value && !force) || loading.value) return
    loading.value = true
    try {
      const response = await api().list()
      const records = Array.isArray(response) ? response : response.results || []
      syllabuses.value = records.map(item => normalizeRecord(item))
      initialized.value = true
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    initialized.value = false
    await initialize(true)
  }

  async function getSyllabuses() {
    if (!initialized.value) await initialize()
    return syllabuses.value
  }

  async function getSyllabusById(id: string, force = false) {
    const cached = syllabuses.value.find(item => item.id === id)
    if (cached && !force) return cached
    const fetched = normalizeRecord(await api().get(id))
    upsertRecord(fetched)
    return fetched
  }

  async function createSyllabus(payload: SyllabusInput | Syllabus) {
    const created = normalizeRecord(await api().create(payload as SyllabusInput))
    upsertRecord(created)
    return created
  }

  async function updateSyllabus(id: string, payload: Partial<Syllabus>) {
    const updated = normalizeRecord(await api().update(id, payload as Partial<SyllabusInput>))
    upsertRecord(updated)
    return updated
  }

  async function patchSyllabus(id: string, payload: Partial<Syllabus>) {
    const updated = normalizeRecord(await api().patch(id, payload as Partial<SyllabusInput>))
    upsertRecord(updated)
    return updated
  }

  async function deleteSyllabus(id: string) {
    await api().remove(id)
    syllabuses.value = syllabuses.value.filter(item => item.id !== id)
  }

  async function duplicateSyllabus(id: string) {
    const copy = normalizeRecord(await api().duplicate(id))
    upsertRecord(copy)
    return copy
  }

  async function updateStatus(id: string, status: SyllabusStatus) {
    const updated = normalizeRecord(await api().setStatus(id, status))
    upsertRecord(updated)
    return updated
  }

  async function generatePdf(id: string) {
    const response = await api().generatePdf(id)
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.pdfStatus = response.status
      record.pdfTaskId = response.taskId
      record.pdfError = ''
      record.pdfGeneratedAt = null
      record.documents = undefined
    }
    return record
  }

  async function getPdfStatus(id: string) {
    const response = await api().getPdfStatus(id)
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.pdfStatus = response.pdfStatus
      record.pdfTaskId = response.taskId
      record.pdfGeneratedAt = response.pdfGeneratedAt
      record.pdfError = response.pdfError
      record.pdfFile = response.pdfFile
      record.documents = response.documents
    }
    return record
  }

  async function downloadPdf(id: string) {
    await downloadDocument(id, { language: 'ru', format: 'pdf' })
  }

  async function downloadDocument(id: string, options: { language: DocumentLanguage, format: DocumentFormat }) {
    const blob = await api().downloadDocument(id, options.language, options.format)
    if (!import.meta.client) return

    const syllabus = syllabuses.value.find(item => item.id === id)
    const courseCode = syllabus?.titleInfo.codeAndName.split('—', 1)[0].trim() || id
    const safeCode = courseCode.replace(/[^\p{L}\p{N}_.-]+/gu, '_').replace(/^[._]+|[._]+$/g, '')
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `syllabus_${safeCode || id}_${options.language}.${options.format}`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  async function translateRendered(id: string) {
    const response = await api().translateRendered(id)
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.renderTranslationStatus = response.status
      record.renderTranslationTaskId = response.taskId
      record.renderTranslationError = ''
    }
    return record
  }

  async function getRenderTranslationStatus(id: string) {
    const response = await api().getRenderTranslationStatus(id)
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.renderTranslationStatus = response.status
      record.renderTranslationTaskId = response.taskId
      record.renderTranslationError = response.error
      record.renderTranslatedAt = response.translatedAt
      record.renderedContent = response.renderedContent
      record.renderedContentKz = response.renderedContentKz
      record.renderedContentRu = response.renderedContentRu
      record.renderedContentEn = response.renderedContentEn
    }
    return record
  }

  async function aiFill(id: string) {
    const response = await api().aiFill(id)
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.aiFillStatus = response.status
      record.aiFillTaskId = response.taskId
      record.aiFillError = ''
      record.aiFilledAt = null
    }
    return record
  }

  async function getAiFillStatus(id: string) {
    const response = await api().getAiFillStatus(id)
    if (response.syllabus) {
      const updated = normalizeRecord(response.syllabus)
      upsertRecord(updated)
      return updated
    }
    const record = syllabuses.value.find(item => item.id === id)
    if (record) {
      record.aiFillStatus = response.status
      record.aiFillTaskId = response.taskId
      record.aiFillError = response.error
      record.aiFilledAt = response.filledAt
    }
    return record
  }

  async function reset() {
    syllabuses.value = []
    initialized.value = false
    loading.value = false
  }

  return {
    syllabuses,
    initialized,
    loading,
    initialize,
    refresh,
    getSyllabuses,
    getSyllabusById,
    createSyllabus,
    updateSyllabus,
    patchSyllabus,
    deleteSyllabus,
    duplicateSyllabus,
    updateStatus,
    generatePdf,
    getPdfStatus,
    downloadPdf,
    downloadDocument,
    translateRendered,
    getRenderTranslationStatus,
    aiFill,
    getAiFillStatus,
    reset
  }
})
