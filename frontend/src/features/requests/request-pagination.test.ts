import { describe, expect, it } from "vitest";
import { clampRequestPage } from "./request-pagination";

describe("request pagination", () => {
  it("moves back when a mutation removes the last item on a page", () => {
    expect(clampRequestPage(1, 50, 50)).toBe(0);
    expect(clampRequestPage(2, 101, 50)).toBe(2);
    expect(clampRequestPage(3, 0, 50)).toBe(0);
  });
});
