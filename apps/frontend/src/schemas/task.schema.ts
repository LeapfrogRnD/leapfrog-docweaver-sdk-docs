import { z } from 'zod';

// Task name schema (Step 1)
export const taskNameSchema = z.object({
  task_id: z.number().optional().nullable(),
  name: z.string().min(1, 'Task name is required').max(255, 'Task name is too long'),
});

// Presigned URL request schema (Step 2)
export const presignedUrlSchema = z.object({
  filename: z
    .string()
    .min(1, 'Filename is required')
    .refine(
      (filename) => {
        const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
        const extension = filename.toLowerCase().split('.').pop();
        return extension && allowedExtensions.includes(`.${extension}`);
      },
      {
        message: 'Only PDF and image files (JPG, JPEG, PNG) are allowed',
      }
    )
    .refine(
      (filename) => {
        const invalidChars = /[<>:"|?*\x00-\x1f]/;
        return !invalidChars.test(filename);
      },
      {
        message: 'Filename contains invalid characters',
      }
    )
    .refine(
      (filename) => {
        return filename.includes('.') && !filename.startsWith('.') && !filename.endsWith('.');
      },
      {
        message: 'Filename must have a valid extension',
      }
    ),
});

// Document upload confirmation schema
export const confirmDocUploadSchema = z.object({
  file_key: z.string().min(1, 'File key is required'),
});

// Extraction field schema
export const extractionFieldSchema = z.object({
  name: z.string().min(1, 'Field name is required'),
  type: z.string().min(1, 'Field type is required'),
  description: z.string().min(1, 'Field description is required'),
});

// Classification category schema
export const classificationCategorySchema = z.object({
  category: z.string().min(1, 'Category name is required'),
  fields: z
    .array(
      z.object({
        name: z.string().min(1, 'Field name is required'),
        title: z.string().min(1, 'Field title is required'),
        description: z.string().min(1, 'Field description is required'),
        example: z.string().min(1, 'Field example is required'),
      })
    )
    .min(1, 'At least one field is required'),
});

// Task configuration schema (Step 3)
export const taskConfigurationSchema = z.object({
  additional_instruction: z.string().optional(),
  task_type: z.enum(['extraction', 'classification', 'summarization'], {
    errorMap: () => ({ message: 'Please select a valid task type' }),
  }),
  json_schema: z.record(z.any()).refine(
    (schema) => {
      // Basic validation - more specific validation will be done in the component
      return Object.keys(schema).length > 0;
    },
    {
      message: 'JSON schema is required',
    }
  ),
  enableContext: z.boolean().optional(),
  pipeline_id: z
    .number({
      required_error: 'Pipeline selection is required',
      invalid_type_error: 'Please select a valid pipeline',
    })
    .min(1, 'Pipeline selection is required'),
});

// Combined form schema for the entire task creation flow
export const taskCreationFlowSchema = z
  .object({
    taskName: taskNameSchema.shape.name,

    uploadedFiles: z.array(z.instanceof(File)).min(1, 'At least one file must be uploaded'),

    additionalInstruction: taskConfigurationSchema.shape.additional_instruction,
    taskType: taskConfigurationSchema.shape.task_type,
    pipelineId: taskConfigurationSchema.shape.pipeline_id,
    enableContext: z.boolean().optional(),
    fileStatus: z.string().nullable().optional(),
    extractionFields: z.array(extractionFieldSchema).optional(),
    classificationCategories: z.array(classificationCategorySchema).optional(),
  })
  .refine(
    (data) => {
      if (data.taskType === 'extraction') {
        return data.extractionFields && data.extractionFields.length > 0;
      }
      if (data.taskType === 'classification') {
        return data.classificationCategories && data.classificationCategories.length > 0;
      }
      return true;
    },
    {
      message: 'Please configure fields for the selected task type',
      path: ['taskType'],
    }
  );

// Type exports
export type TaskNameFormData = z.infer<typeof taskNameSchema>;
export type PresignedUrlFormData = z.infer<typeof presignedUrlSchema>;
export type ConfirmDocUploadFormData = z.infer<typeof confirmDocUploadSchema>;
export type TaskConfigurationFormData = z.infer<typeof taskConfigurationSchema>;
export type TaskCreationFlowFormData = z.infer<typeof taskCreationFlowSchema>;
export type ExtractionFieldFormData = z.infer<typeof extractionFieldSchema>;
export type ClassificationCategoryFormData = z.infer<typeof classificationCategorySchema>;
