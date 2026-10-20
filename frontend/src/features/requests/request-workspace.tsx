"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ErrorMessage } from "@/components/error-message";
import { api } from "@/lib/api-client";
import {
  trackedRequestListSchema,
  trackedRequestSchema,
  type TrackedRequest,
  type TrackedRequestList
} from "@/lib/contracts";
import { RequestForm, type RequestFormValues } from "./request-form";
import { clampRequestPage } from "./request-pagination";

type RequestFilter = "open" | "overdue" | "completed" | "all";

const PAGE_SIZE = 50;
const DATE_FORMAT = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short"
});

function displayDate(value: string): string {
  return DATE_FORMAT.format(new Date(value));
}

function RequestCard({
  request,
  busy,
  onUpdate,
  onComplete
}: {
  request: TrackedRequest;
  busy: boolean;
  onUpdate: (values: RequestFormValues) => Promise<boolean>;
  onComplete: (response: string | null) => Promise<boolean>;
}) {
  const [editing, setEditing] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [response, setResponse] = useState("");

  async function save(values: RequestFormValues): Promise<boolean> {
    const saved = await onUpdate(values);
    if (saved) setEditing(false);
    return saved;
  }

  async function complete(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (await onComplete(response.trim() || null)) {
      setCompleting(false);
      setResponse("");
    }
  }

  return (
    <article className="panel space-y-4" aria-labelledby={`request-${request.id}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 id={`request-${request.id}`} className="text-lg font-semibold">{request.title}</h3>
          <p className="mt-1 whitespace-pre-wrap break-words text-sm text-slate-300">{request.details}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {request.is_overdue && <span className="rounded-full bg-red-950 px-3 py-1 text-red-200">Overdue</span>}
          <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-200">
            {request.status === "open" ? "Open" : "Completed"}
          </span>
        </div>
      </div>
      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        <div><dt className="text-slate-400">Owner</dt><dd>{request.owner}</dd></div>
        <div>
          <dt className="text-slate-400">Deadline</dt>
          <dd><time dateTime={request.due_at}>{displayDate(request.due_at)}</time></dd>
        </div>
      </dl>
      {request.response && (
        <div className="rounded-lg border border-slate-800 p-3">
          <h4 className="text-sm font-medium">Recorded response</h4>
          <p className="mt-1 whitespace-pre-wrap break-words text-sm text-slate-300">{request.response}</p>
        </div>
      )}
      {request.status === "completed" && request.completed_at && (
        <p className="text-xs text-slate-400">
          Completed <time dateTime={request.completed_at}>{displayDate(request.completed_at)}</time>
        </p>
      )}
      {editing ? (
        <RequestForm
          key={`edit-${request.id}`}
          initial={{
            title: request.title,
            details: request.details,
            owner: request.owner,
            due_at: request.due_at
          }}
          submitLabel="Save changes"
          busy={busy}
          onSubmit={(values) => save(values)}
          onCancel={() => setEditing(false)}
        />
      ) : request.status === "open" && (
        <div className="flex flex-wrap gap-3 border-t border-slate-800 pt-4">
          <button className="text-sm text-sky-300 underline" type="button" onClick={() => setEditing(true)} disabled={busy}>
            Edit request
          </button>
          <button
            className="text-sm text-sky-300 underline"
            type="button"
            onClick={() => setCompleting((value) => !value)}
            disabled={busy}
          >
            {completing ? "Cancel completion" : "Record response / complete"}
          </button>
        </div>
      )}
      {completing && request.status === "open" && !editing && (
        <form onSubmit={complete} className="space-y-3 border-t border-slate-800 pt-4">
          <label className="block text-sm font-medium" htmlFor={`response-${request.id}`}>
            Response (optional)
          </label>
          <textarea
            id={`response-${request.id}`}
            className="input min-h-20"
            value={response}
            onChange={(event) => setResponse(event.target.value)}
            maxLength={4000}
            placeholder="Record what was sent or agreed"
          />
          <button className="button" type="submit" disabled={busy}>
            {busy ? "Completing..." : "Complete request"}
          </button>
        </form>
      )}
    </article>
  );
}

export function RequestWorkspace() {
  const [data, setData] = useState<TrackedRequestList | null>(null);
  const [filter, setFilter] = useState<RequestFilter>("open");
  const [searchText, setSearchText] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [refresh, setRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [mutating, setMutating] = useState(false);
  const [createFormVersion, setCreateFormVersion] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function loadRequests() {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({
        status: filter,
        limit: String(PAGE_SIZE),
        offset: String(page * PAGE_SIZE)
      });
      if (search) params.set("q", search);
      try {
        const result = await api.request(
          `/requests?${params.toString()}`,
          trackedRequestListSchema,
          { signal: controller.signal }
        );
        const clampedPage = clampRequestPage(page, result.total, PAGE_SIZE);
        if (clampedPage !== page) {
          setPage(clampedPage);
          return;
        }
        setData(result);
      } catch (cause: unknown) {
        if (!(cause instanceof DOMException && cause.name === "AbortError")) {
          setData(null);
          setError(cause instanceof Error ? cause.message : "Could not load requests.");
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    void loadRequests();
    return () => controller.abort();
  }, [filter, page, refresh, search]);

  async function saveNew(
    values: RequestFormValues,
    submissionKey: string | null
  ): Promise<boolean> {
    if (!submissionKey) {
      setError("Could not prepare a safe request submission. Please try again.");
      return false;
    }
    setCreating(true);
    setError(null);
    try {
      await api.request("/requests", trackedRequestSchema, {
        method: "POST",
        body: JSON.stringify({ ...values, submission_key: submissionKey })
      });
      setFilter("open");
      setSearch("");
      setSearchText("");
      setPage(0);
      setCreateFormVersion((value) => value + 1);
      setRefresh((value) => value + 1);
      return true;
    } catch (cause: unknown) {
      setError(cause instanceof Error ? cause.message : "Could not create the request.");
      return false;
    } finally {
      setCreating(false);
    }
  }

  async function updateRequest(id: string, values: RequestFormValues): Promise<boolean> {
    setMutating(true);
    setError(null);
    try {
      await api.request(`/requests/${id}`, trackedRequestSchema, {
        method: "PATCH",
        body: JSON.stringify(values)
      });
      setRefresh((value) => value + 1);
      return true;
    } catch (cause: unknown) {
      setError(cause instanceof Error ? cause.message : "Could not update the request.");
      return false;
    } finally {
      setMutating(false);
    }
  }

  async function completeRequest(id: string, response: string | null): Promise<boolean> {
    setMutating(true);
    setError(null);
    try {
      await api.request(`/requests/${id}/complete`, trackedRequestSchema, {
        method: "POST",
        body: JSON.stringify({ response })
      });
      setRefresh((value) => value + 1);
      return true;
    } catch (cause: unknown) {
      setError(cause instanceof Error ? cause.message : "Could not complete the request.");
      return false;
    } finally {
      setMutating(false);
    }
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(0);
    setSearch(searchText.trim());
  }

  const filters: { value: RequestFilter; label: string; count: number }[] = [
    { value: "open", label: "Open", count: data?.open_count ?? 0 },
    { value: "overdue", label: "Overdue", count: data?.overdue_count ?? 0 },
    { value: "completed", label: "Completed", count: data?.completed_count ?? 0 },
    { value: "all", label: "All", count: (data?.open_count ?? 0) + (data?.completed_count ?? 0) }
  ];

  return (
    <section className="space-y-6">
      <section className="panel" aria-labelledby="new-request-heading">
        <h2 id="new-request-heading" className="mb-4 text-xl font-semibold">Track a response</h2>
        <RequestForm
          key={`create-${createFormVersion}`}
          submitLabel="Create request"
          busy={creating}
          idempotent
          onSubmit={saveNew}
        />
      </section>

      <section aria-labelledby="requests-heading" className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="requests-heading" className="text-xl font-semibold">Requests</h2>
            <p className="mt-1 text-sm text-slate-400">Private to your account; owners are tracked by name or contact.</p>
          </div>
          <form onSubmit={submitSearch} className="flex w-full gap-2 sm:w-auto">
            <label className="sr-only" htmlFor="request-search">Search requests</label>
            <input
              id="request-search"
              className="input min-w-0 flex-1 sm:w-64"
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              maxLength={120}
              placeholder="Search requests or owners"
            />
            <button className="rounded-lg border border-slate-700 px-4 py-2" type="submit">Search</button>
          </form>
        </div>

        <div className="flex flex-wrap gap-2" role="group" aria-label="Filter requests">
          {filters.map((item) => (
            <button
              key={item.value}
              className={filter === item.value
                ? "rounded-full bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950"
                : "rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-200"}
              type="button"
              aria-pressed={filter === item.value}
              onClick={() => { setFilter(item.value); setPage(0); }}
            >
              {item.label} <span aria-label={`${item.count} requests`}>({item.count})</span>
            </button>
          ))}
        </div>

        <ErrorMessage message={error} />
        {loading ? (
          <p role="status" className="py-8 text-center text-slate-400">Loading requests...</p>
        ) : data?.items.length ? (
          <>
            <div className="space-y-4">
              {data.items.map((request) => (
                <RequestCard
                  key={request.id}
                  request={request}
                  busy={mutating}
                  onUpdate={(values) => updateRequest(request.id, values)}
                  onComplete={(response) => completeRequest(request.id, response)}
                />
              ))}
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
              <p>{data.total} matching {data.total === 1 ? "request" : "requests"}</p>
              <div className="flex gap-2">
                <button
                  className="rounded-lg border border-slate-700 px-3 py-2 disabled:opacity-50"
                  type="button"
                  onClick={() => setPage((value) => Math.max(0, value - 1))}
                  disabled={page === 0}
                >
                  Previous
                </button>
                <button
                  className="rounded-lg border border-slate-700 px-3 py-2 disabled:opacity-50"
                  type="button"
                  onClick={() => setPage((value) => value + 1)}
                  disabled={(page + 1) * PAGE_SIZE >= data.total}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        ) : data ? (
          <div className="panel py-10 text-center">
            <p className="font-medium">
              {search ? "No matching requests." : filter === "completed"
                ? "No completed requests yet."
                : filter === "overdue" ? "No overdue requests."
                  : filter === "all" ? "No requests yet." : "Nothing needs a response right now."}
            </p>
            <p className="mt-2 text-sm text-slate-400">
              {search ? "Try another search term." : "Create a request above to start tracking a response."}
            </p>
          </div>
        ) : null}
      </section>
    </section>
  );
}
