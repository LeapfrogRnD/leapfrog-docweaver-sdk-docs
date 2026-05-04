import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui';
import { Lock, ArrowLeft, Eye, EyeOff, AlertCircle, Check } from 'lucide-react';
import { useAuthOperations } from '@/hooks/useAuth';
import { useToast } from '@/context/ToastContext';

export function PasswordUpdatePage() {
  const [searchParams] = useSearchParams();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [touched, setTouched] = useState({
    newPassword: false,
    confirmPassword: false,
  });

  const { resetPassword } = useAuthOperations();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      showToast('Invalid or missing reset token', 'error');
      navigate('/login');
    }
  }, [token, navigate, showToast]);

  const validation = useMemo(() => {
    const errors: { newPassword?: string; confirmPassword?: string } = {};

    if (newPassword.length < 8) errors.newPassword = 'Password must be at least 8 characters';
    if (newPassword.length > 128)
      errors.newPassword = 'Password must be within 128 characters limit';
    if (/\s/.test(newPassword)) errors.newPassword = 'Password must not contain spaces';
    if (!/[A-Z]/.test(newPassword)) errors.newPassword = 'Must contain uppercase letter';
    if (!/[a-z]/.test(newPassword)) errors.newPassword = 'Must contain lowercase letter';
    if (!/[0-9]/.test(newPassword)) errors.newPassword = 'Must contain a number';
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(newPassword))
      errors.newPassword = 'Must contain a special character';

    if (newPassword !== confirmPassword) errors.confirmPassword = 'Passwords do not match';

    return {
      errors,
      isValid: Object.keys(errors).length === 0,
    };
  }, [newPassword, confirmPassword]);

  const { errors, isValid } = validation;

  const passwordRules = [
    {
      label: 'At least 8 characters',
      valid: newPassword.length >= 8,
    },
    {
      label: 'One uppercase letter',
      valid: /[A-Z]/.test(newPassword),
    },
    {
      label: 'One lowercase letter',
      valid: /[a-z]/.test(newPassword),
    },
    {
      label: 'One number',
      valid: /[0-9]/.test(newPassword),
    },
    {
      label: 'One special character',
      valid: /[!@#$%^&*(),.?":{}|<>]/.test(newPassword),
    },
    {
      label: 'Passwords match',
      valid: !!confirmPassword && newPassword === confirmPassword,
    },
  ];

  const handleBlur = (field: keyof typeof touched) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setTouched({ newPassword: true, confirmPassword: true });

    if (!isValid || !token) {
      return;
    }

    resetPassword.mutate(
      {
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      },
      {
        onSuccess: (response) => {
          showToast(response.message || 'Password reset successfully', 'success');
          navigate('/login');
        },
        onError: (error: any) => {
          const errorMessage = error.response?.data?.message || 'Failed to reset password';
          showToast(errorMessage, 'error');
        },
      }
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10 px-4">
      <div className="w-full max-w-md">
        <Link
          to="/login"
          className="inline-flex items-center gap-2 text-sm text-[#6b7280] hover:text-[#038e43] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Login
        </Link>

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-brand rounded-2xl shadow-lg mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-semibold text-primary-black mb-2">Set New Password</h1>
          <p className="text-gray-600">Enter your new password below</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create New Password</CardTitle>
            <CardDescription>
              Your new password must be different from previous passwords
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* New Password Field */}
              <div className="relative">
                <Input
                  type={showNewPassword ? 'text' : 'password'}
                  label={
                    <>
                      New Password <span className="text-red-500">*</span>
                    </>
                  }
                  placeholder="Enter your password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  onBlur={() => handleBlur('newPassword')}
                  className={
                    touched.newPassword && errors.newPassword ? 'border-red-500 pr-10' : 'pr-10'
                  }
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700"
                  tabIndex={-1}
                >
                  {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Confirm Password Field */}
              <div className="relative">
                <Input
                  type={showConfirmPassword ? 'text' : 'password'}
                  label={
                    <>
                      Confirm Password <span className="text-red-500">*</span>
                    </>
                  }
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  onBlur={() => handleBlur('confirmPassword')}
                  className={
                    touched.confirmPassword && errors.confirmPassword
                      ? 'border-red-500 pr-10'
                      : 'pr-10'
                  }
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>

              {/* Password Requirements */}
              <div className="bg-gradient-to-br from-gray-50 to-white border rounded-lg p-4">
                <h3 className="text-sm font-semibold mb-2 text-gray-900 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-primary-brand" />
                  Password Requirements
                </h3>
                <p className="text-xs text-gray-500 mb-3">
                  Your password must meet all criteria below
                </p>
                <div className="space-y-1.5">
                  {passwordRules.map((rule) => (
                    <div key={rule.label} className="flex items-start gap-2">
                      <div
                        className={`mt-0.5 rounded-full p-0.5 ${rule.valid ? 'bg-green-100' : 'bg-gray-100'}`}
                      >
                        {rule.valid ? (
                          <Check className="w-3 h-3 text-green-600" />
                        ) : (
                          <div className="w-3 h-3 rounded-full border-2 border-gray-300" />
                        )}
                      </div>
                      <span
                        className={`text-xs leading-tight ${rule.valid ? 'text-green-700 font-medium' : 'text-gray-600'}`}
                      >
                        {rule.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={resetPassword.isPending || !isValid}
              >
                {resetPassword.isPending ? 'Resetting...' : 'Reset Password'}
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
