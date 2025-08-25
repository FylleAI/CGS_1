import React, { useState, useEffect } from 'react';

// Temporary icon replacements with emoji
const Clock = () => <span>⏰</span>;
const CheckCircle = () => <span>✅</span>;
const AlertCircle = () => <span>⚠️</span>;
const FileText = () => <span>📄</span>;
const Download = () => <span>📥</span>;
const RefreshCw = () => <span>🔄</span>;
const Preview = () => <span>👁️</span>;

interface ProcessingStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  startTime?: Date;
  endTime?: Date;
  error?: string;
}

interface ProcessingJob {
  id: string;
  client: string;
  workflowMode: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  steps: ProcessingStep[];
  startTime: Date;
  endTime?: Date;
  estimatedDuration: number; // in seconds
  results?: {
    files: string[];
    downloadUrl: string;
    exportPath: string;
  };
  error?: string;
}

interface ProcessingMonitorProps {
  job: ProcessingJob;
  onJobComplete?: (job: ProcessingJob) => void;
  onJobError?: (job: ProcessingJob, error: string) => void;
}

const ProcessingMonitor: React.FC<ProcessingMonitorProps> = ({
  job,
  onJobComplete,
  onJobError
}) => {
  const [currentJob, setCurrentJob] = useState<ProcessingJob>(job);
  const [previewFile, setPreviewFile] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update elapsed time every second
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const elapsed = Math.floor((now.getTime() - currentJob.startTime.getTime()) / 1000);
      setElapsedTime(elapsed);
    }, 1000);

    return () => clearInterval(interval);
  }, [currentJob.startTime]);

  // Simulate job progress (in real implementation, this would poll the API)
  useEffect(() => {
    if (currentJob.status === 'processing') {
      const interval = setInterval(() => {
        setCurrentJob(prev => {
          const newProgress = Math.min(prev.progress + 5, 100);
          const newStatus: ProcessingJob['status'] = newProgress === 100 ? 'completed' : 'processing';
          
          // Update steps based on progress
          const updatedSteps = prev.steps.map((step, index) => {
            const stepProgress = Math.max(0, Math.min(100, (newProgress - index * 25)));
            let stepStatus: ProcessingStep['status'] = 'pending';
            
            if (stepProgress > 0 && stepProgress < 100) {
              stepStatus = 'processing';
            } else if (stepProgress === 100) {
              stepStatus = 'completed';
            }
            
            return {
              ...step,
              progress: stepProgress,
              status: stepStatus
            };
          });

          const updatedJob = {
            ...prev,
            progress: newProgress,
            status: newStatus,
            steps: updatedSteps,
            endTime: newStatus === 'completed' ? new Date() : undefined
          };

          // Trigger completion callback
          if (newStatus === 'completed' && onJobComplete) {
            onJobComplete(updatedJob);
          }

          return updatedJob;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [currentJob.status, onJobComplete]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusIcon = (status: ProcessingStep['status']) => {
    switch (status) {
      case 'completed':
        return <span className="text-green-500"><CheckCircle /></span>;
      case 'processing':
        return <span className="text-blue-500"><RefreshCw /></span>;
      case 'error':
        return <span className="text-red-500"><AlertCircle /></span>;
      default:
        return <span className="text-gray-400"><Clock /></span>;
    }
  };

  const getStatusColor = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-blue-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            Processing Knowledge Base
          </h2>
          <p className="text-gray-600">
            {currentJob.client} • {currentJob.workflowMode}
          </p>
        </div>
        
        <div className="text-right">
          <div className={`text-lg font-semibold ${getStatusColor(currentJob.status)}`}>
            {currentJob.status.charAt(0).toUpperCase() + currentJob.status.slice(1)}
          </div>
          <div className="text-sm text-gray-500">
            {formatTime(elapsedTime)} / {formatTime(currentJob.estimatedDuration)}
          </div>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span>{currentJob.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${currentJob.progress}%` }}
          />
        </div>
      </div>

      {/* Processing Steps */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-medium text-gray-900">Processing Steps</h3>
        
        {currentJob.steps.map((step, index) => (
          <div key={step.id} className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              {getStatusIcon(step.status)}
            </div>
            
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-900">
                  {step.name}
                </span>
                <span className="text-xs text-gray-500">
                  {step.progress}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div
                  className={`h-1 rounded-full transition-all duration-300 ${
                    step.status === 'completed' ? 'bg-green-500' :
                    step.status === 'processing' ? 'bg-blue-500' :
                    step.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                  }`}
                  style={{ width: `${step.progress}%` }}
                />
              </div>
              
              {step.error && (
                <p className="text-xs text-red-600 mt-1">{step.error}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Results Section */}
      {currentJob.status === 'completed' && currentJob.results && (
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Generated Files
          </h3>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div className="flex items-center text-green-600 mb-2">
              <span className="mr-2 text-green-500"><CheckCircle /></span>
              <span className="font-medium">
                Knowledge Base Generated Successfully!
              </span>
            </div>
            
            <p className="text-green-700 text-sm">
              {currentJob.results.files.length} files generated in {formatTime(elapsedTime)}
            </p>
          </div>
          
          <div className="space-y-2 mb-4">
            {currentJob.results.files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-blue-500"><FileText /></span>
                  <span className="text-sm font-medium">{file}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setPreviewFile(file)}
                    className="flex items-center text-green-600 hover:text-green-800 text-sm px-2 py-1 rounded hover:bg-green-50 transition-colors"
                  >
                    <span className="mr-1"><Preview /></span>
                    Preview
                  </button>
                  <button
                    onClick={() => {
                      // Download individual file
                      const url = `/api/v1/kba/file/${currentJob.client}/${currentJob.workflowMode}/${currentJob.id}/${file}`;
                      window.open(url, '_blank');
                    }}
                    className="flex items-center text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                  >
                    <span className="mr-1"><Download /></span>
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={() => {
                window.open(currentJob.results!.downloadUrl, '_blank');
              }}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <span className="mr-2"><Download /></span>
              Download All (ZIP)
            </button>
            
            <button
              onClick={() => {
                // Copy export path to clipboard
                navigator.clipboard.writeText(currentJob.results!.exportPath);
              }}
              className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Copy Export Path
            </button>
          </div>
        </div>
      )}

      {/* Error Section */}
      {currentJob.status === 'error' && (
        <div className="border-t pt-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center text-red-600 mb-2">
              <span className="mr-2 text-red-500"><AlertCircle /></span>
              <span className="font-medium">Processing Failed</span>
            </div>
            
            <p className="text-red-700 text-sm">
              {currentJob.error || 'An unknown error occurred during processing.'}
            </p>
            
            <button
              onClick={() => {
                // Retry logic would go here
                console.log('Retry processing');
              }}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
            >
              Retry Processing
            </button>
          </div>
        </div>
      )}

      {/* File Preview Modal */}
      {previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Preview: {previewFile}</h3>
              <button
                onClick={() => setPreviewFile(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe
                src={`http://localhost:8000/api/v1/kba/preview/${currentJob.client}/${currentJob.workflowMode}/${currentJob.id}/${previewFile}`}
                className="w-full h-full border-0"
                title={`Preview of ${previewFile}`}
              />
            </div>
            <div className="p-4 border-t flex justify-end space-x-2">
              <button
                onClick={() => setPreviewFile(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const url = `/api/v1/kba/file/${currentJob.client}/${currentJob.workflowMode}/${currentJob.id}/${previewFile}`;
                  window.open(url, '_blank');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessingMonitor;
