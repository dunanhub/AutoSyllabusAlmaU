import QRCode from 'qrcode'
import {
  TEMPLATE_MARKER_BY_KEY,
  type TemplateMarkerDefinition,
  type TemplateMarkerType
} from '~/constants/templateMarkers'
import type { Syllabus } from '~/types/syllabus'

export interface TemplateMarkerInstance extends TemplateMarkerDefinition {
  id: string
}

export interface TemplateValidationResult {
  valid: boolean
  errors: string[]
  markers: TemplateMarkerInstance[]
}

export interface RenderTemplateOptions {
  showPlaceholders?: boolean
  editableKeys?: Set<string> | string[]
}

export function createTemplateMarkerHtml(marker: TemplateMarkerDefinition) {
  const id = `marker-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
  const title = `${marker.label} · ${marker.token} · ${marker.key}`
  return `<span class="template-marker template-marker--${marker.type}" data-template-marker="true" data-marker-id="${id}" data-marker-key="${escapeHtml(marker.key)}" data-marker-type="${marker.type}" data-marker-token="${escapeHtml(marker.token)}" title="${escapeHtml(title)}">${escapeHtml(marker.label)}</span>`
}

export function extractTemplateMarkers(html: string): TemplateMarkerInstance[] {
  if (!html.trim()) return []
  const wrapper = createHtmlWrapper(html)
  return Array.from(wrapper.querySelectorAll('[data-template-marker="true"]')).map((node, index) => {
    const key = node.getAttribute('data-marker-key') || ''
    const fallbackType = (node.getAttribute('data-marker-type') || 'text') as TemplateMarkerType
    const definition = TEMPLATE_MARKER_BY_KEY[key]

    return {
      id: node.getAttribute('data-marker-id') || `marker-${index}`,
      key,
      label: definition?.label || node.textContent?.trim() || key || 'Неизвестный маркер',
      type: definition?.type || fallbackType,
      token: definition?.token || node.getAttribute('data-marker-token') || '',
      group: definition?.group || 'Неизвестные маркеры',
      description: definition?.description || '',
      repeatable: definition?.repeatable
    }
  })
}

export function validateTemplatePayload(title: string, description: string, content: string): TemplateValidationResult {
  const errors: string[] = []
  const markers = extractTemplateMarkers(content)

  if (!title.trim()) errors.push('Укажите название шаблона.')
  if (!description.trim()) errors.push('Укажите описание шаблона.')
  if (!content.trim()) errors.push('Добавьте содержимое шаблона.')

  markers.forEach((marker) => {
    if (!marker.key || !TEMPLATE_MARKER_BY_KEY[marker.key]) {
      errors.push(`Найден неизвестный или повреждённый маркер: ${marker.label || marker.id}.`)
    }
  })

  return { valid: errors.length === 0, errors, markers }
}

export function renderTemplateWithSyllabus(content: string, syllabus: Syllabus, options: RenderTemplateOptions = {}) {
  const wrapper = createHtmlWrapper(content)
  wrapper.querySelectorAll('[data-template-marker="true"]').forEach((node) => {
    const key = node.getAttribute('data-marker-key') || ''
    const html = renderMarkerHtml(key, syllabus, options)
    node.outerHTML = html || '<span class="template-empty-value">Не заполнено</span>'
  })
  return wrapper.innerHTML.replace(/\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}/g, (token, key: string) => {
    if (!TEMPLATE_MARKER_BY_KEY[key]) return token
    return renderMarkerHtml(key, syllabus, options) || '<span class="template-empty-value">Не заполнено</span>'
  })
}

function renderMarkerHtml(key: string, syllabus: Syllabus, options: RenderTemplateOptions) {
  if (options.showPlaceholders && isPlaceholderMarker(key, options) && isMarkerEmpty(key, syllabus)) {
    return renderPreviewPlaceholder(key)
  }
  return resolveMarkerHtml(key, syllabus)
}

function resolveMarkerHtml(key: string, syllabus: Syllabus) {
  const title = syllabus.titleInfo
  const policy = syllabus.coursePolicy
  const signatures = syllabus.signatures
  const syllabusUrl = title.qrUrl || ''
  const textValues: Record<string, string | number | undefined> = {
    'course.code_and_name': title.codeAndName,
    'course.credits': title.credits,
    'course.total_hours': title.totalHours,
    'course.classroom_hours': title.classroomHours,
    'course.independent_hours': title.independentWorkHours,
    'course.prerequisites': title.prerequisites,
    'course.level': title.levelOfTraining,
    'course.semester': title.semester,
    'course.program': title.educationalProgram,
    'course.format': title.formatOfTraining,
    'course.time_place': title.timeAndPlace,
    'teacher.full_name': title.instructorName,
    'teacher.email': title.instructorEmail,
    'approval.director_name': signatures.preparedByName,
    'approval.program_leader': signatures.preparedByPosition,
    'syllabus.url': syllabusUrl,
    'manual.course_description': syllabus.courseDescription,
    'manual.course_goal': syllabus.courseGoal,
    'manual.teaching_philosophy': syllabus.teachingPhilosophy,
    'manual.teaching_methods': policy.masteringDiscipline || policy.informationCommunication
  }

  if (key in textValues) return textValues[key] || textValues[key] === 0 ? formatTextHtml(textValues[key] || '') : ''
  if (key === 'syllabus.qr') return renderQrCode(syllabusUrl)
  if (key === 'list.required_literature') return renderList(syllabus.literature.required)
  if (key === 'list.additional_literature') return renderList(syllabus.literature.additional)
  if (key === 'list.internet_resources') return renderList(syllabus.literature.internetResources)
  if (key === 'table.learning_outcomes') return renderTable(['Код', 'Результат курса', 'Результат программы', 'Описание'], syllabus.learningOutcomes.map(row => [row.code, row.courseLearningOutcome, row.programLearningOutcome, row.description]))
  if (key === 'table.weekly_plan') return renderTable(['Неделя', 'Модуль', 'Результат', 'Вопросы', 'Задания'], syllabus.thematicPlan.map(row => [row.week, row.topicModule, row.courseOutcome, row.questions, row.tasks]))
  if (key === 'table.rubric') return renderTable(['Компонент', 'Макс. %', 'Вес', 'Итоговые баллы'], syllabus.assessmentSystem.map(row => [row.topicModule, row.maxPercent, row.maxWeight, row.finalPoints]))
  return ''
}

function isPlaceholderMarker(key: string, options: RenderTemplateOptions) {
  if (!options.editableKeys) return true
  return Array.isArray(options.editableKeys) ? options.editableKeys.includes(key) : options.editableKeys.has(key)
}

function isMarkerEmpty(key: string, syllabus: Syllabus) {
  const title = syllabus.titleInfo
  const policy = syllabus.coursePolicy
  const signatures = syllabus.signatures
  const values: Record<string, unknown> = {
    'course.code_and_name': title.codeAndName,
    'course.credits': title.credits,
    'course.total_hours': title.totalHours,
    'course.classroom_hours': title.classroomHours,
    'course.independent_hours': title.independentWorkHours,
    'course.prerequisites': title.prerequisites,
    'course.level': title.levelOfTraining,
    'course.semester': title.semester,
    'course.program': title.educationalProgram,
    'course.format': title.formatOfTraining,
    'course.time_place': title.timeAndPlace,
    'teacher.full_name': title.instructorName,
    'teacher.email': title.instructorEmail,
    'approval.director_name': signatures.preparedByName,
    'approval.program_leader': signatures.preparedByPosition,
    'syllabus.url': title.qrUrl,
    'syllabus.qr': title.qrUrl,
    'manual.course_description': syllabus.courseDescription,
    'manual.course_goal': syllabus.courseGoal,
    'manual.teaching_philosophy': syllabus.teachingPhilosophy,
    'manual.teaching_methods': policy.masteringDiscipline || policy.informationCommunication
  }

  if (key in values) return !String(values[key] || '').trim()
  if (key === 'list.required_literature') return !syllabus.literature.required.some(item => item.trim())
  if (key === 'list.additional_literature') return !syllabus.literature.additional.some(item => item.trim())
  if (key === 'list.internet_resources') return !syllabus.literature.internetResources.some(item => item.trim())
  if (key === 'table.learning_outcomes') return !syllabus.learningOutcomes.some(row => [row.code, row.courseLearningOutcome, row.programLearningOutcome, row.description].some(value => String(value || '').trim()))
  if (key === 'table.weekly_plan') return !syllabus.thematicPlan.some(row => [row.topicModule, row.courseOutcome, row.questions, row.tasks, row.literature, row.gradeStructure].some(value => String(value || '').trim()))
  if (key === 'table.rubric') return !syllabus.assessmentSystem.some(row => [row.topicModule, row.maxPercent, row.maxWeight, row.finalPoints].some(value => String(value || '').trim()))
  return true
}

function renderPreviewPlaceholder(key: string) {
  const marker = TEMPLATE_MARKER_BY_KEY[key]
  const label = marker?.label || marker?.token || key
  const type = marker?.type || 'text'
  return `<span class="template-preview-marker template-preview-marker--${escapeHtml(type)}" data-empty-marker="${escapeHtml(key)}">${escapeHtml(label)}</span>`
}

function renderList(items: string[]) {
  if (!items.length) return '<span class="template-empty-value">Не заполнено</span>'
  return `<ol>${items.map(item => `<li>${formatTextHtml(item)}</li>`).join('')}</ol>`
}

function renderTable(headers: string[], rows: Array<Array<string | number>>) {
  if (!rows.length) return '<span class="template-empty-value">Не заполнено</span>'
  return `<table><thead><tr>${headers.map(header => `<th>${formatTextHtml(header)}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${formatTextHtml(cell || '')}</td>`).join('')}</tr>`).join('')}</tbody></table>`
}

