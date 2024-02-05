export const isTauri = () => {
  return 'TAURI_ENV_PLATFORM' in import.meta.env
}
