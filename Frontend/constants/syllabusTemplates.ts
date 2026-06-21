import type {
  AssessmentRow,
  ClassScheduleRow,
  CoursePolicy,
  LiteratureBlock,
  ThematicPlanRow
} from '~/types/syllabus'

export type CourseType =
  | 'default'
  | 'technical'
  | 'project'
  | 'laboratory'
  | 'seminar'
  | 'history'

export const DEFAULT_TEMPLATE_ID = ''

export const COURSE_TYPE_ITEMS = [
  { title: 'Стандартный академический курс', value: 'default' },
  { title: 'Технический / цифровой курс', value: 'technical' },
  { title: 'Проектный курс', value: 'project' },
  { title: 'Лабораторный курс', value: 'laboratory' },
  { title: 'Семинарский курс', value: 'seminar' },
  { title: 'Гуманитарный / исторический курс', value: 'history' }
]

export const SEMESTER_ITEMS = [
  '1 семестр',
  '2 семестр',
  '3 семестр',
  '4 семестр',
  '5 семестр',
  '6 семестр',
  '7 семестр',
  '8 семестр'
]

export const FORMAT_OF_TRAINING_ITEMS = [
  'Очная',
  'Blended',
  'Онлайн',
  'Вечерняя'
]

export const SYLLABUS_TEMPLATE_CATALOG: Array<{ id: string, title: string, description: string }> = []

const topicByType: Record<CourseType, string[]> = {
  default: [
    'Введение в дисциплину и требования курса',
    'Ключевые понятия и академический контекст',
    'Методы анализа и источники данных',
    'Практическое применение теории',
    'Кейс-анализ и командная работа',
    'Промежуточная подготовка к рубежному контролю',
    'Систематизация материалов курса',
    'RK1 / Midterm assessment',
    'Продвинутые темы дисциплины',
    'Исследовательские и прикладные задания',
    'Работа с источниками и доказательствами',
    'Проектирование итогового решения',
    'Презентации и обратная связь',
    'Финализация портфолио курса',
    'RK2 / Final project',
    'Exam'
  ],
  technical: [
    'Введение в цифровую дисциплину и среду разработки',
    'Архитектура решений и базовые инструменты',
    'Данные, алгоритмы и качество результата',
    'Практикум: проектирование модуля',
    'Интеграции и API-подход',
    'Тестирование и документация',
    'Подготовка к техническому рубежному контролю',
    'RK1 / Midterm assessment',
    'Безопасность, надежность и сопровождение',
    'Командная разработка и review',
    'Прототипирование технического решения',
    'Метрики и оценка эффективности',
    'Демо технического проекта',
    'Финализация и защита',
    'RK2 / Final project',
    'Exam'
  ],
  project: [
    'Введение в проектный формат курса',
    'Постановка проблемы и стейкхолдеры',
    'Исследование пользователей и контекста',
    'Формирование гипотез и критериев успеха',
    'Прототипирование решения',
    'Финансовая и операционная модель',
    'Подготовка к midterm pitch',
    'RK1 / Midterm assessment',
    'План реализации и риски',
    'Маркетинг и коммуникация проекта',
    'Аналитика результата',
    'Подготовка итогового deliverable',
    'Репетиция презентации',
    'Обратная связь и улучшения',
    'RK2 / Final project',
    'Exam'
  ],
  laboratory: [
    'Введение в лабораторный формат и безопасность',
    'Методология эксперимента',
    'Лабораторная работа 1',
    'Лабораторная работа 2',
    'Обработка и интерпретация результатов',
    'Лабораторная работа 3',
    'Подготовка к рубежному контролю',
    'RK1 / Midterm assessment',
    'Лабораторная работа 4',
    'Лабораторная работа 5',
    'Сравнение результатов и выводы',
    'Проектирование финального эксперимента',
    'Финальная лабораторная работа',
    'Защита лабораторного портфолио',
    'RK2 / Final project',
    'Exam'
  ],
  seminar: [
    'Введение в семинарский формат и критерии участия',
    'Академическое чтение и аргументация',
    'Семинарская дискуссия 1',
    'Семинарская дискуссия 2',
    'Аналитическое эссе',
    'Работа с кейсами',
    'Подготовка к рубежному контролю',
    'RK1 / Midterm assessment',
    'Дебаты и позиционный анализ',
    'Сравнительный анализ подходов',
    'Индивидуальная презентация',
    'Групповая дискуссия',
    'Исследовательский мини-проект',
    'Финальная консультация',
    'RK2 / Final project',
    'Exam'
  ],
  history: [
    'История Казахстана как академическая дисциплина',
    'Древняя история и ранние государственные образования',
    'Средневековые государства на территории Казахстана',
    'Казахское ханство и политическая культура',
    'Казахстан в составе Российской империи',
    'Национальная интеллигенция и движение Алаш',
    'Советская модернизация и ее последствия',
    'RK1 / Midterm assessment',
    'Казахстан в годы Второй мировой войны',
    'Послевоенное развитие и социальные изменения',
    'Перестройка и путь к независимости',
    'Становление Республики Казахстан',
    'Казахстан в глобальном мире',
    'Историческая память и идентичность',
    'RK2 / Final project',
    'Exam'
  ]
}

