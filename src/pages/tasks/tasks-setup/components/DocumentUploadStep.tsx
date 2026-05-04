import { useFormContext, useController } from 'react-hook-form';
import { FileText, CheckCircle, AlertCircle, Loader2, X, RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { PDFDocument } from 'pdf-lib';
import type { AxiosProgressEvent } from 'axios';

import { FileUploader } from '@/components/FileUploader';
import { TaskCreationFlowFormData } from '@/schemas/task.schema';
import { useTaskStore } from '@/store/taskStore';
import { apiClient } from '@/lib/client';
import {
  useGeneratePresignedUrl,
  useConfirmDocUpload,
  useDeleteTaskFiles,
} from '@/queries/task.query';
import { useToast } from '@/context/ToastContext';
import { formatFileSize } from '@/utils';
import AlertBanner from '@/components/infoStep';
import { uploadFile } from '@/utils/fileupload.utils';

interface DocumentUploadStepProps {
  editingDraftId: string | null;
}

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  isCompleted: boolean;
}
const MAX_FILE_SIZE = (import.meta.env.MAX_FILE_SIZE as number) || 30;

export function DocumentUploadStep({ editingDraftId }: DocumentUploadStepProps) {
  const {
    control,
    formState: { errors },
  } = useFormContext<TaskCreationFlowFormData>();

  const { setUploadedFiles, taskId, formData, isUploadCompleted, setUploadCompleted } =
    useTaskStore();
  const { showToast } = useToast();

  const [files, setFiles] = useState<File[]>([]);
  const [removing, setRemoving] = useState(false);
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    isCompleted: !!isUploadCompleted,
  });

  const generatePresignedUrlMutation = useGeneratePresignedUrl();
  const confirmDocUploadMutation = useConfirmDocUpload();
  const delteTaskFilesMutation = useDeleteTaskFiles();

  const {
    field: { onChange: setUploadedFilesForm },
  } = useController({
    name: 'uploadedFiles',
    control,
    defaultValue: [],
  });

  const uploadFileToServer = async (file: File) => {
    if (!taskId) {
      const errorMessage = 'No task ID available. Please go back and create a task first.';
      setUploadState((prev) => ({ ...prev, error: errorMessage }));
      showToast(errorMessage, 'error');
      return false;
    }

    setUploadState({ isUploading: true, progress: 10, error: null, isCompleted: false });
    setUploadCompleted(false);

    try {
      const presignedResponse = await generatePresignedUrlMutation.mutateAsync({
        taskId,
        request: {
          filename: file.name,
          file_metadata: { file_size: file.size, content_type: file.type },
        },
      });
      setUploadState((prev) => ({ ...prev, progress: 20 }));

      let uploadUrl = presignedResponse.url;
      if (!/^https?:\/\//i.test(uploadUrl)) {
        const apiBase =
          (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000/api/';
        if (!uploadUrl.startsWith('/')) uploadUrl = '/' + uploadUrl;
        uploadUrl = apiBase.replace(/\/$/, '') + uploadUrl;
      }

      const isLocalUpload = uploadUrl.startsWith(window.location.origin);
      const uploadBody = isLocalUpload ? await file.arrayBuffer() : file;

      if (isLocalUpload) {
        await apiClient.put(uploadUrl, uploadBody, {
          headers: { 'Content-Type': file.type || 'application/octet-stream' },
          maxBodyLength: Infinity,
          onUploadProgress: (progressEvent?: AxiosProgressEvent) => {
            const loaded = progressEvent?.loaded ?? 0;
            const total = progressEvent?.total ?? 0;
            if (total > 0) {
              const percent = 20 + Math.round((loaded / total) * 60);
              setUploadState((prev) => ({ ...prev, progress: Math.min(percent, 80) }));
            }
          },
        });
      } else {
        await uploadFile(file, uploadUrl, setUploadState);
      }

      setUploadState((prev) => ({ ...prev, progress: 90 }));
      await confirmDocUploadMutation.mutateAsync({
        taskId,
        request: { file_key: presignedResponse.file_key! },
      });

      setUploadState({ isUploading: false, progress: 100, error: null, isCompleted: true });
      setUploadCompleted(true);
      showToast('File uploaded successfully', 'success');
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed.';
      setUploadState({ isUploading: false, progress: 0, error: errorMessage, isCompleted: false });
      setUploadCompleted(false);
      showToast(`Upload failed: ${errorMessage}`, 'error');
      return false;
    }
  };

  const validatePageCount = async (file: File, maxPages = 50): Promise<boolean> => {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      if (pdfDoc.getPageCount() > maxPages) {
        showToast(`Maximum allowed is ${maxPages} pages.`, 'error');
        return false;
      }
      return true;
    } catch (err) {
      showToast('Failed to read PDF file.', 'error');
      return false;
    }
  };

  const handleFileSelect = async (file: File) => {
    const maxSize = MAX_FILE_SIZE * 1024 * 1024;
    const maxSizeMB = maxSize / (1024 * 1024);
    if (file.size > maxSize) {
      showToast(`File size exceeds ${maxSizeMB}MB limit.`, 'error');
      return;
    }

    if (file.type === 'application/pdf' && !(await validatePageCount(file))) return;

    setUploadState({ isUploading: false, progress: 0, error: null, isCompleted: false });
    setUploadCompleted(false);

    const newFiles = [file];
    setFiles(newFiles);
    setUploadedFilesForm(newFiles);
    setUploadedFiles(newFiles);

    if (taskId) await uploadFileToServer(file);
  };

  const handleRemoveFile = async (index: number) => {
    if (taskId) {
      try {
        setRemoving(true);
        await delteTaskFilesMutation.mutateAsync(taskId);
        showToast('File removed successfully', 'success');
      } catch (error) {
        showToast('Error removing file', 'error');
      } finally {
        setRemoving(false);
      }
    }

    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    setUploadedFilesForm(newFiles);
    setUploadState({ isUploading: false, progress: 0, error: null, isCompleted: false });
    setUploadedFiles(newFiles);
    setUploadCompleted(false);
  };

  const handleRefreshClick = () => {
    const newFiles: File[] = [];
    setFiles(newFiles);
    setUploadedFilesForm(newFiles);
    setUploadedFiles(newFiles);
    setUploadState({ isUploading: false, progress: 0, error: null, isCompleted: false });
    setUploadCompleted(false);
    showToast('Cleared file. Please select a new file.', 'info');
  };

  const displayFiles = files.length > 0 ? files : (formData.uploadedFiles as File[]) || [];

  return (
    <div className="space-y-8">
      {editingDraftId && (
        <AlertBanner
          variant="info"
          title="Editing Draft"
          description="You can upload a new document to replace the previous one."
        />
      )}

      {!taskId && (
        <div className="bg-red-50 border border-red-100 rounded-xl p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-red-900">Task Required</h3>
            <p className="text-sm text-red-700">Please complete step 1 before uploading.</p>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
        <p className="text-sm text-gray-500">
          Initiate the processing workflow by uploading your files.
        </p>
      </div>

      {displayFiles.length === 0 ? (
        <div className="space-y-3">
          <label className="text-sm font-medium">
            Select Files <span className="text-red-500">*</span>
          </label>
          <FileUploader
            onFileSelect={handleFileSelect}
            accept=".pdf,.jpg,.jpeg,.png"
            maxSize={MAX_FILE_SIZE * 1024 * 1024}
            disabled={!taskId || uploadState.isUploading}
          />
          {errors.uploadedFiles && (
            <p className="text-xs text-red-600">{errors.uploadedFiles.message}</p>
          )}
        </div>
      ) : (
        <div
          className={`space-y-4 ${formData.fileStatus === 'pending' ? 'border border-red-400 p-4 rounded-lg' : ''}`}
        >
          <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">
            Selected File
          </h3>
          {displayFiles.map((file: File, index: number) => (
            <div key={index} className="group animate-in fade-in slide-in-from-top-1 duration-200">
              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-50 rounded-lg">
                    <FileText className="w-5 h-5 text-[#038e43]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p
                        className={`text-sm font-semibold  truncate max-w-[280px] ${formData.fileStatus === 'pending'} ? 'text-red-900':'text-gray-900'`}
                      >
                        {file.name}
                      </p>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(index)}
                        className="p-1 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                        disabled={uploadState.isUploading || removing}
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {removing && <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />}
                  {uploadState.isCompleted &&
                    !uploadState.isUploading &&
                    formData.fileStatus != 'pending' && (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    )}
                  {formData.fileStatus == 'pending' && (
                    <span
                      title="Upload failed. Click to retry"
                      aria-label="Upload failed. Retry upload"
                      role="button"
                      tabIndex={0}
                      onClick={() => handleRefreshClick()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleRefreshClick();
                        }
                      }}
                      className="inline-flex items-center gap-1 text-red-600 cursor-pointer group"
                    >
                      <RefreshCw
                        className="w-4 h-4 transition duration-150 ease-in-out group-hover:rotate-180 group-hover:text-red-800"
                        aria-hidden="true"
                      />
                    </span>
                  )}
                </div>
              </div>

              {/* Status Section - Simplified and borderless */}
              {(uploadState.isUploading || uploadState.error) && (
                <div className="mt-2 py-2 space-y-3">
                  {uploadState.isUploading && (
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-[11px] uppercase tracking-wider font-bold text-gray-500">
                        <span>Uploading to server</span>
                        <span>{uploadState.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1 overflow-hidden">
                        <div
                          className="bg-[#038e43] h-full transition-all duration-300"
                          style={{ width: `${uploadState.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {uploadState.error && (
                    <div className="flex gap-2 text-red-600 items-center">
                      <AlertCircle className="w-3.5 h-3.5" />
                      <p className="text-xs font-medium">{uploadState.error}</p>
                      <button
                        onClick={() => uploadFileToServer(file)}
                        className="text-xs font-bold underline ml-1"
                      >
                        Retry
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AlertBanner
        variant="guidance"
        title="Document Guidelines"
        description={
          <ul className="mt-2 ml-4 list-disc text-xs text-gray-500 space-y-1">
            <li>Ensure documents are clear and readable for OCR accuracy.</li>
            <li>Maximum file size: {MAX_FILE_SIZE}MB per document.</li>
            <li>Supported formats: PDF, JPG, PNG.</li>
          </ul>
        }
      />
    </div>
  );
}
