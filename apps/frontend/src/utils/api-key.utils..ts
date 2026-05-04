export const maskApiKey = (key: string): string => {
  if (!key) return '';
  if (key.length < 8) return key;
  const prefix = key.substring(0, 7); // "lpx_" prefix
  const suffix = key.substring(key.length - 4);
  return `${prefix}${'•'.repeat(20)}${suffix}`;
};
