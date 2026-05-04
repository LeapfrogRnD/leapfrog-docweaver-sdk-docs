import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Loader2 } from 'lucide-react';

import { Button, Card, CardContent } from '@/components/ui';
import { Form } from '@/components/ui/form'; // Added for context
import { WatchedInput } from '@/components/ui/WatchedInput'; // Added for email
import FormSelect from '@/components/ui/FormSelect';

import { useInviteUser } from '@/queries/user.query';
import { useToast } from '@/context/ToastContext';
import { userInviteSchema, UserInviteFormData } from '@/schemas/user.schema';

const ROLE_OPTIONS = {
  user: 'User',
  admin: 'Admin',
};

/**
 * 1. RegisterUserModal
 */
export function RegisterUserModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const form = useForm<UserInviteFormData>({
    resolver: zodResolver(userInviteSchema),
    defaultValues: {
      email: '',
      role: 'user',
    },
  });

  const {
    handleSubmit,
    reset,
    watch,
    control,
    formState: { isSubmitting },
  } = form;
  const { showToast } = useToast();
  const inviteMutation = useInviteUser();

  const email = watch('email');
  const isLoading = isSubmitting || inviteMutation.isPending;

  useEffect(() => {
    if (isOpen) reset({ email: '', role: 'user' });
  }, [isOpen, reset]);

  if (!isOpen) return null;

  const onSubmit = async (data: UserInviteFormData) => {
    try {
      const result = await inviteMutation.mutateAsync({
        email: data.email,
        role: data.role,
      });

      if (result.success) {
        showToast(result.message || 'User invited successfully.', 'success');
        reset();
        onClose();
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'An error occurred.', 'error');
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && !isLoading && onClose()}
    >
      <div className="relative w-full max-w-lg mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-[#111]">Invite New User</h2>
          <p className="text-sm text-[#6b7280] mt-1">
            Send an invitation email to add a member to your team.
          </p>
        </div>

        <Form {...form}>
          <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5">
            <div className="space-y-5">
              <WatchedInput
                control={control}
                name="email"
                label="Email Address"
                placeholder="name@company.com"
                required={true}
              />

              <FormSelect control={control} name="role" label="Role" options={ROLE_OPTIONS} />
            </div>

            <div className="flex gap-3 mt-8 pt-5 border-t border-gray-100">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-[#038e43] hover:bg-[#027235]"
                disabled={isLoading || !email?.includes('@')}
              >
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Send Invite'}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}

/**
 * 2. RegisterUserPage
 */
export function RegisterUserPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const inviteMutation = useInviteUser();

  const form = useForm<UserInviteFormData>({
    resolver: zodResolver(userInviteSchema),
    defaultValues: { email: '', role: 'user' },
  });

  const {
    handleSubmit,
    reset,
    watch,
    control,
    formState: { isSubmitting },
  } = form;
  const email = watch('email');
  const isLoading = isSubmitting || inviteMutation.isPending;

  const onSubmit = async (data: UserInviteFormData) => {
    try {
      const result = await inviteMutation.mutateAsync({
        email: data.email,
        role: data.role,
      });

      if (result.success) {
        showToast(result.message || 'User invited successfully.', 'success');
        reset();
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'An error occurred.', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-[#fafafa] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto">
        <div className="mb-10 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-[#038e43] rounded-2xl flex items-center justify-center shadow-lg mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Invite User</h1>
          <p className="text-gray-500 mt-2">Add a new member to your organization.</p>
        </div>

        <Card className="border-none shadow-md">
          <CardContent className="pt-8">
            <Form {...form}>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <WatchedInput
                  control={control}
                  name="email"
                  label="Email Address"
                  placeholder="name@company.com"
                  required={true}
                />

                <FormSelect control={control} name="role" label="Role" options={ROLE_OPTIONS} />

                <div className="flex gap-4 pt-6 border-t border-gray-100">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate(-1)}
                    disabled={isLoading}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-[#038e43] hover:bg-[#027235]"
                    disabled={isLoading || !email?.includes('@')}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      'Send Invitation'
                    )}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