export function getTeachingPhilosophy(courseType: string) {
  const type = normalizeCourseType(courseType)
  if (type === 'project') {
    return 'Курс построен вокруг проектного обучения: студенты проходят путь от постановки проблемы до защиты решения. Преподаватель выступает фасилитатором, а оценивание связывается с качеством исследования, командной работы и итогового результата.'
  }
  if (type === 'technical' || type === 'laboratory') {
    return 'Философия курса основана на практике, доказательности и регулярной обратной связи. Студенты осваивают материал через задания, лабораторные работы, технические разборы и демонстрацию результата.'
  }
  if (type === 'seminar' || type === 'history') {
    return 'Курс развивает критическое мышление, академическое чтение, аргументацию и ответственное участие в дискуссиях. Особое внимание уделяется связи теории, источников и современного профессионального контекста.'
  }
  return 'Курс сочетает лекционные объяснения, практические задания, самостоятельную работу и регулярную обратную связь. Цель преподавания - сформировать академическую самостоятельность и способность применять знания в профессиональной среде.'
}

export function getCoursePolicyTemplate(): CoursePolicy {
  return {
    masteringDiscipline: 'Студент обязан регулярно посещать занятия, выполнять задания в установленные сроки, участвовать в обсуждениях и самостоятельно изучать рекомендованные источники.',
    allowed: 'Разрешается использовать электронные ресурсы AlmaU, библиотечные базы данных, академические источники, групповые обсуждения и инструменты ИИ при условии корректного раскрытия их использования.',
    notAllowed: 'Не допускаются плагиат, списывание, фабрикация данных, сдача чужой работы, нарушение сроков без уважительной причины и неэтичное использование генеративного ИИ.',
    examEthics: 'Во время экзамена и рубежного контроля студент обязан соблюдать академическую честность, выполнять инструкции преподавателя и не использовать неразрешенные материалы.',
    informationCommunication: 'Основные коммуникации ведутся через корпоративную почту AlmaU и LMS. Ответы на академические вопросы предоставляются в рабочее время или на консультациях.'
  }
}

export function getAssessmentScheme(courseType: string): AssessmentRow[] {
  const type = normalizeCourseType(courseType)
  const schemes: Record<CourseType, Array<[string, number, number]>> = {
    default: [
      ['Текущая работа и участие', 100, 20],
      ['Индивидуальные задания', 100, 20],
      ['RK1 / Midterm', 100, 20],
      ['RK2 / Final project', 100, 20],
      ['Final exam', 100, 20]
    ],
    technical: [
      ['Практические задания', 100, 25],
      ['Технические тесты', 100, 15],
      ['Лабораторные мини-проекты', 100, 20],
      ['RK1 / Midterm', 100, 20],
      ['Final exam', 100, 20]
    ],
    project: [
      ['Исследование проблемы', 100, 20],
      ['Проектный прототип', 100, 25],
      ['Командная презентация', 100, 20],
      ['Final project defense', 100, 25],
      ['Рефлексия и портфолио', 100, 10]
    ],
    laboratory: [
      ['Лабораторные работы', 100, 40],
      ['Отчеты и анализ данных', 100, 20],
      ['RK1 / Midterm', 100, 15],
      ['Финальная лабораторная защита', 100, 15],
      ['Final exam', 100, 10]
    ],
    seminar: [
      ['Участие в семинарах', 100, 20],
      ['Аналитические эссе', 100, 25],
      ['Кейс-разборы', 100, 20],
      ['RK1 / Midterm', 100, 15],
      ['Final exam', 100, 20]
    ],
    history: [
      ['Семинарские обсуждения', 100, 20],
      ['Работа с историческими источниками', 100, 20],
      ['Аналитическое эссе', 100, 20],
      ['RK1 / Midterm', 100, 20],
      ['Final exam', 100, 20]
    ]
  }

  return schemes[type].map(([topicModule, maxPercent, maxWeight], index) => ({
    id: `assessment-${type}-${index + 1}`,
    topicModule,
    maxPercent,
    maxWeight,
    finalPoints: Math.round((maxPercent * maxWeight) / 100)
  }))
}

