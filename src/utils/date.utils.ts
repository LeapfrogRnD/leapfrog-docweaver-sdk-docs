export const formatDate = (
  date?: number | null | string,
  includeTime: boolean = false,
  options?: {
    seconds?: boolean;
    use12Hour?: boolean;
  }
): string => {
  if (!date) return '';

  const d = new Date(date);
  if (isNaN(d.getTime())) return '';

  const months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ];
  const month = months[d.getMonth()];
  const day = d.getDate();
  const year = d.getFullYear();
  if (!includeTime) {
    return `${month} ${day}, ${year}`;
  }

  let hours = d.getHours();
  const minutes = d.getMinutes().toString().padStart(2, '0');
  const seconds = d.getSeconds().toString().padStart(2, '0');

  let suffix = '';

  suffix = hours >= 12 ? ' PM' : ' AM';
  hours = hours % 12 || 12; // convert 0 → 12

  const formattedHours = hours.toString().padStart(2, '0');

  const time = options?.seconds
    ? `${formattedHours}:${minutes}:${seconds}${suffix}`
    : `${formattedHours}:${minutes}${suffix}`;

  const result = `${month} ${day}, ${year} | ${time}`;
  return result;
};
