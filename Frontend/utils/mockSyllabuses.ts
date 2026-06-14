import type {
  AssessmentRow,
  ClassScheduleRow,
  Syllabus,
  SyllabusLanguage,
  SyllabusStatus,
  ThematicPlanRow
} from '~/types/syllabus'

export const STORAGE_SCHEMA_VERSION = 3

export function createId(prefix = 'item'): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`
}

export function createClassSchedule(count = 15): ClassScheduleRow[] {
  return Array.from({ length: count }, (_, index) => ({
    id: createId('schedule'),
    week: String(index + 1),
    topic: '',
    format: '',
    task: ''
  }))
}

export function createThematicPlan(count = 15): ThematicPlanRow[] {
  return Array.from({ length: count }, (_, index) => ({
    id: createId('topic'),
    week: String(index + 1),
    topicModule: '',
    courseOutcome: '',
    questions: '',
    tasks: '',
    literature: '',
    gradeStructure: ''
  }))
}

export function calculateAssessmentPoints(maxPercent: number | string, maxWeight: number | string): number {
  return Number(((Number(maxPercent || 0) * Number(maxWeight || 0)) / 100).toFixed(2))
}

export function calculateCompletion(item: Syllabus): number {
  const values = [
    item.titleInfo.codeAndName,
    item.titleInfo.instructorName,
    item.titleInfo.educationalProgram,
    item.classSchedule.some(row => row.topic || row.task),
    item.courseDescription,
    item.courseGoal,
    item.learningOutcomes.some(row => row.courseLearningOutcome || row.programLearningOutcome),
    item.thematicPlan.some(row => row.topicModule || row.tasks),
    item.assessmentSystem.some(row => row.topicModule),
    item.literature.required.length || item.literature.additional.length || item.literature.internetResources.length,
    item.teachingPhilosophy,
    item.coursePolicy.masteringDiscipline,
    item.signatures.preparedByName
  ]

  return Math.round(values.filter(Boolean).length / values.length * 100)
}

export function createEmptySyllabus(): Syllabus {
  const syllabus: Syllabus = {
    id: '',
    status: 'draft',
    completion: 0,
    titleInfo: {
      codeAndName: '',
      credits: 5,
      totalHours: 150,
      classroomHours: 45,
      independentWorkHours: 105,
      prerequisites: '',
      levelOfTraining: 'Бакалавриат',
      semester: 'Осенний',
      educationalProgram: '',
      languageOfEducation: 'RU',
      proficiencyLevel: '',
      formatOfTraining: 'Очная',
      instructorName: '',
      instructorDegree: '',
      instructorEmail: '',
      instructorContacts: '',
      timeAndPlace: ''
    },
    classSchedule: createClassSchedule(),
    courseDescription: '',
    courseGoal: '',
    learningOutcomes: [{
      id: createId('lo'),
      code: 'PO1',
      courseLearningOutcome: '',
      programLearningOutcome: '',
      description: ''
    }],
    thematicPlan: createThematicPlan(),
    assessmentSystem: [{
      id: createId('assessment'),
      topicModule: 'Рубежный контроль 1',
      maxPercent: 100,
      maxWeight: 100,
      finalPoints: 100
    }],
    literature: {
      required: [],
      additional: [],
      internetResources: []
    },
    teachingPhilosophy: '',
    coursePolicy: {
      masteringDiscipline: '',
      allowed: '',
      notAllowed: '',
      examEthics: '',
      informationCommunication: ''
    },
    signatures: {
      preparedByName: '',
      preparedByPosition: '',
      preparedByDate: new Date().toISOString().slice(0, 10),
      signatureImage: '',
      stampImage: ''
    },
    createdAt: '',
    updatedAt: ''
  }

  syllabus.completion = calculateCompletion(syllabus)
  return syllabus
}

const scheduleTopics = [
  ['Кіріспе. Қазақстан тарихы курсының пәні, мақсаты және дереккөздері', 'Лекция / семинар', 'Силлабуспен танысу, тарихнамалық ұғымдар бойынша қысқаша эссе'],
  ['Ежелгі Қазақстан: тас дәуірі және қола дәуірі мәдениеттері', 'Лекция / практикум', 'Археологиялық мәдениеттер кестесін толтыру'],
  ['Сақ, ғұн, үйсін және қаңлы мемлекеттері', 'Семинар / дерекпен жұмыс', 'Дерек үзіндісін талдау және картаға түсіру'],
  ['Түркі дәуірі және ортағасырлық мемлекеттер', 'Лекция / пікірталас', 'Түркі қағанаттарының саяси құрылымын салыстыру'],
  ['Қазақ хандығының құрылуы және дамуы', 'Семинар', 'Қазақ хандығының тарихи маңызы бойынша аргументтер дайындау'],
  ['XVII-XVIII ғғ. қазақ қоғамы және жоңғар шапқыншылығы', 'Лекция / кейс', 'Ақтабан шұбырынды оқиғалары бойынша хронология'],
  ['Қазақстанның Ресей империясы құрамына кіруі', 'Семинар / дебат', 'Отарлық басқару реформаларын талдау'],
  ['XIX ғасырдағы ұлт-азаттық қозғалыстар', 'Лекция / семинар', 'Кенесары Қасымұлы қозғалысы бойынша дерек талдау'],
  ['XX ғасыр басындағы Қазақстан және Алаш қозғалысы', 'Workshop', 'Алаш бағдарламасының негізгі бағыттарын презентациялау'],
  ['Кеңестік кезең: индустрияландыру, ұжымдастыру және ашаршылық', 'Лекция / құжатпен жұмыс', '1930-жылдардағы әлеуметтік өзгерістер туралы аналитикалық жазба'],
  ['Екінші дүниежүзілік соғыс жылдарындағы Қазақстан', 'Семинар', 'Тыл еңбегі және майдандағы қазақстандықтар бойынша постер'],
  ['Соғыстан кейінгі Қазақстан және тың игеру', 'Лекция / талқылау', 'Тың игерудің демографиялық салдарын талдау'],
  ['Қазақстандағы қайта құру және тәуелсіздікке жол', 'Семинар / пікірталас', 'Желтоқсан оқиғасының тарихи бағасы бойынша эссе'],
  ['Тәуелсіз Қазақстан: мемлекеттілік және жаңғыру', 'Лекция / кейс', 'Конституциялық реформалар бойынша қысқаша шолу'],
  ['Қорытындылау. Қазіргі Қазақстанның тарихи жады және ұлттық бірегейлік', 'Презентация / рефлексия', 'Қорытынды жоба және жеке рефлексия']
]

const historyClassSchedule: ClassScheduleRow[] = scheduleTopics.map((row, index) => ({
  id: `schedule-history-${index + 1}`,
  week: String(index + 1),
  topic: row[0],
  format: row[1],
  task: row[2]
}))

const historyThematicPlan: ThematicPlanRow[] = scheduleTopics.map((row, index) => ({
  id: `theme-history-${index + 1}`,
  week: String(index + 1),
  topicModule: row[0],
  courseOutcome: `PO${(index % 4) + 1}`,
  questions: [
    'Негізгі тарихи ұғымдар мен кезеңдеу',
    'Саяси, әлеуметтік және мәдени өзгерістердің себеп-салдары',
    'Дереккөздерді сыни талдау және интерпретация'
  ].join('\n'),
  tasks: row[2],
  literature: `Негізгі әдебиет: Қазақстан тарихы. 1-5 томдар.\nҚосымша материалдар: апта ${index + 1} бойынша LMS-тағы деректер жинағы.`,
  gradeStructure: index === 7
    ? 'Рубежный контроль 1 — 15%'
    : index === 14
      ? 'Қорытынды жоба және презентация — 20%'
      : 'Семинар белсенділігі және тапсырма — 3-5%'
}))

const historyAssessments: AssessmentRow[] = [
  ['Семинарларға қатысу және белсенділік', 100, 10],
  ['Апталық жазбаша тапсырмалар', 100, 15],
  ['Дереккөздерді талдау жұмыстары', 100, 10],
  ['Карта және хронология тапсырмалары', 100, 5],
  ['Эссе: Алаш қозғалысының тарихи маңызы', 100, 10],
  ['Рубежный контроль 1', 100, 15],
  ['Workshop презентациясы', 100, 5],
  ['Топтық жоба', 100, 10],
  ['Рубежный контроль 2', 100, 10],
  ['Всего за теоретическое обучение', 100, 90],
  ['Государственный экзамен', 100, 10],
  ['Всего за курс', 100, 100]
].map(([topicModule, maxPercent, maxWeight], index) => ({
  id: `assessment-history-${index + 1}`,
  topicModule: String(topicModule),
  maxPercent,
  maxWeight,
  finalPoints: calculateAssessmentPoints(maxPercent, maxWeight)
}))

export const mockSyllabuses: Syllabus[] = [{
  id: 'syl-history-kazakhstan',
  status: 'ready',
  completion: 100,
  titleInfo: {
    codeAndName: 'HIS 1101 — История Казахстана',
    credits: 5,
    totalHours: 150,
    classroomHours: 45,
    independentWorkHours: 105,
    prerequisites: 'Школьный курс истории Казахстана и всемирной истории',
    levelOfTraining: 'Бакалавриат',
    semester: '1 семестр',
    educationalProgram: 'Все образовательные программы бакалавриата AlmaU',
    languageOfEducation: 'RU',
    proficiencyLevel: 'Академический русский / базовое понимание исторической терминологии',
    formatOfTraining: 'Очная / blended learning',
    instructorName: 'Смагулова Айжан Ерлановна',
    instructorDegree: 'к.и.н., ассоциированный профессор',
    instructorEmail: 'a.smagulova@almau.edu.kz',
    instructorContacts: 'Консультации: среда 15:00-17:00, LMS Moodle, корпоративная почта',
    timeAndPlace: 'Понедельник 09:00-11:50, аудитория 302'
  },
  classSchedule: historyClassSchedule,
  courseDescription: 'Курс “История Казахстана” направлен на формирование целостного понимания исторического развития Казахстана с древнейших времен до современности. Особое внимание уделяется анализу государственности, социально-экономических трансформаций, культурного наследия, национальной идентичности и места Казахстана в мировом историческом процессе.',
  courseGoal: 'Сформировать у студентов историческое мышление, навыки критического анализа источников и способность аргументированно объяснять ключевые этапы развития Казахстана.',
  learningOutcomes: [
    { id: 'lo-history-1', code: 'PO1', courseLearningOutcome: 'Объясняет основные этапы исторического развития Казахстана.', programLearningOutcome: 'Демонстрирует системное мышление и академическую грамотность.', description: 'Периодизация, ключевые события, причинно-следственные связи.' },
    { id: 'lo-history-2', code: 'PO2', courseLearningOutcome: 'Анализирует исторические источники и научные интерпретации.', programLearningOutcome: 'Применяет критическое мышление при работе с информацией.', description: 'Сравнение источников, выявление позиции автора и контекста.' },
    { id: 'lo-history-3', code: 'PO3', courseLearningOutcome: 'Оценивает роль Казахстана в региональных и глобальных процессах.', programLearningOutcome: 'Понимает социальную ответственность и гражданскую позицию.', description: 'Историческая память, идентичность, модернизация.' },
    { id: 'lo-history-4', code: 'PO4', courseLearningOutcome: 'Аргументирует собственную позицию по историческим проблемам.', programLearningOutcome: 'Эффективно коммуницирует письменно и устно.', description: 'Эссе, презентация, академическая дискуссия.' }
  ],
  thematicPlan: historyThematicPlan,
  assessmentSystem: historyAssessments,
  literature: {
    required: [
      'История Казахстана: учебник для вузов. В 5 томах. Алматы: Атамұра.',
      'Абусеитова М.Х. История Казахстана и Центральной Азии. Алматы.',
      'Козыбаев М.К. Казахстан на рубеже веков: размышления и поиски.'
    ],
    additional: [
      'Омарбеков Т. Голодомор в Казахстане: причины и последствия.',
      'Нурпеисов К. Алаш һәм Алашорда.',
      'Мартин В. Закон империи: Россия и кочевники Центральной Азии.'
    ],
    internetResources: [
      'https://e-history.kz — Портал “История Казахстана”',
      'https://archive.president.kz — Архив Президента Республики Казахстан',
      'https://adilet.zan.kz — Информационно-правовая система нормативных актов РК'
    ]
  },
  teachingPhilosophy: 'Преподавание курса строится на диалоге, анализе источников, сопоставлении исторических интерпретаций и связи исторического знания с современными общественными процессами. Студенты рассматриваются как активные участники академической дискуссии.',
  coursePolicy: {
    masteringDiscipline: 'Освоение дисциплины предусматривает регулярное посещение занятий, подготовку к семинарам, выполнение письменных работ, участие в обсуждениях, работу с историческими источниками и защиту итогового проекта.',
    allowed: 'Допустимо использовать академические базы данных, электронные библиотеки, LMS-материалы, командную работу в рамках заданий и консультации преподавателя.',
    notAllowed: 'Недопустимы плагиат, списывание, фальсификация источников, сдача чужих работ, некорректное цитирование и нарушение сроков без уважительной причины.',
    examEthics: 'Во время рубежного и итогового контроля запрещено использовать неразрешенные материалы, средства связи и помощь третьих лиц. Нарушения рассматриваются согласно академической политике AlmaU.',
    informationCommunication: 'Официальные каналы коммуникации: LMS, корпоративная почта преподавателя и объявления в электронном кабинете. Ответ преподавателя предоставляется в течение двух рабочих дней.'
  },
  signatures: {
    preparedByName: 'Смагулова А.Е.',
    preparedByPosition: 'Ассоциированный профессор Школы общественных наук',
    preparedByDate: '2026-06-01',
    signatureImage: '',
    stampImage: ''
  },
  createdAt: '2026-06-01T09:00:00.000Z',
  updatedAt: '2026-06-13T09:00:00.000Z'
}]

type LegacyRecord = Record<string, any>

export function normalizeSyllabus(source: LegacyRecord): Syllabus {
  if (source.titleInfo && source.classSchedule && source.thematicPlan && source.assessmentSystem) {
    const normalized = source as Syllabus
    normalized.status = normalized.status === 'ready' ? 'ready' : 'draft'
    normalized.completion = calculateCompletion(normalized)
    normalized.assessmentSystem = normalized.assessmentSystem.map(row => ({
      ...row,
      finalPoints: row.finalPoints === '' ? calculateAssessmentPoints(row.maxPercent, row.maxWeight) : row.finalPoints
    }))
    return normalized
  }

  const empty = createEmptySyllabus()
  const codeAndName = [source.courseCode, source.courseName || source.title].filter(Boolean).join(' — ')
  const language: SyllabusLanguage = ['KZ', 'RU', 'EN'].includes(source.language) ? source.language : 'RU'
  const status: SyllabusStatus = source.status === 'ready' || source.status === 'Ready' ? 'ready' : 'draft'
  const instructor = source.instructor || {}

  const migrated: Syllabus = {
    ...empty,
    id: String(source.id || createId('syl')),
    status,
    titleInfo: {
      ...empty.titleInfo,
      codeAndName,
      credits: source.credits ?? empty.titleInfo.credits,
      totalHours: source.totalHours ?? empty.titleInfo.totalHours,
      classroomHours: Number(source.lectureHours || 0) + Number(source.practicalHours || 0) || empty.titleInfo.classroomHours,
      independentWorkHours: source.individualWorkHours ?? empty.titleInfo.independentWorkHours,
      prerequisites: source.prerequisites || '',
      levelOfTraining: source.levelOfTraining || empty.titleInfo.levelOfTraining,
      semester: source.semester || empty.titleInfo.semester,
      educationalProgram: source.educationalProgram || '',
      languageOfEducation: language,
      proficiencyLevel: source.levelOfProficiency || '',
      formatOfTraining: source.formatOfTraining || empty.titleInfo.formatOfTraining,
      instructorName: instructor.name || source.instructorName || '',
      instructorDegree: instructor.position || source.instructorDegree || '',
      instructorEmail: instructor.email || source.instructorEmail || '',
      instructorContacts: instructor.contacts || source.instructorContacts || '',
      timeAndPlace: source.timeAndPlace || ''
    },
    courseDescription: source.courseDescription || '',
    courseGoal: source.courseObjective || '',
    createdAt: source.createdAt || new Date().toISOString(),
    updatedAt: source.updatedAt || new Date().toISOString()
  }

  migrated.completion = calculateCompletion(migrated)
  return migrated
}
