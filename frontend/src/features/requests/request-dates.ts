export function localDateTimeValue(isoDate: string): string {
  const date = new Date(isoDate);
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

export function deadlineIsoValue(
  localValue: string,
  unchangedLocalValue: string,
  originalIsoValue: string | null
): string | null {
  if (originalIsoValue && localValue === unchangedLocalValue) return originalIsoValue;
  if (!localValue) return null;

  const parsed = new Date(localValue);
  if (Number.isNaN(parsed.getTime()) || localDateTimeValue(parsed.toISOString()) !== localValue) {
    return null;
  }

  for (let minutes = -180; minutes <= 180; minutes += 15) {
    if (minutes === 0) continue;
    const alternate = new Date(parsed.getTime() + minutes * 60_000);
    if (localDateTimeValue(alternate.toISOString()) === localValue) return null;
  }
  return parsed.toISOString();
}
