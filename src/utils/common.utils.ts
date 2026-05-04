export function formatLabel(key: string): string {
  // 1. Replace underscores with spaces
  let label = key.replace(/_/g, ' ');

  // 2. Add spaces before capital letters (camelCase or PascalCase)
  label = label.replace(/([a-z])([A-Z])/g, '$1 $2');

  // 3. Capitalize the first letter of each word
  label = label.replace(/\b\w/g, (char) => char.toUpperCase());

  return label;
}
