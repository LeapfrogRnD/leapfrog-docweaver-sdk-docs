import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(6, 'Please enter a valid password')
    .refine((val) => val.trim().length > 0, 'Password cannot be only whitespace')
    .refine((val) => val === val.trim(), 'Password cannot start or end with whitespace'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export { loginSchema };
