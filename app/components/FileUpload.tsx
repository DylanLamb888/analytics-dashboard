"use client";

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileIcon, AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { uploadApi } from '@/app/lib/api';
import { motion, AnimatePresence } from 'framer-motion';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    setSuccess(null);

    if (rejectedFiles.length > 0) {
      setError('Please upload a valid CSV file under 5MB');
      return;
    }

    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await uploadApi.uploadCsv(file);
      setSuccess(`Successfully processed ${result.rows_processed} orders`);
      setFile(null);
      setTimeout(() => {
        onUploadSuccess();
      }, 1500);
    } catch (err: any) {
      console.error('Upload error:', err.response?.data);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Failed to upload file';
      setError(typeof errorMessage === 'string' ? errorMessage : errorMessage.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="p-6">
        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-all duration-200 ease-in-out
            ${isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
            ${file ? 'bg-secondary/10' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <motion.div
            initial={{ scale: 1 }}
            animate={{ scale: isDragActive ? 1.05 : 1 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center justify-center space-y-4"
          >
            {file ? (
              <>
                <FileIcon className="w-12 h-12 text-primary" />
                <div>
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">
                    {isDragActive ? 'Drop your CSV file here' : 'Drag & drop your CSV file here'}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    or click to browse (max 5MB)
                  </p>
                </div>
              </>
            )}
          </motion.div>
        </div>

        <AnimatePresence>
          {(error || success) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-4"
            >
              {error && (
                <div className="flex items-center space-x-2 text-destructive">
                  <AlertCircle className="w-4 h-4" />
                  <p className="text-sm">{error}</p>
                </div>
              )}
              {success && (
                <div className="flex items-center space-x-2 text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  <p className="text-sm">{success}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {file && !success && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 flex justify-end space-x-2"
          >
            <Button
              variant="outline"
              onClick={() => {
                setFile(null);
                setError(null);
              }}
              disabled={uploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? 'Processing...' : 'Upload & Process'}
            </Button>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};