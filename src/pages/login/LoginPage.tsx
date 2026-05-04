import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui';
import { Spinner } from '@/components/ui';
import { Eye, EyeOff } from 'lucide-react';
import { LoginFormData, loginSchema } from '@/schemas/auth.schema';
// import { PROJECT_NAME } from '@/constants/project.constants';
import logo from '@/assets/v-logo.svg';

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const {
    login,
    isLoading,
    error,
    clearError,
    isAuthenticated,
    isProfileSetup,
    isProfileVerified,
  } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const email = watch('email');
  const password = watch('password');

  const emailValidation = {
    isEmpty: !email?.trim(),
    hasAt: email?.includes('@'),
    hasDotCom: email?.includes('.com'),
  };

  const getEmailError = () => {
    if (emailValidation.isEmpty) return null;
    if (!emailValidation.hasAt) return 'Email must contain @';
    return null;
  };

  const isFormEmpty = !email?.trim() || !password?.trim() || !email?.includes('@');

  useEffect(() => {
    if (isAuthenticated && isProfileSetup && isProfileVerified) {
      navigate('/tasks');
    } else if (isAuthenticated && isProfileVerified) {
      navigate('/complete-profile');
    } else if (isAuthenticated) {
      navigate('/setup-user');
    }
  }, [isAuthenticated, navigate, isProfileSetup, isProfileVerified]);

  useEffect(() => {
    if (error) {
      showToast(error, 'error');
      clearError();
    }
  }, [error, showToast, clearError]);

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    await login(data.email, data.password);
  };

  const handleInputChange = () => {
    if (error) {
      clearError();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center mb-1">
            <img src={logo} alt="Logo" className="w-[35%]" />
          </div>
          {/* <h1 className="text-3xl font-semibold text-primary-black mb-2">{PROJECT_NAME}</h1> */}
          {/* <p className="text-gray-600">Sign in to process your documents</p> */}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>Enter your credentials to access the system</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-primary-black mb-2">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <Input
                  type="email"
                  placeholder="Enter your email address"
                  {...register('email')}
                  onChange={(e) => {
                    register('email').onChange(e);
                    handleInputChange();
                  }}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
                {getEmailError() && <p className="mt-1 text-sm text-red-600">{getEmailError()}</p>}
              </div>

              <div>
                <div className="relative">
                  <label className="block text-sm font-medium text-primary-black mb-2">
                    Password <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    {...register('password')}
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700 transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div className="flex items-center justify-end">
                <Link
                  to="/password-reset"
                  className="text-sm text-[#038e43] hover:text-[#027235] font-medium"
                >
                  Forgot password?
                </Link>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading || isSubmitting || isFormEmpty}
              >
                {isLoading || isSubmitting ? (
                  <>
                    <Spinner size="sm" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
