import { defineStore } from 'pinia'
import type { Syllabus, SyllabusInput, SyllabusStatus } from '~/types/syllabus'
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

  async function getSyllabusById(id: string) {
    const cached = syllabuses.value.find(item => item.id === id)
    if (cached) return cached
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
    }
    return record
  }

  async function downloadPdf(id: string) {
    const blob = await api().downloadPdf(id)
    if (!import.meta.client) return

    const syllabus = syllabuses.value.find(item => item.id === id)
    const courseCode = syllabus?.titleInfo.codeAndName.split('—', 1)[0].trim() || id
    const safeCode = courseCode.replace(/[^\p{L}\p{N}_.-]+/gu, '_').replace(/^[._]+|[._]+$/g, '')
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `syllabus_${safeCode || id}.pdf`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
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
    deleteSyllabus,
    duplicateSyllabus,
    updateStatus,
    generatePdf,
    getPdfStatus,
    downloadPdf,
    reset
  }
})
