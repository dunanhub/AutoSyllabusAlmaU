import type { Syllabus, SyllabusInput, SyllabusTitleInfo } from '~/types/syllabus'
import {
  DEFAULT_TEMPLATE_ID,
  createClassSchedulePreset,
  createThematicPlanPreset,
  getAssessmentScheme,
  getCoursePolicyTemplate,
  getLiteraturePreset,
  getTeachingPhilosophy
} from '~/constants/syllabusTemplates'

export interface CourseDetails {
  courseName: string
  courseCode: string
  languageOfEducation: string
  credits: string
  totalHours: string
  classroomHours: string
  independentWorkHours: string
  prerequisites: string
  levelOfTraining: string
  semester: string
  educationalProgram: string
  schoolId: string
  schoolName: string
  courseType: string
  templateId: string
  proficiencyLevel: string
  formatOfTraining: string
  timeAndPlace: string
  instructorName: string
  instructorDegree: string
  instructorEmail: string
  instructorContacts: string
  approvedBy: string
  deanName: string
  approvalDate: string
  courseDescription: string
  courseGoal: string
  qrUrl: string
}

export function splitCodeAndName(value = '') {
  const [code = '', ...rest] = value.split('—')
  return {
    courseCode: code.trim(),
    courseName: rest.join('—').trim()
  }
}

export function joinCodeAndName(courseCode: string, courseName: string) {
  return [courseCode.trim(), courseName.trim()].filter(Boolean).join(' — ')
}

function normalizeCodeAndName(details: CourseDetails) {
  const codeAndName = details.courseCode.trim()
  if (!codeAndName) return details.courseName.trim()
  if (codeAndName.includes('—') || !details.courseName.trim()) return codeAndName
  return joinCodeAndName(codeAndName, details.courseName)
}

export function createInitialCourseDetails(): CourseDetails {
  return {
    courseName: '',
    courseCode: '',
    languageOfEducation: 'MULTI',
    credits: '5',
    totalHours: '150',
    classroomHours: '45',
    independentWorkHours: '105',
    prerequisites: '',
    levelOfTraining: 'Бакалавриат',
    semester: '1 семестр',
    educationalProgram: '',
    schoolId: '',
    schoolName: '',
    courseType: 'default',
    templateId: DEFAULT_TEMPLATE_ID,
    proficiencyLevel: '',
    formatOfTraining: 'Очная',
    timeAndPlace: 'По утвержденному расписанию',
    instructorName: '',
    instructorDegree: '',
    instructorEmail: '',
    instructorContacts: '',
    approvedBy: '',
    deanName: '',
    approvalDate: new Date().toISOString().slice(0, 10),
    courseDescription: '',
    courseGoal: '',
    qrUrl: ''
  }
}

export function courseDetailsFromSyllabus(syllabus: Syllabus): CourseDetails {
  const names = splitCodeAndName(syllabus.titleInfo.codeAndName)
  return {
    ...createInitialCourseDetails(),
    ...names,
    languageOfEducation: syllabus.titleInfo.languageOfEducation || 'MULTI',
    credits: String(syllabus.titleInfo.credits || ''),
    totalHours: String(syllabus.titleInfo.totalHours || ''),
    classroomHours: String(syllabus.titleInfo.classroomHours || ''),
    independentWorkHours: String(syllabus.titleInfo.independentWorkHours || ''),
    prerequisites: syllabus.titleInfo.prerequisites || '',
    levelOfTraining: syllabus.titleInfo.levelOfTraining || '',
    semester: syllabus.titleInfo.semester || '',
    educationalProgram: syllabus.titleInfo.educationalProgram || '',
    schoolId: syllabus.titleInfo.schoolId || '',
    schoolName: syllabus.titleInfo.schoolName || '',
    courseType: syllabus.titleInfo.courseType || 'default',
    templateId: syllabus.titleInfo.templateId || DEFAULT_TEMPLATE_ID,
    proficiencyLevel: syllabus.titleInfo.proficiencyLevel || '',
    formatOfTraining: syllabus.titleInfo.formatOfTraining || '',
    timeAndPlace: syllabus.titleInfo.timeAndPlace || '',
    instructorName: syllabus.titleInfo.instructorName || '',
    instructorDegree: syllabus.titleInfo.instructorDegree || '',
    instructorEmail: syllabus.titleInfo.instructorEmail || '',
    instructorContacts: syllabus.titleInfo.instructorContacts || '',
    approvedBy: syllabus.signatures.preparedByName || '',
    deanName: syllabus.signatures.preparedByPosition || '',
    approvalDate: syllabus.signatures.preparedByDate || new Date().toISOString().slice(0, 10),
    courseDescription: syllabus.courseDescription || '',
    courseGoal: syllabus.courseGoal || '',
    qrUrl: syllabus.titleInfo.qrUrl || ''
  }
}

