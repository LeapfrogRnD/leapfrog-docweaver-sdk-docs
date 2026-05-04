import { InfoIcon } from 'lucide-react';
import { TaskDetail, TaskStatus } from '@/types/task.type';

interface StatusMessageCardProps {
  task: TaskDetail;
}

export function StatusMessageCard({ task }: StatusMessageCardProps) {
  // Error Message - if failed
  if (task.status === TaskStatus.FAILED) {
    return (
      <div className="bg-[#fee2e2] border border-[#fca5a5] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#e7000b] flex-shrink-0" />
          <p className="text-sm text-[#e7000b]">
            The task failed to process. Please check the configuration and try again.
          </p>
        </div>
      </div>
    );
  }

  // Processing Info
  if (task.status === TaskStatus.PROCESSING) {
    return (
      <div className="bg-[#dbeafe] border border-[#93c5fd] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#155dfc] flex-shrink-0" />
          <p className="text-sm text-[#155dfc]">
            This task is currently being processed. Please check back later for results.
          </p>
        </div>
      </div>
    );
  }

  // Draft Info
  if (task.status === TaskStatus.DRAFT) {
    return (
      <div className="bg-[#fef3c7] border border-[#fbbf24] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#d97706] flex-shrink-0" />
          <p className="text-sm text-[#d97706]">
            This task is in draft mode. Complete the configuration to process it.
          </p>
        </div>
      </div>
    );
  }

  if (task.status === TaskStatus.DOCUMENT_PENDING) {
    return (
      <div className="bg-[#fed7aa] border border-[#fdba74] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#b45309] flex-shrink-0" />
          <p className="text-sm text-[#b45309]">
            Waiting for document upload. Please upload the required document to proceed.
          </p>
        </div>
      </div>
    );
  }

  // Document Uploaded Info
  if (task.status === TaskStatus.DOCUMENT_UPLOADED) {
    return (
      <div className="bg-[#d1fae5] border border-[#6ee7b7] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#065f46] flex-shrink-0" />
          <p className="text-sm text-[#065f46]">
            Document has been uploaded successfully. Configure the task settings to proceed.
          </p>
        </div>
      </div>
    );
  }

  // Ready Info
  if (task.status === TaskStatus.READY) {
    return (
      <div className="bg-[#d1fae5] border border-[#6ee7b7] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#059669] flex-shrink-0" />
          <p className="text-sm text-[#059669]">
            This task is configured and ready to be processed. Click the "Re-run Task" button to
            start processing.
          </p>
        </div>
      </div>
    );
  }

  if (task.status === TaskStatus.QUEUED) {
    return (
      <div className="bg-[#ede9fe] border border-[#c4b5fd] rounded-[14px] p-3">
        <div className="flex gap-3">
          <InfoIcon className="w-5 h-5 text-[#7c3aed] flex-shrink-0" />
          <p className="text-sm text-[#7c3aed]">
            This task is in the processing queue. It will start processing once previous tasks are
            completed.
          </p>
        </div>
      </div>
    );
  }

  return null;
}
