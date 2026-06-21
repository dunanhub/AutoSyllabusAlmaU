<script setup lang="ts">
import { mdiAccountTieOutline, mdiBookOpenPageVariantOutline, mdiCheck, mdiQrcode, mdiSchoolOutline } from '@mdi/js'
import type { CourseDetails } from '~/utils/courseSyllabus'
import { courseDetailsFromSyllabus, createInitialCourseDetails } from '~/utils/courseSyllabus'
import type { Syllabus } from '~/types/syllabus'

const props = defineProps<{
  modelValue: boolean
  syllabus: Syllabus | null
  submitting?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [value: CourseDetails]
}>()

const form = reactive<CourseDetails>(createInitialCourseDetails())
const error = ref('')

const languageItems = [
  { title: 'KZ · Қазақша', value: 'KZ' },
  { title: 'RU · Русский', value: 'RU' },
  { title: 'EN · English', value: 'EN' }
]

function fill() {
  if (!props.syllabus) return
  Object.assign(form, courseDetailsFromSyllabus(props.syllabus))
  error.value = ''
}

watch(() => props.modelValue, (open) => {
  if (open) fill()
})

watch(() => props.syllabus?.id, fill)

function close() {
  emit('update:modelValue', false)
}

function validate() {
  if (!form.courseCode.trim() || !form.courseName.trim()) return 'Укажите код и название дисциплины.'
  if (!form.languageOfEducation) return 'Выберите язык обучения.'
  if (!form.semester.trim()) return 'Укажите семестр.'
  if (!form.educationalProgram.trim()) return 'Укажите образовательную программу.'
  if (!form.instructorName.trim()) return 'Укажите преподавателя.'
  if (form.instructorEmail.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.instructorEmail.trim())) return 'Введите корректный email преподавателя.'
  if (form.qrUrl.trim() && !/^https?:\/\/.+/i.test(form.qrUrl.trim())) return 'QR URL должен начинаться с http:// или https://.'
  return ''
}

function submit() {
  error.value = validate()
  if (error.value) return
  emit('submit', structuredClone(toRaw(form)))
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="980"
    scrollable
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card class="course-dialog">
      <v-card-title class="border-b border-white/10 px-5 py-4 sm:px-6">
        <div class="flex items-center gap-3">
          <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiBookOpenPageVariantOutline" /></v-avatar>
          <div>
            <p class="text-lg font-black">Редактировать дисциплину</p>
            <p class="text-xs text-medium-emphasis">Изменяются только базовые данные дисциплины и QR.</p>
          </div>
        </div>
      </v-card-title>

      <v-card-text class="px-5 py-5 sm:px-6">
        <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4">{{ error }}</v-alert>

        <section class="form-section">
          <div class="section-title"><v-icon :icon="mdiSchoolOutline" size="18" />Данные дисциплины</div>
          <div class="form-grid">
            <v-text-field v-model="form.courseCode" label="Код дисциплины" />
            <v-text-field v-model="form.courseName" label="Название дисциплины" />
            <v-select v-model="form.languageOfEducation" :items="languageItems" label="Язык обучения" />
            <v-text-field v-model="form.credits" label="Кредиты ECTS" type="number" />
            <v-text-field v-model="form.totalHours" label="Всего часов" type="number" />
            <v-text-field v-model="form.classroomHours" label="Аудиторные часы" type="number" />
            <v-text-field v-model="form.independentWorkHours" label="Самостоятельная работа" type="number" />
            <v-textarea v-model="form.prerequisites" label="Пререквизиты" rows="2" class="md:col-span-2" />
          </div>
        </section>

        <section class="form-section">
          <div class="section-title"><v-icon :icon="mdiBookOpenPageVariantOutline" size="18" />Учебные данные</div>
          <div class="form-grid">
            <v-text-field v-model="form.levelOfTraining" label="Уровень обучения" />
            <v-text-field v-model="form.semester" label="Семестр" />
            <v-text-field v-model="form.educationalProgram" label="Образовательная программа" class="md:col-span-2" />
            <v-text-field v-model="form.proficiencyLevel" label="Уровень владения языком" />
            <v-text-field v-model="form.formatOfTraining" label="Формат обучения" />
            <v-textarea v-model="form.timeAndPlace" label="Время и место занятий" rows="2" class="md:col-span-2" />
          </div>
        </section>

        <section class="form-section">
          <div class="section-title"><v-icon :icon="mdiAccountTieOutline" size="18" />Преподаватель</div>
          <div class="form-grid">
            <v-text-field v-model="form.instructorName" label="ФИО преподавателя" />
            <v-text-field v-model="form.instructorDegree" label="Степень / должность" />
            <v-text-field v-model="form.instructorEmail" label="Email" type="email" />
            <v-textarea v-model="form.instructorContacts" label="Контакты" rows="2" />
          </div>
        </section>

        <section class="form-section">
          <div class="section-title"><v-icon :icon="mdiQrcode" size="18" />Утверждение / QR</div>
          <div class="form-grid">
            <v-text-field v-model="form.approvedBy" label="Утвердил" />
            <v-text-field v-model="form.deanName" label="Декан / согласовано" />
            <v-text-field v-model="form.approvalDate" label="Дата утверждения" type="date" />
            <v-text-field v-model="form.qrUrl" label="QR URL" placeholder="https://..." />
          </div>
        </section>
      </v-card-text>

      <v-card-actions class="border-t border-white/10 px-5 py-4 sm:px-6">
        <v-spacer />
        <v-btn variant="text" class="text-none" :disabled="submitting" @click="close">Отмена</v-btn>
        <v-btn color="primary" class="text-none font-weight-bold" :prepend-icon="mdiCheck" :loading="submitting" @click="submit">
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.course-dialog {
  border: 1px solid rgba(var(--v-border-color), .1);
}
.form-section + .form-section {
  margin-top: 22px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: rgb(var(--v-theme-primary));
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.form-grid {
  display: grid;
  gap: 12px;
}
@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