export function titleInfoFromCourseDetails(details: CourseDetails): SyllabusTitleInfo {
  return {
    codeAndName: normalizeCodeAndName(details),
    credits: details.credits,
    totalHours: details.totalHours,
    classroomHours: details.classroomHours,
    independentWorkHours: details.independentWorkHours,
    prerequisites: details.prerequisites,
    levelOfTraining: details.levelOfTraining,
    semester: details.semester,
    educationalProgram: details.educationalProgram,
    schoolId: details.schoolId,
    schoolName: details.schoolName,
    courseType: details.courseType,
    templateId: details.templateId,
    languageOfEducation: details.languageOfEducation,
    proficiencyLevel: details.proficiencyLevel,
    formatOfTraining: details.formatOfTraining,
    instructorName: details.instructorName,
    instructorDegree: details.instructorDegree,
    instructorEmail: details.instructorEmail,
    instructorContacts: details.instructorContacts,
    timeAndPlace: details.timeAndPlace,
    qrUrl: details.qrUrl
  }
}

export function createCourseSyllabusInput(details: CourseDetails): SyllabusInput {
  const courseType = details.courseType || 'default'
  const courseName = details.courseName || splitCodeAndName(details.courseCode).courseName || details.courseCode
  return {
    status: 'draft',
    completion: 62,
    titleInfo: titleInfoFromCourseDetails(details),
    classSchedule: createClassSchedulePreset(courseName, courseType),
    courseDescription: details.courseDescription,
    courseGoal: details.courseGoal,
    learningOutcomes: [{
      id: 'lo-1',
      code: 'PO1',
      courseLearningOutcome: 'Объясняет ключевые понятия и академический контекст дисциплины.',
      programLearningOutcome: 'Применяет профессиональные знания для анализа учебных и практических ситуаций.',
      description: 'Студент демонстрирует понимание основных концепций курса и умеет связывать их с образовательной программой.'
    }, {
      id: 'lo-2',
      code: 'PO2',
      courseLearningOutcome: 'Анализирует источники, кейсы и данные для аргументированного решения задач.',
      programLearningOutcome: 'Использует критическое мышление, коммуникацию и исследовательские навыки.',
      description: 'Студент выполняет письменные и устные задания с опорой на академические источники.'
    }, {
      id: 'lo-3',
      code: 'PO3',
      courseLearningOutcome: 'Разрабатывает и презентует итоговый учебный результат.',
      programLearningOutcome: 'Работает индивидуально и в команде, соблюдая академическую этику.',
      description: 'Студент готовит итоговый проект, эссе, лабораторный отчет или презентацию в зависимости от формата курса.'
    }],
    thematicPlan: createThematicPlanPreset(courseName, courseType),
    assessmentSystem: getAssessmentScheme(courseType),
    literature: getLiteraturePreset(courseType),
    teachingPhilosophy: getTeachingPhilosophy(courseType),
    coursePolicy: getCoursePolicyTemplate(),
    signatures: {
      preparedByName: details.approvedBy,
      preparedByPosition: details.deanName,
      preparedByDate: details.approvalDate,
      signatureImage: '',
      stampImage: ''
    }
  }
}

export function applyCourseDetailsToSyllabus(syllabus: Syllabus, details: CourseDetails): Syllabus {
  return {
    ...syllabus,
    titleInfo: titleInfoFromCourseDetails(details),
    courseDescription: details.courseDescription || syllabus.courseDescription,
    courseGoal: details.courseGoal || syllabus.courseGoal,
    signatures: {
      ...syllabus.signatures,
      preparedByName: details.approvedBy,
      preparedByPosition: details.deanName,
      preparedByDate: details.approvalDate
    }
  }
}
