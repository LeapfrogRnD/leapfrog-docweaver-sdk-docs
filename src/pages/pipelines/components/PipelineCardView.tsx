import { Pipeline } from '@/types/pipeline.type';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  CardSkeleton,
} from '@/components/ui';
import { Edit, Trash2, Copy, CheckCircle, Settings, XCircle, FileText } from 'lucide-react';
import {
  getOcrProviderLabel,
  getLlmProviderLabel,
  getLlmModelLabel,
  getParsingMethodLabel,
  getVlmModelLabel,
} from '@/utils';
import { Switch } from '@/components/ui/Switch';

interface PipelineCardViewProps {
  pipelines: Pipeline[];
  onEdit: (pipeline: Pipeline) => void;
  onDelete: (id: number) => void;
  onDuplicate: (id: number) => void;
  onToggleStatus: (id: number) => void;
  user: { id: number } | null;
  isLoading?: boolean;
}

export function PipelineCardView({
  pipelines,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleStatus,
  user,
  isLoading,
}: PipelineCardViewProps) {
  if (isLoading) {
    return <CardSkeleton cards={6} />;
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pipelines.map((pipeline) => {
          const isOwnedByUser = user && pipeline.created_by === user.id;

          return (
            <Card
              key={pipeline.id}
              className={`hover:shadow-lg transition-shadow ${
                pipeline.is_active ? 'bg-[#f0fdf4]' : ''
              }`}
            >
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-[10px] flex items-center justify-center flex-shrink-0 ${
                      pipeline.is_active ? 'bg-[#dcfce7]' : 'bg-[#f3f4f6]'
                    }`}
                  >
                    <FileText
                      className={`w-5 h-5 ${pipeline.is_active ? 'text-[#16a34a]' : 'text-[#6b7280]'}`}
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-lg">{pipeline.name}</CardTitle>
                      {pipeline.is_active && (
                        <span className="inline-flex items-center gap-1 px-2 h-[20px] bg-[#038e43] text-white text-xs font-medium rounded-md">
                          <CheckCircle className="w-3 h-3 flex-shrink-0" />
                          <span className="block truncate max-w-[64px] sm:max-w-[120px]">
                            Active
                          </span>
                        </span>
                      )}
                      {!pipeline.is_active && (
                        <span className="inline-flex items-center gap-1 px-2 h-[20px] bg-[#dc2626] text-white text-xs font-medium rounded-md">
                          <XCircle className="w-3 h-3 flex-shrink-0" />
                          <span className="block truncate max-w-[64px] sm:max-w-[120px]">
                            Inactive
                          </span>
                        </span>
                      )}
                    </div>
                    <CardDescription className="text-sm">
                      {pipeline.description || 'No description'}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 mb-1">LLM Provider</p>
                    <p className="text-sm font-semibold text-primary-black">
                      {getLlmProviderLabel(pipeline.llm_model_provider)}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 mb-1">OCR Provider</p>
                    <p className="text-sm font-semibold text-primary-black">
                      {getOcrProviderLabel(pipeline.ocr_provider)}
                    </p>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Settings className="w-4 h-4 text-gray-400" />
                    Model: {getLlmModelLabel(pipeline.llm_model_provider, pipeline.llm_model)}
                  </div>
                  {pipeline.ocr_provider === 'vlm' && pipeline.vlm_model && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                      VLM Model: {getVlmModelLabel(pipeline.vlm_model_provider, pipeline.vlm_model)}
                    </div>
                  )}
                  {pipeline.parsing_method && pipeline.ocr_provider !== 'vlm' && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                      Parsing: {getParsingMethodLabel(pipeline.parsing_method)}
                    </div>
                  )}
                </div>

                {/* Status Toggle */}
                {isOwnedByUser && !pipeline.is_default && (
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="text-sm text-gray-600 mr-2">Status</span>
                    <Switch
                      checked={pipeline.is_active}
                      onCheckedChange={() => onToggleStatus(pipeline.id)}
                      aria-label="Toggle pipeline status"
                    />
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t">
                  {!pipeline.is_default && isOwnedByUser && (
                    <Button
                      variant="outline"
                      onClick={() => onEdit(pipeline)}
                      className="flex-1 h-9 text-sm"
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    onClick={() => onDuplicate(pipeline.id)}
                    className="h-9 text-sm"
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                  {!pipeline.is_default && isOwnedByUser && (
                    <Button
                      variant="outline"
                      onClick={() => onDelete(pipeline.id)}
                      className="h-9 text-sm text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  )}
                </div>

                {/* Last updated */}
                <p className="text-xs text-gray-400 pt-2 border-t">
                  Updated{' '}
                  {pipeline.updated_at
                    ? new Date(pipeline.updated_at).toLocaleDateString()
                    : new Date(pipeline.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
