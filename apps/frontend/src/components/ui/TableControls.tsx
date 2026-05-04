import { useEffect, useState, Dispatch, SetStateAction } from 'react';
import { Search, X } from 'lucide-react';
import clsx from 'clsx';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';

interface TableControlsProps {
  search?: string;
  onSearchChange?: (value: string) => void;

  filters?: React.ReactNode;

  hasActions?: boolean;

  placeholder?: string;
  className?: string;

  debounceMs?: number;
  setIsSearching?: Dispatch<SetStateAction<boolean>>;
  isSearching?: boolean;
}

export function TableControls({
  search = '',
  onSearchChange,
  filters,
  hasActions: hasActionsProp,
  placeholder = 'Search...',
  className = '',
  debounceMs = 400,
  setIsSearching,
  isSearching,
}: TableControlsProps) {
  const [searchInput, setSearchInput] = useState(search);
  const hasActions = hasActionsProp ?? Boolean(filters);

  useEffect(() => {
    setSearchInput(search);
  }, [search]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (onSearchChange && searchInput !== search) {
        onSearchChange(searchInput.trim());
      }
      setIsSearching?.(false);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchInput, debounceMs, onSearchChange, search, setIsSearching]);

  const handleClear = () => {
    setSearchInput('');
    onSearchChange?.('');
    setIsSearching?.(false);
  };

  return (
    <div
      className={clsx(
        'flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4',
        className
      )}
    >
      <div className="flex items-center gap-3 flex-wrap flex-1 max-w-[300px]">
        {onSearchChange && (
          <div
            className={clsx('relative w-full', {
              'md:max-w-sm': hasActions,
              'md:max-w-full': !hasActions,
            })}
          >
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />

            <Input
              value={searchInput}
              onChange={(e) => {
                setSearchInput(e.target.value);
                setIsSearching?.(true);
              }}
              placeholder={placeholder}
              className="w-full pl-9 pr-8 h-9"
            />

            {isSearching && (
              <div className="absolute right-8 top-1/2 -translate-y-1/2">
                <Spinner size="sm" className="text-muted-foreground" />
              </div>
            )}

            {searchInput && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {filters && <div className="flex items-center gap-2 flex-wrap">{filters}</div>}
    </div>
  );
}
