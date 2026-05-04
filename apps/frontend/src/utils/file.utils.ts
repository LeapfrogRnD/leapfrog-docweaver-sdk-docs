export const formatFileSize = (sizeInBytes: number): string => {
  if (!sizeInBytes || sizeInBytes < 0) {
    return 'N/A';
  }
  if (sizeInBytes >= 1024 * 1024) {
    return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
  } else if (sizeInBytes >= 1024) {
    return `${(sizeInBytes / 1024).toFixed(1)} KB`;
  } else {
    return `${sizeInBytes} B`;
  }
};
