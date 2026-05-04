import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui';
import { FileText, ArrowLeft, CheckCircle } from 'lucide-react';
import { useAuthOperations } from '@/hooks/useAuth';
import { useToast } from '@/context/ToastContext';
import { validateEmail } from '@/utils';

export function PasswordResetPage() {
  const [email, setEmail] = useState('');
  const [touched, setTouched] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { forgotPassword } = useAuthOperations();
  const { showToast } = useToast();

  const validation = useMemo(() => {
    const result = validateEmail(email);
    return {
      error: result.isValid ? undefined : result.error,
      isValid: result.isValid,
    };
  }, [email]);

  const { error, isValid } = validation;

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  const handleBlur = () => {
    setTouched(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setTouched(true);

    if (!isValid) {
      return;
    }

    forgotPassword.mutate(
      { email },
      {
        onSuccess: (response) => {
          setIsSubmitted(true);
          showToast(response.message || 'Password reset email sent successfully', 'success');
        },
        onError: (error: any) => {
          const errorMessage = error.response?.data?.message || 'Failed to send reset email';
          showToast(errorMessage, 'error');
        },
      }
    );
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10 px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#22c55e] rounded-2xl shadow-lg mb-4">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-semibold text-primary-black mb-2">Check Your Email</h1>
            <p className="text-gray-600 mb-6">
              If an account exists for this email, you will receive password reset instructions at:
            </p>
            <p className="text-lg font-medium text-[#038e43] mb-8">{email}</p>
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="text-sm text-gray-600 text-center">
                  <p>Didn't receive the email? Check your spam folder or</p>
                  <button
                    onClick={() => setIsSubmitted(false)}
                    className="text-[#038e43] hover:text-[#027235] font-medium"
                  >
                    try another email address
                  </button>
                </div>

                <Link to="/login" className="block">
                  <Button className="w-full">Back to Login</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10 px-4">
      <div className="w-full max-w-md">
        {/* Back to Login */}
        <Link
          to="/login"
          className="inline-flex items-center gap-2 text-sm text-[#6b7280] hover:text-[#038e43] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Login
        </Link>

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-brand rounded-2xl shadow-lg mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-semibold text-primary-black mb-2">Reset Password</h1>
          <p className="text-gray-600">Enter your email to receive reset instructions</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Forgot your password?</CardTitle>
            <CardDescription>No worries, we'll send you reset instructions</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Input
                  type="email"
                  label={
                    <>
                      Email <span className="text-red-500">*</span>
                    </>
                  }
                  placeholder="Enter your email address"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={handleBlur}
                  error={touched && error ? error : undefined}
                  className={touched && error ? 'border-red-500' : ''}
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={forgotPassword.isPending || !email || (touched && !isValid)}
              >
                {forgotPassword.isPending ? 'Sending...' : 'Send Reset Link'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Remember your password?{' '}
                <Link to="/login" className="text-[#038e43] hover:text-[#027235] font-medium">
                  Sign in
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
