import { z } from 'zod';

export const userInviteSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  role: z.enum(['user', 'admin'], {
    required_error: 'Role is required',
  }),
});

export type UserInviteFormData = z.infer<typeof userInviteSchema>;