function renderQrCode(value: string) {
  if (!value.trim()) return ''

  try {
    const qr = QRCode.create(value, { errorCorrectionLevel: 'M' })
    const size = qr.modules.size
    const quietZone = 4
    const viewBoxSize = size + quietZone * 2
    const cells: string[] = []

    qr.modules.data.forEach((enabled, index) => {
      if (!enabled) return
      const x = (index % size) + quietZone
      const y = Math.floor(index / size) + quietZone
      cells.push(`<rect x="${x}" y="${y}" width="1" height="1"/>`)
    })

    return [
      '<span class="template-qr-code" data-template-rendered-qr="true">',
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${viewBoxSize} ${viewBoxSize}" width="96" height="96" role="img" aria-label="QR code">`,
      '<rect width="100%" height="100%" fill="#fff"/>',
      `<g fill="#000">${cells.join('')}</g>`,
      '</svg>',
      '</span>'
    ].join('')
  } catch {
    return `<span>${formatTextHtml(value)}</span>`
  }
}

function createHtmlWrapper(html: string) {
  if (import.meta.client) {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = html
    return wrapper
  }

  const template = globalThis.document?.createElement('div')
  if (template) {
    template.innerHTML = html
    return template
  }

  return {
    innerHTML: html,
    querySelectorAll: () => []
  } as unknown as HTMLDivElement
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function formatTextHtml(value: string | number) {
  return escapeHtml(String(value)).replace(/\r\n|\r|\n/g, '<br>')
}
