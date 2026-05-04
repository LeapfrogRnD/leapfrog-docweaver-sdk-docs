import { useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useToast } from '@/context/ToastContext';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Spinner,
} from '@/components/ui';
import { CheckCircle, Eye, EyeOff, LogOut, UserCircle, AlertCircle, Check } from 'lucide-react';
import { verifyAndChangePassword } from '@/services/user.service';
import { useAuth } from '@/context/AuthContext';

interface FormErrors {
  firstName?: string;
  lastName?: string;
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

interface TouchedFields {
  firstName: boolean;
  lastName: boolean;
  currentPassword: boolean;
  newPassword: boolean;
  confirmPassword: boolean;
}

export function CompleteProfilePage() {
  const { logout, user } = useAuth();
  const [searchParams] = useSearchParams();

  const email = searchParams.get('email') || user?.email || '';
  const token = searchParams.get('token') || '';

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [touched, setTouched] = useState<TouchedFields>({
    firstName: false,
    lastName: false,
    currentPassword: false,
    newPassword: false,
    confirmPassword: false,
  });

  const [isLoading, setIsLoading] = useState(false);

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { showToast } = useToast();
  const navigate = useNavigate();

  const validation = useMemo(() => {
    const errors: FormErrors = {};

    if (!formData.firstName.trim()) errors.firstName = 'First name is required';
    if (!formData.lastName.trim()) errors.lastName = 'Last name is required';

    if (!formData.currentPassword) errors.currentPassword = 'Current password is required';

    if (formData.newPassword.length < 8)
      errors.newPassword = 'Password must be at least 8 characters';

    if (formData.newPassword.length > 128)
      errors.newPassword = 'Password must be at within 128 characters limit ';
    if (/\s/.test(formData.newPassword)) errors.newPassword = 'Password must not contain spaces';

    if (!/[A-Z]/.test(formData.newPassword)) errors.newPassword = 'Must contain uppercase letter';

    if (!/[a-z]/.test(formData.newPassword)) errors.newPassword = 'Must contain lowercase letter';

    if (!/[0-9]/.test(formData.newPassword)) errors.newPassword = 'Must contain a number';
    if (!(formData.confirmPassword == formData.newPassword))
      errors.confirmPassword = 'Confirm password must match new password';

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.newPassword))
      errors.newPassword = 'Must contain a special character';

    if (formData.currentPassword && formData.newPassword) {
      if (formData.currentPassword === formData.newPassword) {
        errors.newPassword = 'New password must be different';
      }
    }

    if (formData.newPassword !== formData.confirmPassword)
      errors.confirmPassword = 'Passwords do not match';

    return {
      errors,
      isValid: Object.keys(errors).length === 0,
    };
  }, [formData]);

  const { errors, isValid } = validation;

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));
  };

  const handleBlur = (field: keyof TouchedFields) => () => {
    setTouched((prev) => ({
      ...prev,
      [field]: true,
    }));
  };

  const handleLogout = async () => {
    try {
      await logout();
      showToast('Logged out successfully', 'success');
      navigate('/login');
    } catch {
      showToast('Failed to logout', 'error');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isValid) {
      // Mark all fields as touched when submitting
      setTouched({
        firstName: true,
        lastName: true,
        currentPassword: true,
        newPassword: true,
        confirmPassword: true,
      });
      showToast('Please fix validation errors first', 'error');
      return;
    }

    if (!email) {
      showToast('Email is required. Please try logging in again.', 'error');
      return;
    }

    setIsLoading(true);

    try {
      const result = await verifyAndChangePassword(
        email,
        formData.currentPassword,
        formData.newPassword,
        formData.firstName,
        formData.lastName,
        token
      );

      if (result.success) {
        showToast(
          'Profile setup completed successfully! Please login with your new password.',
          'success'
        );

        setTimeout(() => {
          logout();
          navigate('/login');
        }, 100);
      } else {
        showToast(result.message, 'error');
      }
    } catch {
      showToast('An error occurred while completing your profile. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // ---------------- Password Requirement Visualization ----------------

  const passwordRules = [
    {
      label: 'At least 8 characters',
      valid: formData.newPassword.length >= 8,
    },
    {
      label: 'One uppercase letter',
      valid: /[A-Z]/.test(formData.newPassword),
    },
    {
      label: 'One lowercase letter',
      valid: /[a-z]/.test(formData.newPassword),
    },
    {
      label: 'One number',
      valid: /[0-9]/.test(formData.newPassword),
    },
    {
      label: 'One special character',
      valid: /[!@#$%^&*(),.?":{}|<>]/.test(formData.newPassword),
    },
    {
      label: 'Different from current password',
      valid: !!formData.currentPassword && formData.currentPassword !== formData.newPassword,
    },
    {
      label: 'New Password and confirm password should match',
      valid: formData.confirmPassword && formData.confirmPassword === formData.newPassword,
    },
  ];

  // ---------------- UI ----------------

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <div className="flex items-center">
            <UserCircle className="w-8 h-8 text-primary-brand mr-3" />
            <h2 className="text-lg font-semibold">Complete Profile</h2>
          </div>

          <div className="flex items-center gap-4">
            {email && <span className="text-sm text-gray-600">{email}</span>}

            <Button variant="outline" onClick={handleLogout} className="gap-2">
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Form */}
      <div className="flex justify-center px-4 py-8 min-h-[calc(100vh-4rem)]">
        <div className="w-full max-w-5xl">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-brand rounded-2xl shadow-lg mb-4">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>

            <h1 className="text-3xl font-semibold mb-2">Complete Your Profile</h1>

            <p className="text-gray-600 text-sm">
              {token
                ? 'Email verified successfully! Now set up your profile.'
                : 'Set up your profile to continue.'}
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Profile Setup</CardTitle>
              <CardDescription>Provide details and secure your account</CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Email Address <span className="text-red-500">*</span>
                      </label>
                      <div className="px-4 py-2 bg-gray-50 border rounded-lg text-sm text-gray-700">
                        {email}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      {[
                        {
                          key: 'firstName',
                          label: (
                            <>
                              First Name <span className="text-red-500">*</span>
                            </>
                          ),
                          placeholder: 'Enter your first name',
                        },
                        {
                          key: 'lastName',
                          label: (
                            <>
                              Last Name <span className="text-red-500">*</span>
                            </>
                          ),
                          placeholder: 'Enter your last name',
                        },
                      ].map((field) => (
                        <div key={field.key}>
                          <Input
                            label={field.label}
                            placeholder={field.placeholder}
                            value={formData[field.key as keyof typeof formData]}
                            onChange={handleChange(field.key)}
                            onBlur={handleBlur(field.key as keyof TouchedFields)}
                            className={
                              touched[field.key as keyof TouchedFields] &&
                              errors[field.key as keyof FormErrors]
                                ? 'border-red-500 pr-10'
                                : 'pr-10'
                            }
                          />
                        </div>
                      ))}
                    </div>

                    {/* Password Fields */}
                    {[
                      {
                        key: 'currentPassword',
                        label: (
                          <>
                            Current Password <span className="text-red-500">*</span>
                          </>
                        ),
                        placeholder: 'Enter your current password',
                        show: showCurrentPassword,
                        toggle: setShowCurrentPassword,
                      },
                      {
                        key: 'newPassword',
                        label: (
                          <>
                            New Password <span className="text-red-500">*</span>
                          </>
                        ),
                        placeholder: 'Enter your new password',
                        show: showNewPassword,
                        toggle: setShowNewPassword,
                      },
                      {
                        key: 'confirmPassword',
                        label: (
                          <>
                            Confirm Password <span className="text-red-500">*</span>
                          </>
                        ),
                        placeholder: 'Re-enter your new password',
                        show: showConfirmPassword,
                        toggle: setShowConfirmPassword,
                      },
                    ].map((field) => (
                      <div key={field.key} className="relative">
                        <Input
                          type={field.show ? 'text' : 'password'}
                          label={field.label}
                          value={formData[field.key as keyof typeof formData]}
                          onChange={handleChange(field.key)}
                          onBlur={handleBlur(field.key as keyof TouchedFields)}
                          placeholder={field.placeholder}
                          className={
                            touched[field.key as keyof TouchedFields] &&
                            errors[field.key as keyof FormErrors]
                              ? 'border-red-500 pr-10'
                              : 'pr-10'
                          }
                        />

                        <button
                          type="button"
                          onClick={() => field.toggle((v) => !v)}
                          className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700"
                          tabIndex={-1}
                        >
                          {field.show ? (
                            <Eye className="w-5 h-5" />
                          ) : (
                            <EyeOff className="w-5 h-5" />
                          )}
                        </button>
                      </div>
                    ))}

                    <Button type="submit" className="w-full gap-2" disabled={isLoading || !isValid}>
                      {isLoading ? (
                        <>
                          <Spinner size="sm" />
                          Completing setup...
                        </>
                      ) : (
                        'Complete Setup'
                      )}
                    </Button>
                  </div>

                  {/* Right: Password Requirements */}
                  <div>
                    <div className="bg-gradient-to-br from-gray-50 to-white border rounded-lg p-4 mt-36">
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
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
