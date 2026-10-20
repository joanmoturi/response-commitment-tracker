import { afterEach, describe, expect, it } from "vitest";
import { deadlineIsoValue, localDateTimeValue } from "./request-dates";

const originalTimezone = process.env.TZ;

afterEach(() => {
  if (originalTimezone === undefined) delete process.env.TZ;
  else process.env.TZ = originalTimezone;
});

describe("request deadline conversion", () => {
  it("preserves the original instant when an edit leaves its local deadline unchanged", () => {
    process.env.TZ = "America/New_York";
    const ambiguousLocalTime = "2026-11-01T01:30";
    const laterOccurrence = "2026-11-01T06:30:00Z";
    expect(localDateTimeValue(laterOccurrence)).toBe(ambiguousLocalTime);
    expect(deadlineIsoValue(ambiguousLocalTime, ambiguousLocalTime, laterOccurrence))
      .toBe(laterOccurrence);
  });

  it("rejects nonexistent and ambiguous local times around clock changes", () => {
    process.env.TZ = "America/New_York";
    expect(deadlineIsoValue("2026-03-08T02:30", "", null)).toBeNull();
    expect(deadlineIsoValue("2026-11-01T01:30", "", null)).toBeNull();
  });
});
