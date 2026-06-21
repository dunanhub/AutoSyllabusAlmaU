export type TemplateMarkerType = 'text' | 'rich_text' | 'table' | 'list' | 'image' | 'link'

export interface TemplateMarkerDefinition {
  key: string
  label: string
  token: string
  type: TemplateMarkerType
  group: string
  description: string
  repeatable?: boolean
}

export const TEMPLATE_MARKER_GROUPS = [
  'Курс',
  'Преподаватель',
  'Ручной ввод',
  'Таблицы',
  'Списки',
  'Утверждение',
  'QR'
] as const

export const TEMPLATE_MARKERS: TemplateMarkerDefinition[] = [
  {
    label: 'Код и название дисциплины',
    key: 'course.code_and_name',
    token: '{{course.code_and_name}}',
    type: 'text',
    group: 'Курс',
    description: 'Код и полное название дисциплины.'
  },
  {
    label: 'ECTS',
    key: 'course.credits',
    token: '{{course.credits}}',
    type: 'text',
    group: 'Курс',
    description: 'Количество кредитов ECTS.'
  },
  {
    label: 'Всего часов',
    key: 'course.total_hours',
    token: '{{course.total_hours}}',
    type: 'text',
    group: 'Курс',
    description: 'Общий объём часов по дисциплине.'
  },
  {
    label: 'Аудиторные часы',
    key: 'course.classroom_hours',
    token: '{{course.classroom_hours}}',
    type: 'text',
    group: 'Курс',
    description: 'Количество аудиторных часов.'
  },
  {
    label: 'Самостоятельная работа',
    key: 'course.independent_hours',
    token: '{{course.independent_hours}}',
    type: 'text',
    group: 'Курс',
    description: 'Часы самостоятельной работы студента.'
  },
  {
    label: 'Пререквизиты',
    key: 'course.prerequisites',
    token: '{{course.prerequisites}}',
    type: 'text',
    group: 'Курс',
    description: 'Предварительные требования к курсу.'
  },
  {
    label: 'Уровень обучения',
    key: 'course.level',
    token: '{{course.level}}',
    type: 'text',
    group: 'Курс',
    description: 'Уровень обучения.'
  },
  {
    label: 'Семестр',
    key: 'course.semester',
    token: '{{course.semester}}',
    type: 'text',
    group: 'Курс',
    description: 'Семестр обучения.'
  },
  {
    label: 'Образовательная программа',
    key: 'course.program',
    token: '{{course.program}}',
    type: 'text',
    group: 'Курс',
    description: 'Название образовательной программы.'
  },
  {
    label: 'Формат обучения',
    key: 'course.format',
    token: '{{course.format}}',
    type: 'text',
    group: 'Курс',
    description: 'Формат обучения.'
  },
  {
    label: 'Время и место занятий',
    key: 'course.time_place',
    token: '{{course.time_place}}',
    type: 'text',
    group: 'Курс',
    description: 'Время и место проведения занятий.'
  },
  {
    label: 'ФИО преподавателя',
    key: 'teacher.full_name',
    token: '{{teacher.full_name}}',
    type: 'text',
    group: 'Преподаватель',
    description: 'ФИО преподавателя из профиля пользователя.'
  },
  {
    label: 'Email преподавателя',
    key: 'teacher.email',
    token: '{{teacher.email}}',
    type: 'text',
    group: 'Преподаватель',
    description: 'Email преподавателя из профиля пользователя.'
  },
  {
    label: 'Краткое описание курса',
    key: 'manual.course_description',
    token: '{{manual.course_description}}',
    type: 'rich_text',
    group: 'Ручной ввод',
    description: 'Краткое описание курса из конструктора силлабуса.'
  },
  {
    label: 'Цель курса',
    key: 'manual.course_goal',
    token: '{{manual.course_goal}}',
    type: 'rich_text',
    group: 'Ручной ввод',
    description: 'Цель курса из конструктора силлабуса.'
  },
  {
    label: 'Методы обучения',
    key: 'manual.teaching_methods',
    token: '{{manual.teaching_methods}}',
    type: 'rich_text',
    group: 'Ручной ввод',
    description: 'Методы обучения из конструктора силлабуса.'
  },
  {
    label: 'Философия преподавания',
    key: 'manual.teaching_philosophy',
    token: '{{manual.teaching_philosophy}}',
    type: 'rich_text',
    group: 'Ручной ввод',
    description: 'Философия преподавания и обучения.'
  },
  {
    label: 'Результаты обучения',
    key: 'table.learning_outcomes',
    token: '{{table.learning_outcomes}}',
    type: 'table',
    group: 'Таблицы',
    description: 'Готовая таблица результатов обучения.'
  },
  {
    label: 'Тематический план',
    key: 'table.weekly_plan',
    token: '{{table.weekly_plan}}',
    type: 'table',
    group: 'Таблицы',
    description: 'Готовая таблица тематического плана.'
  },
  {
    label: 'Критерии оценивания / Рубрика',
    key: 'table.rubric',
    token: '{{table.rubric}}',
    type: 'table',
    group: 'Таблицы',
    description: 'Таблица рубрики или критериев оценивания.'
  },
  {
    label: 'Обязательная литература',
    key: 'list.required_literature',
    token: '{{list.required_literature}}',
    type: 'list',
    group: 'Списки',
    description: 'Список обязательной литературы.'
  },
  {
    label: 'Дополнительная литература',
    key: 'list.additional_literature',
    token: '{{list.additional_literature}}',
    type: 'list',
    group: 'Списки',
    description: 'Список дополнительной литературы.'
  },
  {
    label: 'Интернет-ресурсы',
    key: 'list.internet_resources',
    token: '{{list.internet_resources}}',
    type: 'list',
    group: 'Списки',
    description: 'Список интернет-ресурсов.'
  },
  {
    label: 'Директор ОӘБ / УМУ',
    key: 'approval.director_name',
    token: '{{approval.director_name}}',
    type: 'text',
    group: 'Утверждение',
    description: 'Ответственный директор учебно-методического блока.'
  },
  {
    label: 'Програм-лидер',
    key: 'approval.program_leader',
    token: '{{approval.program_leader}}',
    type: 'text',
    group: 'Утверждение',
    description: 'Програм-лидер выбранной программы.'
  },
  {
    label: 'QR код',
    key: 'syllabus.qr',
    token: '{{syllabus.qr}}',
    type: 'image',
    group: 'QR',
    description: 'QR или ссылка на страницу силлабуса.'
  },
  {
    label: 'Ссылка на силлабус',
    key: 'syllabus.url',
    token: '{{syllabus.url}}',
    type: 'link',
    group: 'QR',
    description: 'URL страницы силлабуса.'
  }
]

export const TEMPLATE_MARKER_BY_KEY = Object.fromEntries(
  TEMPLATE_MARKERS.map(marker => [marker.key, marker])
) as Record<string, TemplateMarkerDefinition>
