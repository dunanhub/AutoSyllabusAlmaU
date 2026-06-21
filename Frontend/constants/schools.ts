export interface AlmaUSchool {
  id: string
  nameRu: string
  nameKz: string
  nameEn: string
  deanName: string
  deputyDeanName: string
  programLeaderName: string
  approverTitleRu: string
  approverTitleKz: string
  approverTitleEn: string
}

export const APPROVAL_PLACEHOLDER = 'Будет заполнено академическим офисом'

export const ALMAU_SCHOOLS: AlmaUSchool[] = [
  {
    id: 'management',
    nameRu: 'Школа менеджмента',
    nameKz: 'Менеджмент мектебі',
    nameEn: 'The School of Management',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'digital-economics',
    nameRu: 'Школа цифровых технологий и экономики',
    nameKz: 'Цифрлық технологиялар және экономика мектебі',
    nameEn: 'School of Digital Technologies and Economics',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'law',
    nameRu: 'Институт права',
    nameKz: 'Құқық институты',
    nameEn: 'Institute of Law',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Директор института',
    approverTitleKz: 'Институт директоры',
    approverTitleEn: 'Institute Director'
  },
  {
    id: 'health-sciences',
    nameRu: 'Школа наук о здоровье имени Шарманова',
    nameKz: 'Шарманов атындағы денсаулық ғылымдары мектебі',
    nameEn: 'Sharmanov School of Health Sciences',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'media-film',
    nameRu: 'Школа медиа и кино',
    nameKz: 'Медиа және кино мектебі',
    nameEn: 'Media and Film School',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'entrepreneurship',
    nameRu: 'Институт предпринимательства',
    nameKz: 'Кәсіпкерлік институты',
    nameEn: 'Institute for Entrepreneurship',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Директор института',
    approverTitleKz: 'Институт директоры',
    approverTitleEn: 'Institute Director'
  },
  {
    id: 'hospitality-tourism',
    nameRu: 'Школа гостеприимства и туризма',
    nameKz: 'Қонақжайлылық және туризм мектебі',
    nameEn: 'School of Hospitality and Tourism',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'social-transformative-humanities',
    nameRu: 'Школа социальных наук и трансформативных гуманитарных дисциплин',
    nameKz: 'Әлеуметтік ғылымдар және трансформативті гуманитарлық пәндер мектебі',
    nameEn: 'School of Social Sciences and Transformative Humanities',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  },
  {
    id: 'gsb',
    nameRu: 'Высшая школа бизнеса',
    nameKz: 'Жоғары бизнес мектебі',
    nameEn: 'Graduate school of business',
    deanName: APPROVAL_PLACEHOLDER,
    deputyDeanName: APPROVAL_PLACEHOLDER,
    programLeaderName: APPROVAL_PLACEHOLDER,
    approverTitleRu: 'Декан школы',
    approverTitleKz: 'Мектеп деканы',
    approverTitleEn: 'Dean of School'
  }
]

export function findAlmaUSchool(id: string) {
  return ALMAU_SCHOOLS.find(school => school.id === id) || null
}
