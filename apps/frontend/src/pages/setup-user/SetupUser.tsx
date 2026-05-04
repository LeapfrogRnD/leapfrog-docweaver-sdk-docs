import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { Button, Input, Card, CardContent } from '@/components/ui';
import { Spinner } from '@/components/ui';
import { FileText, Mail, CheckCircle, LogOut } from 'lucide-react';
import { sendVerificationEmail } from '@/services/user.service';

const emailVerificationSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

type EmailVerificationFormData = z.infer<typeof emailVerificationSchema>;

export function SetupPage() {
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<EmailVerificationFormData>({
    resolver: zodResolver(emailVerificationSchema),
    defaultValues: {
      email: '',
    },
  });

  const { showToast } = useToast();
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const email = watch('email');
  const isLoading = isSubmitting;
  const isFormValid = !!email && email.trim().length > 0 && !errors.email && email.includes('@');

  const handleLogout = async () => {
    try {
      await logout();
      showToast('Logged out successfully', 'success');
      navigate('/login');
    } catch (error) {
      showToast('Failed to logout', 'error');
    }
  };

  const onSubmit = async (data: EmailVerificationFormData) => {
    try {
      const success = await sendVerificationEmail(data.email);
      if (success) {
        setEmailSent(true);
        showToast(
          `Verification email sent to ${data.email}. Please check your inbox and click the link to continue.`,
          'success'
        );
      } else {
        showToast('Failed to send verification email. Please try again.', 'error');
      }
    } catch (err) {
      showToast('An error occurred while sending email. Please try again.', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10">
      {/* Header with Logout */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-primary-brand mr-3" />
              <h2 className="text-lg font-semibold text-primary-black">Account Setup</h2>
            </div>
            <div className="flex items-center gap-4">
              {user?.email && <span className="text-sm text-gray-600">{user.email}</span>}
              <Button variant="outline" onClick={handleLogout} className="flex items-center gap-2">
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex items-center justify-center px-4 py-8 min-h-[calc(100vh-4rem)]">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-brand rounded-2xl shadow-lg mb-4">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-semibold text-primary-black mb-2">Verify Your Email</h1>
            <p className="text-gray-600">
              Please verify your email address to continue setting up your account
            </p>
          </div>

          <Card>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-4">
                <div>
                  <Input
                    {...register('email')}
                    type="email"
                    label="Email Address"
                    placeholder="Enter your email address"
                    required
                  />
                  {errors.email && (
                    <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>
                  )}
                  {emailSent && (
                    <p className="mt-2 text-xs text-green-600 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Verification email sent. Please check your inbox.
                    </p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isLoading || emailSent || !isFormValid}
                >
                  {isLoading ? (
                    <>
                      <Spinner size="sm" />
                      Sending...
                    </>
                  ) : emailSent ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Email Sent
                    </>
                  ) : (
                    <>
                      <Mail className="w-4 h-4 mr-2" />
                      Send Verification Email
                    </>
                  )}
                </Button>

                {emailSent && (
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>Next Step:</strong> Click the verification link in your email to
                        complete your profile setup.
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={handleSubmit(onSubmit)}
                      className="text-sm text-[#038e43] hover:text-[#027235] font-medium w-full"
                      disabled={isLoading}
                    >
                      Resend verification email
                    </button>
                  </div>
                )}
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
