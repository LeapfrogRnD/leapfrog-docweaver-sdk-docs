import z from 'zod';

export const apiKeySchema = z.object({
  name: z.string().min(1, '').trim(),
  webhook_url: z
    .string()
    .trim()
    .optional()
    .transform((val) => (val === '' ? undefined : val))
    .refine(
      (val) => {
        if (!val) return true;
        return z.string().url().safeParse(val).success;
      },
      {
        message: 'Webhook must be a valid URL',
      }
    ),
});

export type ApiKeyFormData = z.infer<typeof apiKeySchema>;
