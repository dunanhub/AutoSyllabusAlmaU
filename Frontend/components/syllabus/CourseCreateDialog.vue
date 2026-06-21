<script setup lang="ts">
import {
  mdiBookOpenPageVariantOutline,
  mdiCheck,
  mdiClockOutline,
  mdiFileDocumentOutline
} from '@mdi/js'
import type { CourseDetails } from '~/utils/courseSyllabus'
import { createInitialCourseDetails, splitCodeAndName } from '~/utils/courseSyllabus'

const props = defineProps<{
  modelValue: boolean
  submitting?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [value: CourseDetails]
}>()

const auth = useAuthStore()
const form = reactive<CourseDetails>(createInitialCourseDetails())
const error = ref('')

const instructorName = computed(() => {
  const firstName = auth.user?.first_name?.trim() || ''
  const lastName = auth.user?.last_name?.trim() || ''
  return [firstName, lastName].filter(Boolean).join(' ') || auth.user?.email || ''
})

const instructorEmail = computed(() => auth.user?.email || '')
const independentWorkAuto = computed(() => Math.max(Number(form.totalHours || 0) - Number(form.classroomHours || 0), 0))

function applyUserDefaults() {
  form.instructorName = instructorName.value
  form.instructorEmail = instructorEmail.value
  form.instructorContacts = instructorEmail.value
}

function reset() {
  Object.assign(form, createInitialCourseDetails())
  form.courseType = 'default'
  form.languageOfEducation = 'MULTI'
  form.schoolId = ''
  form.schoolName = ''
  form.courseGoal = ''
  form.approvedBy = ''
  form.deanName = ''
  form.qrUrl = ''
  error.value = ''
  applyUserDefaults()
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
})

watch([() => form.totalHours, () => form.classroomHours], () => {
  form.independentWorkHours = String(independentWorkAuto.value)
})

function close() {
  emit('update:modelValue', false)
}

function validate() {
  if (!form.courseCode.trim()) return 'Укажите код и название дисциплины.'
  if (!form.credits.trim()) return 'Укажите кредиты ECTS.'
  if (!form.totalHours.trim()) return 'Укажите общее количество часов.'
  if (!form.classroomHours.trim()) return 'Укажите аудиторные часы.'
  if (!form.levelOfTraining.trim()) return 'Укажите уровень обучения.'
  if (!form.semester.trim()) return 'Укажите семестр.'
  if (!form.educationalProgram.trim()) return 'Укажите образовательную программу.'
  if (!form.formatOfTraining.trim()) return 'Укажите формат обучения.'
  if (!form.timeAndPlace.trim()) return 'Укажите время и место занятий.'
  if (!form.courseDescription.trim()) return 'Добавьте описание курса.'
  return ''
}

function submit() {
  applyUserDefaults()
  const names = splitCodeAndName(form.courseCode)
  form.courseName = names.courseName || names.courseCode || form.courseCode
  form.languageOfEducation = 'MULTI'
  form.courseGoal = ''
  form.instructorContacts = form.instructorEmail
  form.independentWorkHours = String(independentWorkAuto.value)
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
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-3">
            <v-avatar color="primary" variant="tonal">
              <v-icon :icon="mdiBookOpenPageVariantOutline" />
            </v-avatar>
            <div>
              <p class="text-lg font-black">Создать дисциплину</p>
              <p class="text-xs text-medium-emphasis">
                Заполните поля, которые будут использоваться маркерами шаблона силлабуса.
              </p>
            </div>
          </div>
          <v-chip color="primary" variant="tonal" size="small">RU / KZ / EN</v-chip>
        </div>
      </v-card-title>

      <v-card-text class="px-5 py-5 sm:px-6">
        <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4">
          {{ error }}
        </v-alert>

        <div class="grid gap-5">
          <section class="form-section">
            <div class="section-heading">
              <v-icon :icon="mdiFileDocumentOutline" size="20" />
              <div>
                <h3>Курс</h3>
                <p>Основные академические данные дисциплины.</p>
              </div>
            </div>

            <div class="form-grid mt-5">
              <v-text-field
                v-model="form.courseCode"
                label="Код и название дисциплины"
                placeholder="HIS 1101 — История Казахстана"
                required
                class="md:col-span-2"
              />
              <v-text-field v-model="form.credits" label="Кредиты ECTS" type="number" required />
              <v-text-field v-model="form.totalHours" label="Всего часов" type="number" required />
              <v-text-field v-model="form.classroomHours" label="Аудиторные часы" type="number" required />
              <v-text-field v-model="form.independentWorkHours" label="Самостоятельная работа" type="number" readonly />
              <v-textarea v-model="form.prerequisites" label="Пререквизиты" rows="3" class="md:col-span-2" />
              <v-text-field v-model="form.levelOfTraining" label="Уровень обучения" required />
              <v-text-field v-model="form.semester" label="Семестр" required />
              <v-text-field v-model="form.educationalProgram" label="Образовательная программа" required />
              <v-text-field v-model="form.formatOfTraining" label="Формат обучения" required />
              <v-text-field v-model="form.timeAndPlace" label="Время и место занятий" required class="md:col-span-2" />
            </div>
          </section>

          <section class="form-section">
            <div class="section-heading">
              <v-icon :icon="mdiClockOutline" size="20" />
              <div>
                <h3>Описание курса</h3>
                <p>Это поле заполнит маркер <code v-pre>{{manual.course_description}}</code>.</p>
              </div>
            </div>

            <v-textarea
              v-model="form.courseDescription"
              label="Описание курса"
              rows="6"
              required
              class="mt-5"
            />
          </section>
        </div>
      </v-card-text>

      <v-card-actions class="border-t border-white/10 px-5 py-4 sm:px-6">
        <v-btn variant="text" class="text-none" :disabled="submitting" @click="close">
          Отмена
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          class="text-none font-weight-bold"
          :prepend-icon="mdiCheck"
          :loading="submitting"
          @click="submit"
        >
          Создать дисциплину
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.course-dialog {
  border: 1px solid rgba(var(--v-border-color), .1);
}
.form-section {
  border: 1px solid rgba(var(--v-border-color), .1);
  border-radius: 18px;
  background: rgba(var(--v-theme-surface-bright), .45);
  padding: 18px;
}
.section-heading {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.section-heading :deep(.v-icon) {
  color: rgb(var(--v-theme-primary));
  margin-top: 2px;
}
.section-heading h3 {
  font-size: 18px;
  font-weight: 900;
  letter-spacing: -.03em;
}
.section-heading p {
  margin-top: 4px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 13px;
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
