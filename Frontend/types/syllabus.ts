export type SyllabusStatus = 'draft' | 'ready'
export type SyllabusLanguage = 'KZ' | 'RU' | 'EN' | 'MULTI'
export type SyllabusPdfStatus = 'not_generated' | 'processing' | 'generated' | 'failed'
export type SyllabusRenderTranslationStatus = 'not_translated' | 'translating' | 'completed' | 'failed'
export type SyllabusAiFillStatus = 'not_started' | 'processing' | 'completed' | 'failed'
export type DocumentLanguage = 'ru' | 'kz' | 'en'
export type DocumentFormat = 'pdf' | 'docx'

export interface PdfGenerationResponse {
  taskId: string
  status: 'processing'
}

export interface PdfStatusResponse {
  taskId: string
  pdfStatus: SyllabusPdfStatus
  pdfGeneratedAt: string | null
  pdfError: string
  pdfFile: string | null
  documents?: Record<DocumentLanguage, Record<DocumentFormat, boolean>>
}

export type DocumentAvailability = Record<DocumentLanguage, Record<DocumentFormat, boolean>>

export interface RenderTranslationResponse {
  taskId: string
  status: SyllabusRenderTranslationStatus
}

export interface RenderTranslationStatusResponse {
  taskId: string
  status: SyllabusRenderTranslationStatus
  error: string
  translatedAt: string | null
  renderedContent: string
  renderedContentKz: string
  renderedContentRu: string
  renderedContentEn: string
}

export interface AiFillResponse {
  taskId: string
  status: SyllabusAiFillStatus
}

export interface AiFillStatusResponse {
  taskId: string
  status: SyllabusAiFillStatus
  error: string
  filledAt: string | null
  syllabus: Syllabus
}

export interface SyllabusTitleInfo {
  codeAndName: string
  credits: number | string
  totalHours: number | string
  classroomHours: number | string
  independentWorkHours: number | string
  prerequisites: string
  levelOfTraining: string
  semester: string
  educationalProgram: string
  schoolId: string
  schoolName: string
  courseType: string
  templateId: string
  languageOfEducation: string
  proficiencyLevel: string
  formatOfTraining: string
  instructorName: string
  instructorDegree: string
  instructorEmail: string
  instructorContacts: string
  timeAndPlace: string
  qrUrl: string
}

export interface ClassScheduleRow {
  id: string
  week: string
  topic: string
  format: string
  task: string
}

export interface LearningOutcomeRow {
  id: string
  code: string
  courseLearningOutcome: string
  programLearningOutcome: string
  description: string
}

export interface ThematicPlanRow {
  id: string
  week: string
  topicModule: string
  courseOutcome: string
  questions: string
  tasks: string
  literature: string
  gradeStructure: string
}

export interface AssessmentRow {
  id: string
  topicModule: string
  maxPercent: number | string
  maxWeight: number | string
  finalPoints: number | string
}

export interface LiteratureBlock {
  required: string[]
  additional: string[]
  internetResources: string[]
}

export interface CoursePolicy {
  masteringDiscipline: string
  allowed: string
  notAllowed: string
  examEthics: string
  informationCommunication: string
}

export interface SignatureBlock {
  preparedByName: string
  preparedByPosition: string
  preparedByDate: string
  signatureImage?: string
  stampImage?: string
}

export interface Syllabus {
  id: string
  status: SyllabusStatus
  completion: number
  titleInfo: SyllabusTitleInfo
  classSchedule: ClassScheduleRow[]
  courseDescription: string
  courseGoal: string
  learningOutcomes: LearningOutcomeRow[]
  thematicPlan: ThematicPlanRow[]
  assessmentSystem: AssessmentRow[]
  literature: LiteratureBlock
  teachingPhilosophy: string
  coursePolicy: CoursePolicy
  signatures: SignatureBlock
  pdfFile?: string | null
  pdfFileRu?: string | null
  pdfFileKz?: string | null
  pdfFileEn?: string | null
  docxFileRu?: string | null
  docxFileKz?: string | null
  docxFileEn?: string | null
  documents?: DocumentAvailability
  pdfStatus?: SyllabusPdfStatus
  pdfGeneratedAt?: string | null
  pdfError?: string
  pdfTaskId?: string
  constructorSavedAt?: string | null
  renderedContent?: string
  renderedContentKz?: string
  renderedContentRu?: string
  renderedContentEn?: string
  renderTranslationStatus?: SyllabusRenderTranslationStatus
  renderTranslationError?: string
  renderTranslatedAt?: string | null
  renderTranslationTaskId?: string
  aiFillStatus?: SyllabusAiFillStatus
  aiFillError?: string
  aiFillTaskId?: string
  aiFilledAt?: string | null
  createdAt: string
  updatedAt: string
}

export type SyllabusInput = Omit<
  Syllabus,
  'id' | 'pdfFile' | 'pdfFileRu' | 'pdfFileKz' | 'pdfFileEn'
  | 'docxFileRu' | 'docxFileKz' | 'docxFileEn'
  | 'pdfStatus' | 'pdfGeneratedAt' | 'pdfError' | 'pdfTaskId'
  | 'constructorSavedAt' | 'renderedContent' | 'renderedContentKz' | 'renderedContentRu'
  | 'renderedContentEn' | 'renderTranslationStatus' | 'renderTranslationError'
  | 'renderTranslatedAt' | 'renderTranslationTaskId' | 'aiFillStatus' | 'aiFillError'
  | 'aiFillTaskId' | 'aiFilledAt' | 'createdAt' | 'updatedAt'
>
