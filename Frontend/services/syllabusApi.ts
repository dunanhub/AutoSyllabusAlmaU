import type { Syllabus, SyllabusInput } from '~/types/syllabus'

// Контракт будущего API. Pinia store можно переключить на этот адаптер,
// не меняя компоненты и страницы приложения.
export interface SyllabusApi {
  getAll(): Promise<Syllabus[]>
  getById(id: string): Promise<Syllabus>
  create(payload: SyllabusInput): Promise<Syllabus>
  update(id: string, payload: Partial<SyllabusInput>): Promise<Syllabus>
  remove(id: string): Promise<void>
}
