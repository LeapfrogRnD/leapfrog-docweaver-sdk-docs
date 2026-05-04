import { z } from 'zod';

export const pipelineSchema = z.object({
  name: z
    .string()
    .min(1, 'Pipeline name is required')
    .max(100, 'Pipeline name is too long')
    .refine((val) => val.trim().length > 0, 'Pipeline name cannot be only whitespace')
    .refine((val) => val === val.trim(), 'Pipeline name cannot start or end with whitespace'),
  description: z.string().max(200, 'Pipeline description is too long').optional().nullable(),
  parsing_method: z.string().optional().nullable(),
  ocr_provider: z.string().optional().nullable(),
  vlm_model_provider: z.string().optional().nullable(),
  vlm_model: z.string().optional().nullable(),
  llm_model_provider: z.string().min(1, 'LLM provider is required'),
  llm_model: z.string().min(1, 'LLM model is required'),
});

export type PipelineFormData = z.infer<typeof pipelineSchema>;
