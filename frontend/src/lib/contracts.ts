import { z } from "zod";

export const userSchema = z.object({ id: z.string().uuid(), email: z.string().email() });
export const authSchema = z.object({
  access_token: z.string().min(1),
  token_type: z.literal("bearer"),
  user: userSchema
});
export const providersSchema = z.object({
  local: z.boolean(),
  registration_enabled: z.boolean(),
  oidc: z.boolean()
});
export const runSchema = z.object({
  id: z.string().uuid(),
  status: z.enum(["pending", "running", "completed", "failed"]),
  answer: z.string().nullable(),
  error: z.string().nullable(),
  steps: z.number().int().nonnegative()
});
export const trackedRequestSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  details: z.string(),
  owner: z.string(),
  due_at: z.string().datetime({ offset: true }),
  status: z.enum(["open", "completed"]),
  response: z.string().nullable(),
  completed_at: z.string().datetime({ offset: true }).nullable(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
  is_overdue: z.boolean()
});
export const trackedRequestListSchema = z.object({
  items: z.array(trackedRequestSchema),
  total: z.number().int().nonnegative(),
  open_count: z.number().int().nonnegative(),
  overdue_count: z.number().int().nonnegative(),
  completed_count: z.number().int().nonnegative()
});

export type User = z.infer<typeof userSchema>;
export type AuthSession = z.infer<typeof authSchema>;
export type AgentRun = z.infer<typeof runSchema>;
export type TrackedRequest = z.infer<typeof trackedRequestSchema>;
export type TrackedRequestList = z.infer<typeof trackedRequestListSchema>;
