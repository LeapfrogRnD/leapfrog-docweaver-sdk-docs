export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validates email format
 */
export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  if (!email.includes('@')) {
    return { isValid: false, error: 'Email must contain @' };
  }

  // Basic email regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Please enter a valid email address' };
  }

  return { isValid: true };
}

/**
 * Validates password with comprehensive rules
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'Password is required' };
  }

  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters' };
  }

  if (password.length > 128) {
    return { isValid: false, error: 'Password must be at most 128 characters' };
  }

  if (/\s/.test(password)) {
    return { isValid: false, error: 'Password cannot contain whitespace characters' };
  }

  if (!/[A-Z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one uppercase letter' };
  }

  if (!/[a-z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one lowercase letter' };
  }

  if (!/[0-9]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one number' };
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one special character' };
  }

  return { isValid: true };
}

/**
 * Validates password confirmation
 */
export function validatePasswordMatch(password: string, confirmPassword: string): ValidationResult {
  if (!confirmPassword) {
    return { isValid: false, error: 'Please confirm your password' };
  }

  if (password !== confirmPassword) {
    return { isValid: false, error: 'Passwords do not match' };
  }

  return { isValid: true };
}

/**
 * Get all password requirements with their validation status
 */
export function getPasswordRequirements(password: string, currentPassword?: string) {
  return [
    {
      label: 'At least 8 characters',
      valid: password.length >= 8,
    },
    {
      label: 'One uppercase letter',
      valid: /[A-Z]/.test(password),
    },
    {
      label: 'One lowercase letter',
      valid: /[a-z]/.test(password),
    },
    {
      label: 'One number',
      valid: /[0-9]/.test(password),
    },
    {
      label: 'One special character',
      valid: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    },
    {
      label: 'No spaces allowed',
      valid: !/\s/.test(password),
    },
    ...(currentPassword
      ? [
          {
            label: 'Different from current password',
            valid: !!currentPassword && currentPassword !== password,
          },
        ]
      : []),
  ];
}

/**
 * Validates required text field
 */
export function validateRequired(value: string, fieldName: string): ValidationResult {
  if (!value || !value.trim()) {
    return { isValid: false, error: `${fieldName} is required` };
  }

  return { isValid: true };
}

/**
 * Validates name fields (first name, last name, etc.)
 */
export function validateName(name: string, fieldName: string): ValidationResult {
  const requiredValidation = validateRequired(name, fieldName);
  if (!requiredValidation.isValid) {
    return requiredValidation;
  }

  if (name.length < 2) {
    return { isValid: false, error: `${fieldName} must be at least 2 characters` };
  }

  if (name.length > 50) {
    return { isValid: false, error: `${fieldName} must be at most 50 characters` };
  }

  return { isValid: true };
}
