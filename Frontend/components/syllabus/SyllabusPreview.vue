<script setup lang="ts">
import type { Syllabus } from '~/types/syllabus'

const props = defineProps<{ syllabus: Syllabus }>()

function display(value: string | number | undefined) {
  return value === '' || value === undefined ? '—' : value
}

function displayLanguage(value: string | undefined) {
  return value === 'MULTI' ? 'RU / KZ / EN' : display(value)
}

function isAssessmentSummaryRow(topicModule: string) {
  const value = topicModule.toLowerCase()
  return value.includes('всего за теоретическое обучение') || value.includes('государственный экзамен') || value.includes('всего за курс')
}

const assessmentRows = computed(() => props.syllabus.assessmentSystem.filter(row => (row.topicModule || row.maxPercent || row.maxWeight || row.finalPoints) && !isAssessmentSummaryRow(row.topicModule)))
const assessmentSummaryRows = computed(() => props.syllabus.assessmentSystem.filter(row => isAssessmentSummaryRow(row.topicModule)))
const assessmentTotals = computed(() => ({
  weight: assessmentRows.value.reduce((sum, item) => sum + Number(item.maxWeight || 0), 0),
  points: assessmentRows.value.reduce((sum, item) => sum + Number(item.finalPoints || 0), 0)
}))
const theoryTotal = computed(() => {
  const row = assessmentSummaryRows.value.find(item => item.topicModule.toLowerCase().includes('теорет'))
  return row?.finalPoints ?? assessmentTotals.value.points
})
const stateExamTotal = computed(() => {
  const row = assessmentSummaryRows.value.find(item => item.topicModule.toLowerCase().includes('государ'))
  return row?.finalPoints ?? 0
})
</script>

