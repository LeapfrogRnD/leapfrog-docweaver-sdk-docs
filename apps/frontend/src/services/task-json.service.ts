export const validateSchemaJson = <T>(
  jsonString: string,
  requiredFields: (keyof T)[]
): { isValid: boolean; data?: T[]; error?: string } => {
  try {
    const parsed = JSON.parse(jsonString);
    if (!Array.isArray(parsed)) {
      return { isValid: false, error: 'JSON must be an array' };
    }

    const isValid = parsed.every((item: any) =>
      requiredFields.every((field) => item[field] !== undefined && item[field] !== '')
    );

    if (!isValid) return { isValid: false, error: 'Invalid structure: Missing required fields' };
    return { isValid: true, data: parsed };
  } catch (e) {
    return { isValid: false, error: 'Invalid JSON format' };
  }
};

export const formatJson = (data: any) => JSON.stringify(data, null, 2);
