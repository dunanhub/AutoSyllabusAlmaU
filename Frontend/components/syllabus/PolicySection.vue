<script setup lang="ts">
import type { CoursePolicy } from '~/types/syllabus'

const model = defineModel<CoursePolicy>({ required: true })
</script>

<template>
  <div class="grid gap-5">
    <BaseTextarea v-model="model.masteringDiscipline" label="Освоение дисциплины предусматривает" :rows="5" />
    <BaseTextarea v-model="model.allowed" label="Допустимо" :rows="4" />
    <BaseTextarea v-model="model.notAllowed" label="Недопустимо" :rows="4" />
    <BaseTextarea v-model="model.examEthics" label="Этика экзамена" :rows="4" />
    <BaseTextarea v-model="model.informationCommunication" label="Информация и связь" :rows="4" />
  </div>
</template>
