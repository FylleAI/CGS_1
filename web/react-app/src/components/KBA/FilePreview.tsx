import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Description as FileTextIcon,
  Code as CodeIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

interface FilePreviewProps {
  open: boolean;
  onClose: () => void;
  client: string;
  workflowMode: string;
  workflowId: string;
  filename: string;
}

interface FilePreviewData {
  filename: string;
  file_type: string;
  content: string;
  size_bytes: number;
  word_count: number;
  line_count: number;
  last_modified: string;
  download_url: string;
}

const FilePreview: React.FC<FilePreviewProps> = ({
  open,
  onClose,
  client,
  workflowMode,
  workflowId,
  filename
}) => {
  const [previewData, setPreviewData] = useState<FilePreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'preview' | 'raw'>('preview');

  useEffect(() => {
    if (open && filename) {
      fetchPreview();
    }
  }, [open, filename, client, workflowMode, workflowId]);

  const fetchPreview = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/kba/preview/${client}/${workflowMode}/${workflowId}/${filename}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to load preview: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (previewData) {
      window.open(`http://localhost:8000${previewData.download_url}`, '_blank');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  const renderContent = () => {
    if (!previewData) return null;

    if (viewMode === 'raw') {
      return (
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            backgroundColor: 'grey.50',
            maxHeight: 500,
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            whiteSpace: 'pre-wrap'
          }}
        >
          {previewData.content}
        </Paper>
      );
    }

    // Preview mode
    if (previewData.file_type === 'markdown') {
      return (
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            maxHeight: 500,
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6
          }}
        >
          {previewData.content}
        </Paper>
      );
    }

    if (previewData.file_type === 'json') {
      try {
        const jsonData = JSON.parse(previewData.content);
        return (
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              backgroundColor: 'grey.50',
              maxHeight: 500,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem'
            }}
          >
            <pre>{JSON.stringify(jsonData, null, 2)}</pre>
          </Paper>
        );
      } catch {
        // Fall back to raw text if JSON parsing fails
      }
    }

    // Default text preview
    return (
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          backgroundColor: 'grey.50',
          maxHeight: 500,
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          whiteSpace: 'pre-wrap'
        }}
      >
        {previewData.content}
      </Paper>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FileTextIcon color="primary" />
            <Typography variant="h6" component="span">
              {filename}
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {previewData && (
          <Box>
            {/* File Info */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<FileTextIcon />}
                  label={previewData.file_type.toUpperCase()}
                  size="small"
                  color="primary"
                />
                <Chip
                  label={formatFileSize(previewData.size_bytes)}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`${previewData.word_count} words`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`${previewData.line_count} lines`}
                  size="small"
                  variant="outlined"
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Last modified: {formatDate(previewData.last_modified)}
              </Typography>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* View Mode Tabs */}
            <Box sx={{ mb: 2 }}>
              <Tabs
                value={viewMode}
                onChange={(_, newValue) => setViewMode(newValue)}
              >
                <Tab
                  icon={<VisibilityIcon />}
                  label="Preview"
                  value="preview"
                  iconPosition="start"
                />
                <Tab
                  icon={<CodeIcon />}
                  label="Raw"
                  value="raw"
                  iconPosition="start"
                />
              </Tabs>
            </Box>

            {/* Content */}
            {renderContent()}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
        <Button
          onClick={handleDownload}
          variant="contained"
          startIcon={<DownloadIcon />}
          disabled={!previewData}
        >
          Download
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FilePreview;
