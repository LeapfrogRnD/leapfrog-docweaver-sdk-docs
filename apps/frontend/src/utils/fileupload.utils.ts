// utils/fileupload.utils.ts
import { Dispatch, SetStateAction } from 'react';

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  isCompleted: boolean;
}

export const uploadFile = (
  file: File,
  url: string,
  setUploadState: Dispatch<SetStateAction<UploadState>>
): Promise<void> => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percent = 20 + Math.round((event.loaded / event.total) * 60);
        setUploadState((prev) => ({
          ...prev,
          isUploading: true,
          progress: Math.min(percent, 80),
        }));
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed: ${xhr.statusText}`));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Network error')));

    xhr.open('PUT', url);
    xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
    xhr.send(file);
  });
};
