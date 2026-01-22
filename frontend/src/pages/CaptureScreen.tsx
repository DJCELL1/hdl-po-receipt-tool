import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function CaptureScreen() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError('');
    }
  };

  const handleCapture = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsProcessing(true);
    setError('');

    try {
      const result = await api.uploadDocket(file);
      navigate('/review', { state: { extractedData: result.extractedData, uploadId: result.uploadId } });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to process docket');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <div className="header">
        <h1>Scan Docket</h1>
        <button onClick={() => navigate('/dashboard')} className="btn btn-outline">Cancel</button>
      </div>
      <div className="container">
        {error && <div className="alert alert-error">{error}</div>}

        <div className="card">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,application/pdf"
            capture="environment"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {!preview ? (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📷</div>
              <h2 style={{ marginBottom: '12px' }}>Capture or Upload Docket</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                Take a photo of your delivery docket or upload an existing image/PDF
              </p>
              <button onClick={handleCapture} className="btn btn-primary">
                {/iPhone|iPad|iPod|Android/i.test(navigator.userAgent) ? '📷 Take Photo' : '📁 Select File'}
              </button>
            </div>
          ) : (
            <>
              <div className="camera-container">
                <img src={preview} alt="Captured docket" />
              </div>
              <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
                <button onClick={handleCapture} className="btn btn-outline" style={{ flex: 1 }}>
                  Retake
                </button>
                <button
                  onClick={handleUpload}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Processing...' : 'Continue'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
