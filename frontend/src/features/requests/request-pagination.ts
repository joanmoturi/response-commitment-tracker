export function clampRequestPage(page: number, total: number, pageSize: number): number {
  const lastPage = Math.max(0, Math.ceil(total / pageSize) - 1);
  return Math.min(page, lastPage);
}
