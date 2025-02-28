// src/pages/documents/DocumentViewer.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './DocumentViewer.css';

const DocumentViewer = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [document, setDocument] = useState(null);
    
    const { docId } = useParams();
    const navigate = useNavigate();
    
    useEffect(() => {
        const fetchDocument = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/doc/view/${docId}`);
                if (!response.ok) {
                    throw new Error('Error al cargar el documento');
                }
                
                const data = await response.json();
                setDocument(data);
                setLoading(false);
            } catch (err) {
                console.error("Error:", err);
                setError(err.message);
                setLoading(false);
            }
        };
        
        if (docId) {
            fetchDocument();
        }
    }, [docId]);
    
    const handleBack = () => {
        navigate(-1);
    };
    
    const handleDownload = () => {
        if (!document) return;
        
        const element = document.createElement('a');
        const file = new Blob([document.content], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = document.file_name || `document-${docId}.${document.format}`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };
    
    if (loading) {
        return (
            <div className="document-viewer">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Cargando documento...</p>
                </div>
            </div>
        );
    }
    
    if (error || !document) {
        return (
            <div className="document-viewer">
                <div className="error-message">
                    <h2>Error</h2>
                    <p>{error || 'No se pudo cargar el documento'}</p>
                    <button onClick={handleBack} className="back-button">
                        Volver
                    </button>
                </div>
            </div>
        );
    }
    
    return (
        <div className="document-viewer">
            <div className="document-header">
                <button onClick={handleBack} className="back-button">
                    ← Volver
                </button>
                <h1>{document.file_name || 'Documento'}</h1>
                <button onClick={handleDownload} className="download-button">
                    Descargar
                </button>
            </div>
            
            <div className="document-content">
                {document.format === 'markdown' || document.format === 'md' ? (
                    <div className="markdown-content">
                        <ReactMarkdown>{document.content}</ReactMarkdown>
                    </div>
                ) : document.format === 'html' ? (
                    <div 
                        className="html-content"
                        dangerouslySetInnerHTML={{ __html: document.content }}
                    />
                ) : document.format === 'json' ? (
                    <pre className="json-content">
                        {JSON.stringify(JSON.parse(document.content), null, 2)}
                    </pre>
                ) : (
                    <pre className="plain-content">{document.content}</pre>
                )}
            </div>
        </div>
    );
};

export default DocumentViewer;