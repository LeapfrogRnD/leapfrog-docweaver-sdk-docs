import { ApiKey } from '@/types/api-key.type';
import { ApiKeyCard } from './ApiKeyCard';

interface ApiKeysCardListProps {
  apiKeys: ApiKey[];
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
  onRegenerate: (id: number) => void;
}

export function ApiKeysCardList({ apiKeys, onDelete, onEdit, onRegenerate }: ApiKeysCardListProps) {
  return (
    <div className="space-y-4">
      {apiKeys.map((apiKey) => (
        <ApiKeyCard
          key={apiKey.id}
          apiKey={apiKey}
          onDelete={onDelete}
          onEdit={onEdit}
          onRegenerate={onRegenerate}
        />
      ))}
    </div>
  );
}
