import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { TaskCreationFlowFormData } from '@/schemas/task.schema';

// Simple file info representation for storage (only filename)
interface FileInfo {
  name: string;
  size: number;
  type: string;
}

interface TaskCreationState {
  // Current step state
  currentStep: number;
  taskId: number | null;
  editingDraftId: string | null;
  isCreatePipelineOpen: boolean;
  isEditMode: boolean;

  isUploadCompleted: boolean;

  // Form data (with file info only)
  formData: Omit<Partial<TaskCreationFlowFormData>, 'uploadedFiles'> & {
    uploadedFiles?: FileInfo[];
  };

  // Actions
  setCurrentStep: (step: number) => void;
  setTaskId: (taskId: number | null) => void;
  setEditingDraftId: (draftId: string | null) => void;
  setIsCreatePipelineOpen: (isOpen: boolean) => void;
  setIsEditMode: (isEditMode: boolean) => void;
  updateFormData: (data: Partial<TaskCreationFlowFormData>) => void;
  setUploadedFiles: (files: File[]) => void;
  getUploadedFileNames: () => string[];
  clearTaskCreation: () => void;
  populateEditData: (
    data: Omit<Partial<TaskCreationFlowFormData>, 'uploadedFiles'> & {
      uploadedFiles?: FileInfo[];
    }
  ) => void;

  // Upload completion setter
  setUploadCompleted: (isCompleted: boolean) => void;

  // Step progression helpers
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (step: number) => void;
}

// Helper function to convert File to FileInfo (basic info only)
const fileToFileInfo = (file: File): FileInfo => ({
  name: file.name,
  size: file.size,
  type: file.type,
});

const initialFormData = {
  taskName: '',
  uploadedFiles: [],
  systemPrompt: '',
  taskType: undefined,
  pipelineId: undefined,
  enableContext: false,
  extractionFields: [],
  classificationCategories: [],
};

export const useTaskStore = create<TaskCreationState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentStep: 1,
      taskId: null,
      editingDraftId: null,
      isCreatePipelineOpen: false,
      isEditMode: false,
      // Track upload completion
      isUploadCompleted: false,
      formData: initialFormData,

      // Actions
      setCurrentStep: (step: number) => set({ currentStep: step }),

      setTaskId: (taskId: number | null) => set({ taskId }),

      setEditingDraftId: (draftId: string | null) => set({ editingDraftId: draftId }),

      setIsCreatePipelineOpen: (isOpen: boolean) => set({ isCreatePipelineOpen: isOpen }),

      setIsEditMode: (isEditMode: boolean) => set({ isEditMode }),

      updateFormData: (data: Omit<Partial<TaskCreationFlowFormData>, 'uploadedFiles'>) =>
        set((state) => ({
          formData: { ...state.formData, ...data },
        })),

      setUploadedFiles: (files: File[]) => {
        const fileInfos = files.map((file) => fileToFileInfo(file));
        set((state) => ({
          formData: { ...state.formData, uploadedFiles: fileInfos },
        }));
      },

      getUploadedFileNames: () => {
        const { formData } = get();
        if (!formData.uploadedFiles || formData.uploadedFiles.length === 0) {
          return [];
        }
        return formData.uploadedFiles.map((fileInfo) => fileInfo.name);
      },

      clearTaskCreation: () =>
        set({
          currentStep: 1,
          taskId: null,
          editingDraftId: null,
          isCreatePipelineOpen: false,
          isEditMode: false,
          formData: initialFormData,
          isUploadCompleted: false,
        }),

      populateEditData: (
        data: Omit<Partial<TaskCreationFlowFormData>, 'uploadedFiles'> & {
          uploadedFiles?: FileInfo[];
        }
      ) =>
        set({
          formData: { ...initialFormData, ...data },
          isEditMode: true,
          isUploadCompleted: !!(data.uploadedFiles && data.uploadedFiles.length > 0),
        }),

      setUploadCompleted: (isCompleted: boolean) => set({ isUploadCompleted: isCompleted }),

      // Step progression helpers
      nextStep: () => {
        const { currentStep } = get();
        if (currentStep < 3) {
          set({ currentStep: currentStep + 1 });
        }
      },

      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 1) {
          set({ currentStep: currentStep - 1 });
        }
      },

      goToStep: (step: number) => {
        if (step >= 1 && step <= 3) {
          set({ currentStep: step });
        }
      },
    }),
    {
      name: 'task-creation-storage',
      partialize: (state) => ({
        currentStep: state.currentStep,
        taskId: state.taskId,
        editingDraftId: state.editingDraftId,
        formData: state.formData,
        isUploadCompleted: state.isUploadCompleted,
      }),
    }
  )
);
