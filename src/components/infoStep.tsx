import type { ReactNode } from 'react';
import { Alert, AlertTitle, AlertDescription } from './ui/Alert';

type AlertVariant = 'info' | 'error' | 'success' | 'warning' | 'guidance' | 'note';

interface AlertBannerProps {
  title: string;
  description: ReactNode;
  variant?: AlertVariant;
  icon?: ReactNode;
  className?: string;
  onClose?: () => void;
}

const AlertBanner: React.FC<AlertBannerProps> = ({
  title,
  description,
  variant = 'info',
  icon,
  className = '',
  onClose,
}) => {
  return (
    <Alert variant={variant} icon={icon} className={className} onClose={onClose}>
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
};

export default AlertBanner;