export function createClassSchedulePreset(courseName: string, courseType: string): ClassScheduleRow[] {
  return topics(courseType).map((topic, index) => ({
    id: `schedule-${index + 1}`,
    week: String(index + 1),
    topic,
    format: index === 15 ? 'Exam' : index === 7 || index === 14 ? 'Рубежный контроль' : 'Лекция / семинар / практикум',
    task: taskForWeek(index, courseName)
  }))
}

export function createThematicPlanPreset(courseName: string, courseType: string): ThematicPlanRow[] {
  return topics(courseType).map((topic, index) => ({
    id: `topic-${index + 1}`,
    week: String(index + 1),
    topicModule: topic,
    courseOutcome: index < 5 ? 'LO1, LO2' : index < 11 ? 'LO2, LO3' : 'LO3, LO4',
    questions: defaultQuestions(topic),
    tasks: taskForWeek(index, courseName),
    literature: index < 8 ? 'Основная литература: 1-3' : 'Основная литература: 2-5; дополнительные источники',
    gradeStructure: index === 7 ? 'RK1 - 20%' : index === 14 ? 'RK2 / Final project - 20%' : index === 15 ? 'Exam - 20%' : 'Текущая работа'
  }))
}

export function getLiteraturePreset(courseType: string): LiteratureBlock {
  const type = normalizeCourseType(courseType)
  const required = [
    'AlmaU Academic Handbook. Internal academic policies and learning standards.',
    'Syllabus and course materials uploaded to the AlmaU LMS.',
    'Relevant peer-reviewed articles and official statistical or industry reports selected by the instructor.'
  ]

  if (type === 'history') {
    required.unshift('История Казахстана: учебник для организаций высшего образования. Алматы: Қазақ университеті.')
  }
  if (type === 'technical') {
    required.unshift('Pressman R., Maxim B. Software Engineering: A Practitioner’s Approach.')
  }

  return {
    required,
    additional: [
      'OECD, World Bank, UN, National Bureau of Statistics and other official analytical reports by course topic.',
      'Selected chapters from academic monographs and case studies provided during the semester.'
    ],
    internetResources: [
      'https://almau.edu.kz/',
      'https://adilet.zan.kz/',
      'https://scholar.google.com/'
    ]
  }
}

export function normalizeCourseType(value: string): CourseType {
  return COURSE_TYPE_ITEMS.some(item => item.value === value)
    ? value as CourseType
    : 'default'
}

function topics(courseType: string) {
  return topicByType[normalizeCourseType(courseType)]
}

function defaultQuestions(topic: string) {
  return `Ключевые понятия темы: ${topic}. Связь темы с результатами обучения и профессиональной практикой.`
}

function taskForWeek(index: number, courseName: string) {
  if (index === 7) return 'Подготовить материалы к RK1 / Midterm assessment.'
  if (index === 14) return 'Подготовить финальный проект, презентацию или итоговый аналитический материал.'
  if (index === 15) return 'Итоговая подготовка к экзамену и повторение ключевых тем курса.'
  return `Изучить материалы недели, выполнить задание по курсу «${courseName || 'дисциплина'}» и подготовить вопросы для обсуждения.`
}