<template>
  <article class="a4-document book-document mx-auto bg-white text-slate-950 shadow-[0_18px_48px_rgba(0,0,0,0.35)]">
    <header class="book-header">
      <div class="flex items-start justify-between gap-6">
        <div class="flex items-center gap-3">
          <span class="grid size-10 place-items-center bg-[#064e3b] text-lg font-black text-white">A</span>
          <div><p class="text-[13px] font-black tracking-wide">AlmaU</p><p class="text-[8px] uppercase tracking-[0.14em] text-slate-500">Almaty Management University</p></div>
        </div>
        <div class="text-right text-[8px] uppercase leading-4 text-slate-500"><p>Академический силлабус</p><p>A4 portrait</p></div>
      </div>
      <div class="mt-7 text-center">
        <p class="text-[9px] font-bold uppercase tracking-[0.22em] text-slate-500">Силлабус дисциплины</p>
        <h1 class="mt-3 text-xl font-bold uppercase leading-tight">{{ syllabus.titleInfo.codeAndName || 'Без названия' }}</h1>
        <p class="mt-3 text-[10px] font-semibold text-slate-600">{{ syllabus.titleInfo.educationalProgram }} · {{ syllabus.titleInfo.semester }} · {{ displayLanguage(syllabus.titleInfo.languageOfEducation) }}</p>
      </div>
    </header>

    <section class="document-section">
      <h3>1. Титульная информация</h3>
      <table class="document-table title-table"><tbody>
        <tr><th>Код и название дисциплины</th><td colspan="3">{{ display(syllabus.titleInfo.codeAndName) }}</td></tr>
        <tr><th>Кредиты</th><td>{{ display(syllabus.titleInfo.credits) }}</td><th>Всего часов</th><td>{{ display(syllabus.titleInfo.totalHours) }}</td></tr>
        <tr><th>Аудиторные часы</th><td>{{ display(syllabus.titleInfo.classroomHours) }}</td><th>Самостоятельная работа</th><td>{{ display(syllabus.titleInfo.independentWorkHours) }}</td></tr>
        <tr><th>Пререквизиты</th><td colspan="3">{{ display(syllabus.titleInfo.prerequisites) }}</td></tr>
        <tr><th>Уровень обучения</th><td>{{ display(syllabus.titleInfo.levelOfTraining) }}</td><th>Семестр</th><td>{{ display(syllabus.titleInfo.semester) }}</td></tr>
        <tr><th>Образовательная программа</th><td colspan="3">{{ display(syllabus.titleInfo.educationalProgram) }}</td></tr>
        <tr><th>Язык обучения</th><td>{{ displayLanguage(syllabus.titleInfo.languageOfEducation) }}</td><th>Уровень владения языком</th><td>{{ display(syllabus.titleInfo.proficiencyLevel) }}</td></tr>
        <tr><th>Формат обучения</th><td>{{ display(syllabus.titleInfo.formatOfTraining) }}</td><th>Время и место</th><td>{{ display(syllabus.titleInfo.timeAndPlace) }}</td></tr>
        <tr><th>Преподаватель</th><td>{{ display(syllabus.titleInfo.instructorName) }}</td><th>Ученая степень / должность</th><td>{{ display(syllabus.titleInfo.instructorDegree) }}</td></tr>
        <tr><th>Email</th><td>{{ display(syllabus.titleInfo.instructorEmail) }}</td><th>Контакты</th><td>{{ display(syllabus.titleInfo.instructorContacts) }}</td></tr>
      </tbody></table>
    </section>

    <section class="document-section">
      <h3>2. График занятий и задания</h3>
      <table class="document-table"><thead><tr><th>Неделя</th><th>Тема / модуль</th><th>Формат проведения занятий</th><th>Задание</th></tr></thead><tbody>
        <tr v-for="item in syllabus.classSchedule" :key="item.id"><td>{{ item.week }}</td><td>{{ display(item.topic) }}</td><td>{{ display(item.format) }}</td><td>{{ display(item.task) }}</td></tr>
      </tbody></table>
    </section>

    <section class="document-section">
      <h3>3. Описание курса</h3>
      <h4>3.1. Описание курса</h4><p>{{ display(syllabus.courseDescription) }}</p>
      <h4>3.2. Цель обучения</h4><p>{{ display(syllabus.courseGoal) }}</p>
    </section>

    <section class="document-section">
      <h3>4. Результаты обучения</h3>
      <table class="document-table"><thead><tr><th>Код</th><th>Результаты обучения курса</th><th>Результаты обучения ОП</th><th>Описание</th></tr></thead><tbody>
        <tr v-for="item in syllabus.learningOutcomes" :key="item.id"><td>{{ item.code }}</td><td>{{ display(item.courseLearningOutcome) }}</td><td>{{ display(item.programLearningOutcome) }}</td><td>{{ display(item.description) }}</td></tr>
      </tbody></table>
    </section>

    <section class="document-section">
      <h3>5. Тематический план</h3>
      <table class="document-table thematic-table"><thead><tr><th>Неделя</th><th>Тема / модуль</th><th>PO курса / PO ОП</th><th>Вопросы</th><th>Задания</th><th>Литература</th><th>Структура оценок</th></tr></thead><tbody>
        <tr v-for="item in syllabus.thematicPlan" :key="item.id"><td>{{ item.week }}</td><td>{{ display(item.topicModule) }}</td><td>{{ display(item.courseOutcome) }}</td><td>{{ display(item.questions) }}</td><td>{{ display(item.tasks) }}</td><td>{{ display(item.literature) }}</td><td>{{ display(item.gradeStructure) }}</td></tr>
      </tbody></table>
    </section>

    <section class="document-section">
      <h3>6. Система оценивания курса</h3>
      <table class="document-table"><thead><tr><th>Тема / модуль</th><th>Максимальный процент (%)</th><th>Максимальный вес (%)</th><th>Итоговые баллы</th></tr></thead><tbody>
        <tr v-for="item in assessmentRows" :key="item.id"><td>{{ display(item.topicModule) }}</td><td>{{ display(item.maxPercent) }}</td><td>{{ display(item.maxWeight) }}</td><td>{{ display(item.finalPoints) }}</td></tr>
        <tr v-for="item in assessmentSummaryRows" :key="`${item.id}-summary`"><th>{{ display(item.topicModule) }}</th><th>{{ display(item.maxPercent) }}</th><th>{{ display(item.maxWeight) }}</th><th>{{ display(item.finalPoints) }}</th></tr>
        <tr v-if="!assessmentSummaryRows.length"><th>Всего за теоретическое обучение</th><th>—</th><th>{{ assessmentTotals.weight }}</th><th>{{ theoryTotal }}</th></tr>
        <tr v-if="!assessmentSummaryRows.length"><th>Государственный экзамен</th><th>—</th><th>—</th><th>{{ stateExamTotal }}</th></tr>
        <tr v-if="!assessmentSummaryRows.length"><th>Всего за курс</th><th>—</th><th>{{ assessmentTotals.weight }}</th><th>{{ assessmentTotals.points }}</th></tr>
      </tbody></table>
    </section>

    <section class="document-section">
      <h3>7. Список литературы</h3>
      <h4>A. Обязательная литература</h4>
      <ol class="book-list"><li v-for="item in syllabus.literature.required.filter(Boolean)" :key="item">{{ item }}</li></ol>
      <h4>B. Дополнительная литература</h4>
      <ol class="book-list"><li v-for="item in syllabus.literature.additional.filter(Boolean)" :key="item">{{ item }}</li></ol>
      <h4>C. Интернет-ресурсы</h4>
      <ol class="book-list"><li v-for="item in syllabus.literature.internetResources.filter(Boolean)" :key="item">{{ item }}</li></ol>
    </section>

    <section class="document-section">
      <h3>8. Философия преподавания и обучения</h3>
      <p>{{ display(syllabus.teachingPhilosophy) }}</p>
    </section>

    <section class="document-section">
      <h3>9. Политика курса</h3>
      <h4>9.1. Освоение дисциплины предусматривает</h4><p>{{ display(syllabus.coursePolicy.masteringDiscipline) }}</p>
      <h4>9.2. Допустимо</h4><p>{{ display(syllabus.coursePolicy.allowed) }}</p>
      <h4>9.3. Недопустимо</h4><p>{{ display(syllabus.coursePolicy.notAllowed) }}</p>
      <h4>9.4. Этика экзамена</h4><p>{{ display(syllabus.coursePolicy.examEthics) }}</p>
      <h4>9.5. Информация и связь</h4><p>{{ display(syllabus.coursePolicy.informationCommunication) }}</p>
    </section>

    <section class="document-section">
      <h3>10. Подписи</h3>
      <table class="document-table"><tbody>
        <tr><th>Подготовил(а)</th><td>{{ display(syllabus.signatures.preparedByName) }}</td><th>Должность</th><td>{{ display(syllabus.signatures.preparedByPosition) }}</td></tr>
        <tr><th>Дата</th><td>{{ display(syllabus.signatures.preparedByDate) }}</td><th>Подпись</th><td>____________________</td></tr>
      </tbody></table>
      <div class="mt-6 flex gap-8">
        <div v-if="syllabus.signatures.signatureImage"><p class="mb-2 text-[10px] font-bold">Подпись</p><img :src="syllabus.signatures.signatureImage" alt="Подпись" class="max-h-20"></div>
        <div v-if="syllabus.signatures.stampImage"><p class="mb-2 text-[10px] font-bold">Печать</p><img :src="syllabus.signatures.stampImage" alt="Печать" class="max-h-24"></div>
      </div>
    </section>
  </article>
</template>

<style scoped>
.book-document { color: #0f172a; font-family: "Times New Roman", Times, serif; }
.book-header { border-bottom: 2px solid #0f172a; padding-bottom: 22px; }
.book-list { list-style: decimal; padding-left: 18px; font-size: 10px; line-height: 1.55; color: #334155; }
.book-list:empty::after { content: 'Не указано.'; color: #64748b; }
.thematic-table { font-size: 8px; }
.document-table td, .document-table th { white-space: pre-line; word-break: break-word; hyphens: auto; }
</style>
