export type SyllabusStatus = 'draft' | 'ready'
export type SyllabusLanguage = 'KZ' | 'RU' | 'EN'
export type SyllabusPdfStatus = 'not_generated' | 'processing' | 'generated' | 'failed'

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
  languageOfEducation: string
  proficiencyLevel: string
  formatOfTraining: string
  instructorName: string
  instructorDegree: string
  instructorEmail: string
  instructorContacts: string
  timeAndPlace: string
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
  pdfStatus?: SyllabusPdfStatus
  pdfGeneratedAt?: string | null
  pdfError?: string
  pdfTaskId?: string
  createdAt: string
  updatedAt: string
}

export type SyllabusInput = Omit<
  Syllabus,
  'id' | 'pdfFile' | 'pdfStatus' | 'pdfGeneratedAt' | 'pdfError' | 'pdfTaskId' | 'createdAt' | 'updatedAt'
>
