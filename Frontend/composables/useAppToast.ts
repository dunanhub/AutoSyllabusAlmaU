export type ToastKind = 'success' | 'info' | 'error'

export interface AppToastMessage {
  id: number
  text: string
  kind: ToastKind
}

export function useAppToast() {
  const messages = useState<AppToastMessage[]>('app-toast-messages', () => [])

  function show(text: string, kind: ToastKind = 'info') {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    messages.value.push({ id, text, kind })
    setTimeout(() => dismiss(id), 3500)
  }

  function dismiss(id: number) {
    messages.value = messages.value.filter(message => message.id !== id)
  }

  return { messages, show, dismiss }
}
