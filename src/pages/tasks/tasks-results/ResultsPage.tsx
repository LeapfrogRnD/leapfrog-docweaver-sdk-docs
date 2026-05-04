import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, Button, Spinner } from '@/components/ui';
import { ExtractedView } from './components/ExtractedView';
import { ClassifiedView } from './components/ClassifiedView';
import { GenerationView } from './components/GenerationView';
import {
  Download,
  ArrowLeft,
  FileText,
  RotateCw,
  Lock,
  CircleCheckBig,
  RefreshCcw,
} from 'lucide-react';
import { OcrResult } from '@/types/types';
import { RerunConfirmModal } from '@/components/ui/RerunConfirmModal';
import { useGetTask, useGetTaskResults, useExecuteTask } from '@/queries/task.query';
import { mapTaskResultResponse } from '@/mappers/task.mapper';
import { PdfViewer } from './components/PDFViewerNew';
import { ImageViewer } from './components/ImageViewer';
import { DocHeaderInfo } from './components/DocHeaderInfo';
import { TaskStatus, TaskType } from '@/types/task.type';
import { TextViewer } from './components/TextViewer';
import { useAuth } from '@/context/AuthContext';
import { Roles } from '@/types/types';
import { PageHeader } from '@/components';
import { ResultPageSkeleton } from './components/ResultPageSkeleton';

