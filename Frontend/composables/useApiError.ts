export interface ApiErrorPayload {
  status?: number
  message: string
}

export function useApiError() {
  const { show } = useAppToast()

  function messageFor(status?: number) {
    if (status === 401) return 'Сессия истекла. Выполните вход снова.'
    if (status === 403) return 'Недостаточно прав для выполнения операции.'
    if (status === 404) return 'Запрашиваемый ресурс не найден.'
    if (status === 500) return 'Ошибка сервера. Попробуйте позже.'
    return 'Ошибка сети. Проверьте подключение.'
  }

  function handle(error: unknown) {
    const status = (error as { status?: number })?.status
    show(messageFor(status), 'error')
    return { status, message: messageFor(status) } satisfies ApiErrorPayload
  }

  return { handle, messageFor }
}
