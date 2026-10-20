"use client";

import { useId, useRef, useState, type FormEvent } from "react";
import { deadlineIsoValue, localDateTimeValue } from "./request-dates";

export interface RequestFormValues {
  title: string;
  details: string;
  owner: string;
  due_at: string;
}

interface RequestFormProps {
  initial?: RequestFormValues;
  submitLabel: string;
  busy: boolean;
  idempotent?: boolean;
  onSubmit: (values: RequestFormValues, submissionKey: string | null) => Promise<boolean>;
  onCancel?: () => void;
}

export function RequestForm({
  initial,
  submitLabel,
  busy,
  idempotent = false,
  onSubmit,
  onCancel
}: RequestFormProps) {
  const id = useId();
  const submissionKey = useRef<string | null>(null);
  const [title, setTitle] = useState(initial?.title ?? "");
  const [details, setDetails] = useState(initial?.details ?? "");
  const [owner, setOwner] = useState(initial?.owner ?? "");
  const [originalDueAt] = useState(initial?.due_at ?? null);
  const [originalLocalDueAt] = useState(
    () => initial ? localDateTimeValue(initial.due_at) : ""
  );
  const [dueAt, setDueAt] = useState(originalLocalDueAt);
  const [validationError, setValidationError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError(null);
    const deadline = deadlineIsoValue(dueAt, originalLocalDueAt, originalDueAt);
    if (!deadline) {
      setValidationError("Choose a valid local time that is not ambiguous during a clock change.");
      return;
    }
    const key = idempotent ? (submissionKey.current ?? crypto.randomUUID()) : null;
    if (idempotent) submissionKey.current = key;
    const saved = await onSubmit({
      title: title.trim(),
      details: details.trim(),
      owner: owner.trim(),
      due_at: deadline
    }, key);
    if (saved && idempotent) submissionKey.current = null;
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium" htmlFor={`${id}-title`}>Request</label>
        <input
          id={`${id}-title`}
          className="input"
          value={title}
          onChange={(event) => { submissionKey.current = null; setTitle(event.target.value); }}
          required
          maxLength={160}
          placeholder="What response or action is needed?"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium" htmlFor={`${id}-details`}>Details</label>
        <textarea
          id={`${id}-details`}
          className="input min-h-24"
          value={details}
          onChange={(event) => { submissionKey.current = null; setDetails(event.target.value); }}
          required
          maxLength={4000}
          placeholder="Add context for the expected response"
        />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium" htmlFor={`${id}-owner`}>Owner</label>
          <input
            id={`${id}-owner`}
            className="input"
            value={owner}
            onChange={(event) => { submissionKey.current = null; setOwner(event.target.value); }}
            required
            maxLength={160}
            placeholder="Name or contact"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium" htmlFor={`${id}-due`}>Response deadline</label>
          <input
            id={`${id}-due`}
            className="input"
            type="datetime-local"
            step={60}
            value={dueAt}
            onChange={(event) => { submissionKey.current = null; setDueAt(event.target.value); }}
            required
          />
        </div>
      </div>
      <p className="text-xs text-slate-400">Deadline is entered in your local time and stored in UTC.</p>
      {validationError && <p role="alert" className="text-sm text-red-300">{validationError}</p>}
      <div className="flex flex-wrap gap-3">
        <button className="button" type="submit" disabled={busy}>
          {busy ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button className="rounded-lg border border-slate-700 px-4 py-2" type="button" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