export function ResultsPage() {
  const { taskId: taskIdParam } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [showRerunConfirm, setShowRerunConfirm] = useState(false);
  const { user } = useAuth();

  const [currentPage, setCurrentPage] = useState(1);
  const [isPreviewPageRendered, setIsPreviewPageRendered] = useState(false);

  useEffect(() => {
    if (!taskIdParam) {
      navigate('/tasks');
      return;
    }
  }, [taskIdParam, navigate]);

  const taskId = taskIdParam ? Number(taskIdParam) : 0;

  const { data: taskResult, isLoading: isLoadingResult } = useGetTaskResults(taskId);
  const { data: taskDetail, isLoading: isLoadingTask } = useGetTask(taskId);
  const executeTaskMutation = useExecuteTask();
  const isPdfPreview = Boolean(
    taskResult?.file_metadata?.content_type &&
    !taskResult.file_metadata.content_type.startsWith('image/') &&
    !taskResult.file_metadata.content_type.startsWith('text/')
  );

  const result: OcrResult | null = useMemo(
    () => (taskResult ? mapTaskResultResponse(taskResult) : null),
    [taskResult]
  );

  // Determine if current user can trigger a rerun for this result
  const canRerun = Boolean(
    result &&
    [TaskStatus.FAILED, TaskStatus.COMPLETED, TaskStatus.READY].includes(
      result.status as TaskStatus
    ) &&
    (taskDetail?.created_by === user?.id || user?.role === Roles.Admin)
  );

  const [editedStructuredData, setEditedStructuredData] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!result) return;
    const sd = result.structuredData;
    if (Array.isArray(sd)) {
      const normalized = sd.reduce((acc, item, idx) => {
        acc[idx.toString()] = item;
        return acc;
      }, {});
      setEditedStructuredData(normalized);
    } else if (sd && typeof sd === 'object') {
      setEditedStructuredData({ '0': sd });
    } else {
      setEditedStructuredData({});
    }
  }, [result]);

  const handleExport = () => {
    if (!result) return;

    const exportData = {
      id: result.id,
      documentId: result.documentId,
      documentName: result.documentName,
      status: result.status,
      extractedText: result.extractedText,
      structuredData: editedStructuredData,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.documentName.replace(/\.[^/.]+$/, '')}_ocr_result.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRerunClick = () => {
    setShowRerunConfirm(true);
  };

  const handleChangeSettings = () => {
    if (taskId) navigate(`/tasks/${taskId}/edit`);
  };

  const handleRerunWithSameSettings = async () => {
    if (!taskId || !result) return;

    try {
      await executeTaskMutation.mutateAsync(taskId);
      setShowRerunConfirm(false);
      navigate(`/tasks`);
    } catch (error) {
      console.error('Task execution failed:', error);
    }
  };

  if (isLoadingResult || isLoadingTask) {
    return <ResultPageSkeleton />;
  }

  if (!result) {
    return (
      <div className="min-h-[calc(100vh-89px)] flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-primary-black mb-2">No Results Found</h2>
          <p className="text-gray-600 mb-4">Unable to find the Tasks Result</p>
          <Button onClick={() => navigate('/upload')}>
            <ArrowLeft className="w-4 h-4" />
            Back to Tasks
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#f9fafb]">
      {executeTaskMutation.isPending && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-[14px] p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center">
              <Spinner size="lg" className="mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-[#111] mb-2">Re-processing Document</h2>
              <p className="text-sm text-[#6b7280] mb-4">
                Please wait while we re-analyze your document with OCR...
              </p>
            </div>
          </div>
        </div>
      )}
      <PageHeader
        icon={<CircleCheckBig className="w-6 h-6" />}
        title="Workflow Result"
        description="View your processed data and details"
        actions={
          <>
            <button
              onClick={() => navigate('/tasks')}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-[#f3f4f6] transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-[#6b7280]" />
            </button>
            {canRerun && (
              <Button
                onClick={handleRerunClick}
                icon={<RefreshCcw className="w-4 h-4" />}
                disabled={executeTaskMutation.isPending}
                variant="outline"
              >
                Re-run Workflow
              </Button>
            )}
            <Button onClick={handleExport} icon={<Download className="w-4 h-4" />}>
              Export JSON
            </Button>
          </>
        }
      />
      <div className="bg-[#f9fafb] p-12 mx-7">
        <DocHeaderInfo result={result} taskResult={taskResult} />

        {/* Rerun / Failure Section (shown for failed tasks) */}
        {result.status === TaskStatus.FAILED && (
          <div className="mb-6">
            <Card>
              <CardHeader>
                <CardTitle>Failure Details & Re-run Options</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                  <div>
                    <label className="block text-xs font-medium text-[#6b7280] mb-1">
                      Failed Remarks
                    </label>
                    <p className="text-sm font-medium text-[#111]">
                      {taskDetail?.failed_remarks ? taskDetail.failed_remarks : 'N/A'}
                    </p>
                  </div>

                  <div>
                    {!(taskDetail?.created_by === user?.id || user?.role === Roles.Admin) ? (
                      <div className="flex items-start gap-3 p-4 bg-[#fef2f2] rounded-[10px]">
                        <div className="w-8 h-8 bg-[#fee2e2] rounded-lg flex items-center justify-center flex-shrink-0">
                          <Lock className="w-4 h-4 text-[#dc2626]" />
                        </div>
                        <div>
                          <h3 className="text-sm font-medium text-[#dc2626] mb-1">
                            Permission Denied
                          </h3>
                          <p className="text-xs text-[#6b7280] leading-relaxed">
                            You can only re-run tasks that you created. This task belongs to another
                            user.
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-2 flex-wrap">
                        <Button
                          onClick={handleRerunClick}
                          icon={<RotateCw className="w-4 h-4" />}
                          disabled={executeTaskMutation.isPending}
                          variant="outline"
                        >
                          Re-run with same settings
                        </Button>
                        <Button onClick={handleChangeSettings} variant="outline">
                          Change settings before re-running
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Document Preview</CardTitle>
            </CardHeader>

            <CardContent>
              {taskResult?.file_metadata?.content_type?.startsWith('image/') ? (
                <ImageViewer fileUrl={taskResult?.document_preview_url ?? undefined} />
              ) : taskResult?.file_metadata?.content_type?.startsWith('text/') ? (
                <TextViewer fileUrl={taskResult?.document_preview_url ?? undefined} />
              ) : (
                <PdfViewer
                  fileUrl={taskResult?.document_preview_url ?? undefined}
                  onPageChange={setCurrentPage}
                  onPageRenderStatusChange={(isRendered, page) => {
                    if (page === currentPage) {
                      setIsPreviewPageRendered(isRendered);
                    }
                  }}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              {taskResult?.task_type === TaskType.CLASSIFICATION ? (
                <ClassifiedView
                  result={result}
                  currentPage={currentPage}
                  onEditedDataChange={setEditedStructuredData}
                  isLoading={isPdfPreview && !isPreviewPageRendered}
                />
              ) : taskResult?.task_type === TaskType.EXTRACTION ? (
                <ExtractedView
                  result={result}
                  currentPage={currentPage}
                  onEditedDataChange={setEditedStructuredData}
                  isLoading={isPdfPreview && !isPreviewPageRendered}
                />
              ) : (
                <GenerationView
                  result={result}
                  currentPage={currentPage}
                  isLoading={isPdfPreview && !isPreviewPageRendered}
                  onEditedDataChange={setEditedStructuredData}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* RERUN MODAL */}
      <RerunConfirmModal
        isOpen={showRerunConfirm}
        onClose={() => setShowRerunConfirm(false)}
        onRerunWithSameSettings={handleRerunWithSameSettings}
        onChangeSettings={handleChangeSettings}
        taskName={result?.documentName}
        isOwnedByCurrentUser={taskDetail?.created_by === user?.id}
      />
    </div>
  );
}
