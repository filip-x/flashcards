import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles } from 'lucide-react';
import { uploadFile, generateFlashcards } from '../api';

const UploadSection = ({ onGenerationSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) return;
    
    setError('');
    setIsUploading(true);
    
    try {
      // 1. Upload the file
      const doc = await uploadFile(selectedFile);
      
      setIsUploading(false);
      setIsGenerating(true);
      
      // 2. Instruct backend to generate smart flashcards
      const result = await generateFlashcards(doc.id);
      
      if (result && result.flashcards) {
        onGenerationSuccess(result.total);
      }
    } catch (err) {
      setError(err.message || 'An error occurred during process');
      setIsUploading(false);
      setIsGenerating(false);
    }
  };

  if (isUploading || isGenerating) {
    return (
      <div className="upload-container">
        <div className="loader-container">
          <div className="spinner"></div>
          <h2 className="upload-title">
            {isUploading ? 'Uploading Document...' : 'Synthesizing Neural Flashcards...'}
          </h2>
          <p className="upload-subtitle text-secondary">
            {isGenerating && 'Our AI is extracting core concepts and generating perfect spaced-repetition cards.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="upload-container">
      <div>
        <h1 className="upload-title text-gradient">Master Any Document</h1>
        <p className="upload-subtitle">
          Upload your PDF, text, or markdown file. We'll extract the knowledge and build a bespoke spaced-repetition curriculum.
        </p>
      </div>

      <div 
        className={`dropzone ${isDragging ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud size={48} className="upload-icon" />
        <h3 style={{ fontFamily: 'Outfit', fontWeight: 600 }}>Drag & Drop to Upload</h3>
        <p className="text-secondary">Supported formats: .pdf, .txt, .md</p>
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".pdf,.txt,.md"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              setSelectedFile(e.target.files[0]);
            }
          }}
        />
      </div>

      {selectedFile && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '600px' }}>
          <div className="file-info glass-panel" style={{ width: '100%' }}>
            <FileText size={24} color="var(--accent-cyan)" />
            <div style={{ textAlign: 'left', flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{selectedFile.name}</div>
              <div style={{ fontSize: '0.8rem' }} className="text-secondary">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            <button 
              className="btn btn-primary" 
              onClick={(e) => {
                e.stopPropagation();
                handleProcess();
              }}
            >
              <Sparkles size={16} /> Generate Knowledge
            </button>
          </div>
        </div>
      )}

      {error && <div style={{ color: '#ff5b5b', marginTop: '1rem', padding: '1rem', background: 'rgba(255,0,0,0.1)', borderRadius: '8px' }}>{error}</div>}
    </div>
  );
};

export default UploadSection;
