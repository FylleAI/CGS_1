import React, { useState, useCallback } from 'react';

// Temporary icon replacements with emoji
const Upload = () => <span>📤</span>;
const FileText = () => <span>📄</span>;
const Globe = () => <span>🌐</span>;
const Download = () => <span>📥</span>;
const CheckCircle = () => <span>✅</span>;
const AlertCircle = () => <span>⚠️</span>;
const Clock = () => <span>⏰</span>;

interface KBASource {
  id: string;
  type: 'file' | 'url';
  name: string;
  content?: File;
  url?: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

interface KBAJob {
  id: string;
  client: string;
  workflowMode: string;
  sources: KBASource[];
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  results?: {
    files: string[];
    downloadUrl: string;
  };
  error?: string;
}

const KBAInterface: React.FC = () => {
  const [sources, setSources] = useState<KBASource[]>([]);
  const [client, setClient] = useState('');
  const [workflowMode, setWorkflowMode] = useState('brand_kba_4docs');
  const [customInstructions, setCustomInstructions] = useState('');
  const [currentJob, setCurrentJob] = useState<KBAJob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const workflowModes = [
    {
      id: 'brand_kba_4docs',
      name: 'Brand Knowledge Base',
      description: 'Generate comprehensive brand guidelines (4 documents)',
      estimatedTime: '3-7 minutes',
      outputCount: 4
    },
    {
      id: 'faq_kba',
      name: 'FAQ Knowledge Base',
      description: 'Create structured FAQ from sources (2 documents)',
      estimatedTime: '2-5 minutes',
      outputCount: 2
    },
    {
      id: 'documentation_kba',
      name: 'Documentation Knowledge Base',
      description: 'Technical documentation structure (4 documents)',
      estimatedTime: '4-8 minutes',
      outputCount: 4
    },
    {
      id: 'training_kba',
      name: 'Training Knowledge Base',
      description: 'Training materials organization (4 documents)',
      estimatedTime: '5-10 minutes',
      outputCount: 4
    }
  ];

  const handleFileUpload = useCallback((files: FileList) => {
    const newSources: KBASource[] = Array.from(files).map(file => ({
      id: `file-${Date.now()}-${Math.random()}`,
      type: 'file',
      name: file.name,
      content: file,
      status: 'pending'
    }));
    setSources(prev => [...prev, ...newSources]);
  }, []);

  const handleUrlAdd = useCallback((url: string) => {
    if (!url.trim()) return;
    
    const newSource: KBASource = {
      id: `url-${Date.now()}-${Math.random()}`,
      type: 'url',
      name: url,
      url: url.trim(),
      status: 'pending'
    };
    setSources(prev => [...prev, newSource]);
  }, []);

  const removeSource = useCallback((id: string) => {
    setSources(prev => prev.filter(source => source.id !== id));
  }, []);

  const handleSubmit = async () => {
    if (!client.trim() || sources.length === 0) {
      alert('Please provide client name and at least one source');
      return;
    }

    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('client', client);
      formData.append('workflow_mode', workflowMode);
      formData.append('custom_instructions', customInstructions);

      // Add files
      sources.forEach(source => {
        if (source.type === 'file' && source.content) {
          formData.append('files', source.content);
        }
      });

      // Add URLs (if any) - would need API modification to support URLs in upload
      const urls = sources.filter(s => s.type === 'url').map(s => s.url);
      if (urls.length > 0) {
        formData.append('urls', JSON.stringify(urls));
      }

      const response = await fetch('http://localhost:8000/api/v1/kba/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('API Response:', result);

      if (result.success) {
        setCurrentJob({
          id: result.workflow_id,
          client,
          workflowMode,
          sources,
          status: 'completed',
          progress: 100,
          results: {
            files: result.files || [],
            downloadUrl: `/api/v1/kba/download/${result.workflow_id}`
          }
        });
      } else {
        throw new Error(result.message || 'Processing failed');
      }
    } catch (error) {
      console.error('KBA processing error:', error);

      let errorMessage = 'Unknown error occurred';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      setCurrentJob({
        id: `error-${Date.now()}`,
        client,
        workflowMode,
        sources,
        status: 'error',
        progress: 0,
        error: errorMessage
      });

      // Also show an alert for immediate feedback
      alert(`Processing failed: ${errorMessage}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setSources([]);
    setClient('');
    setCustomInstructions('');
    setCurrentJob(null);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🤖 Knowledge Base Assistant
        </h1>
        <p className="text-gray-600 mb-6">
          Transform multiple sources into structured knowledge base documents
        </p>

        {/* Client Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client Name
            </label>
            <input
              type="text"
              value={client}
              onChange={(e) => setClient(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter client/company name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Workflow Mode
            </label>
            <select
              value={workflowMode}
              onChange={(e) => setWorkflowMode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {workflowModes.map(mode => (
                <option key={mode.id} value={mode.id}>
                  {mode.name} ({mode.outputCount} files)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Workflow Mode Details */}
        {workflowMode && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            {(() => {
              const mode = workflowModes.find(m => m.id === workflowMode);
              return mode ? (
                <div>
                  <h3 className="font-semibold text-blue-900">{mode.name}</h3>
                  <p className="text-blue-700 text-sm">{mode.description}</p>
                  <p className="text-blue-600 text-xs mt-1">
                    ⏱️ {mode.estimatedTime} | 📄 {mode.outputCount} output files
                  </p>
                </div>
              ) : null;
            })()}
          </div>
        )}

        {/* File Upload Zone */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6">
          <div className="mx-auto h-12 w-12 text-gray-400 mb-4 text-4xl"><Upload /></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Upload Files or Add URLs
          </h3>
          <p className="text-gray-600 mb-4">
            Supported: PDF, DOCX, MD, TXT files and web URLs
          </p>
          
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.md,.txt"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
            className="hidden"
            id="file-upload"
          />
          
          <div className="space-y-2">
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
            >
              <span className="mr-2"><FileText /></span>
              Choose Files
            </label>
            
            <div className="flex items-center space-x-2">
              <input
                type="url"
                placeholder="Enter URL to add"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleUrlAdd(e.currentTarget.value);
                    e.currentTarget.value = '';
                  }
                }}
              />
              <button
                onClick={() => {
                  const input = document.querySelector('input[type="url"]') as HTMLInputElement;
                  if (input) {
                    handleUrlAdd(input.value);
                    input.value = '';
                  }
                }}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
              >
                <Globe />
              </button>
            </div>
          </div>
        </div>

        {/* Sources List */}
        {sources.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Sources ({sources.length})
            </h3>
            <div className="space-y-2">
              {sources.map(source => (
                <div key={source.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {source.type === 'file' ? (
                      <span className="text-blue-500"><FileText /></span>
                    ) : (
                      <span className="text-green-500"><Globe /></span>
                    )}
                    <span className="text-sm font-medium">{source.name}</span>
                    <span className="text-xs text-gray-500">({source.type})</span>
                  </div>
                  <button
                    onClick={() => removeSource(source.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Custom Instructions */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Instructions (Optional)
          </label>
          <textarea
            value={customInstructions}
            onChange={(e) => setCustomInstructions(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add specific instructions for content generation..."
          />
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !client.trim() || sources.length === 0}
            className="flex-1 flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <span className="mr-2"><Clock /></span>
                Processing...
              </>
            ) : (
              <>
                🚀 Generate Knowledge Base
              </>
            )}
          </button>
          
          <button
            onClick={resetForm}
            className="px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Results Section */}
      {currentJob && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Processing Results
          </h2>
          
          {currentJob.status === 'completed' && currentJob.results && (
            <div className="space-y-4">
              <div className="flex items-center text-green-600">
                <span className="mr-2 text-green-500"><CheckCircle /></span>
                <span className="font-medium">Knowledge Base Generated Successfully!</span>
              </div>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-medium text-green-900 mb-3">Generated Files:</h3>
                <div className="space-y-2">
                  {currentJob.results.files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-white p-3 rounded border">
                      <div className="flex items-center space-x-2">
                        <span className="text-green-600">📄</span>
                        <span className="text-sm font-medium text-gray-900">{file}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            // Preview functionality - could open modal or new tab
                            const url = `http://localhost:8000/api/v1/kba/preview/${currentJob.client}/${currentJob.workflowMode}/${currentJob.id}/${file}`;
                            window.open(url, '_blank');
                          }}
                          className="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded hover:bg-blue-50"
                        >
                          👁️ Preview
                        </button>
                        <button
                          onClick={() => {
                            const url = `http://localhost:8000/api/v1/kba/file/${currentJob.client}/${currentJob.workflowMode}/${currentJob.id}/${file}`;
                            window.open(url, '_blank');
                          }}
                          className="text-green-600 hover:text-green-800 text-sm px-2 py-1 rounded hover:bg-green-50"
                        >
                          📥 Download
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex space-x-4">
                <a
                  href={currentJob.results.downloadUrl}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <span className="mr-2"><Download /></span>
                  Download All Files (ZIP)
                </a>
                
                <button
                  onClick={resetForm}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Start New Process
                </button>
              </div>
            </div>
          )}
          
          {currentJob.status === 'error' && (
            <div className="space-y-4">
              <div className="flex items-center text-red-600">
                <span className="mr-2 text-red-500"><AlertCircle /></span>
                <span className="font-medium">Processing Failed</span>
              </div>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700 text-sm">{currentJob.error}</p>
              </div>
              
              <button
                onClick={resetForm}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KBAInterface;
