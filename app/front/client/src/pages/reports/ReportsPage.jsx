import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ReportsPage.css';

const ReportsPage = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [projectData, setProjectData] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [templates, setTemplates] = useState([]);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [generatingReport, setGeneratingReport] = useState(false);
    const [selectedFormat, setSelectedFormat] = useState('markdown');
    const [successMessage, setSuccessMessage] = useState('');
    
    const { projectId } = useParams();
    const navigate = useNavigate();
    
    // Cargar datos iniciales
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Obtener datos del proyecto
                const projectResponse = await fetch(`/challenge/${projectId}`);
                if (!projectResponse.ok) {
                    throw new Error(`Error al cargar datos del proyecto: ${projectResponse.statusText}`);
                }
                const projectData = await projectResponse.json();
                setProjectData(projectData);
                
                // Obtener documentos existentes
                const documentsResponse = await fetch(`/doc/project/${projectId}`);
                if (documentsResponse.ok) {
                    const docData = await documentsResponse.json();
                    setDocuments(docData.documents || []);
                }
                
                // Obtener templates disponibles
                const templatesResponse = await fetch('/doc/templates');
                if (!templatesResponse.ok) {
                    throw new Error(`Error al cargar templates: ${templatesResponse.statusText}`);
                }
                const templatesData = await templatesResponse.json();
                setTemplates(templatesData);
                
                setLoading(false);
            } catch (err) {
                console.error("Error cargando datos:", err);
                setError(err.message);
                setLoading(false);
            }
        };
        
        if (projectId) {
            fetchData();
        }
    }, [projectId]);
    
    // Generar un informe
    const handleGenerateReport = async () => {
        if (!selectedTemplate) {
            setError("Por favor selecciona un tipo de informe");
            return;
        }
        
        setGeneratingReport(true);
        setError(null);
        setSuccessMessage('');
        
        try {
            const response = await fetch('/doc/generate-documentation-with-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project_id: projectId,
                    template_id: selectedTemplate,
                    format: selectedFormat,
                    include_raw_metrics: false
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error generando informe');
            }
            
            const result = await response.json();
            
            // Actualizar lista de documentos
            const documentsResponse = await fetch(`/doc/project/${projectId}`);
            if (documentsResponse.ok) {
                const docData = await documentsResponse.json();
                setDocuments(docData.documents || []);
            }
            
            setSuccessMessage('¡Informe generado exitosamente!');
            setSelectedTemplate(null);
        } catch (err) {
            console.error("Error generando informe:", err);
            setError(err.message);
        } finally {
            setGeneratingReport(false);
        }
    };
    
    // Ver un documento
    const handleViewDocument = (docId) => {
        window.open(`/doc/view/${docId}`, '_blank');
    };
    
    // Formatear fecha
    const formatDate = (timestamp) => {
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };
    
    // Obtener nombre del formato para mostrar
    const getFormatName = (format) => {
        switch (format.toLowerCase()) {
            case 'md':
            case 'markdown':
                return 'Markdown';
            case 'html':
                return 'HTML';
            case 'json':
                return 'JSON';
            case 'pdf':
                return 'PDF';
            default:
                return format.toUpperCase();
        }
    };
    
    if (loading) {
        return (
            <div className="reports-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Cargando información...</p>
                </div>
            </div>
        );
    }
    
    if (error && !documents.length && !templates.length) {
        return (
            <div className="reports-container">
                <div className="error-message">
                    <h2>Error</h2>
                    <p>{error}</p>
                    <button onClick={() => navigate(-1)} className="back-button">
                        Volver
                    </button>
                </div>
            </div>
        );
    }
    
    return (
        <div className="reports-container">
            <div className="reports-header">
                <h1>Informes y Documentación</h1>
                {projectData && (
                    <h2>{projectData.name || `Proyecto ${projectId}`}</h2>
                )}
                <button onClick={() => navigate(-1)} className="back-button">
                    Volver al Tablero
                </button>
            </div>
            
            {error && (
                <div className="error-notification">
                    <p>{error}</p>
                    <button onClick={() => setError(null)}>✕</button>
                </div>
            )}
            
            {successMessage && (
                <div className="success-notification">
                    <p>{successMessage}</p>
                    <button onClick={() => setSuccessMessage('')}>✕</button>
                </div>
            )}
            
            <div className="reports-content">
                <div className="report-generator-section">
                    <h3>Generar Nuevo Informe</h3>
                    <div className="generator-form">
                        <div className="form-group">
                            <label>Tipo de Informe:</label>
                            <select 
                                value={selectedTemplate || ''} 
                                onChange={(e) => setSelectedTemplate(e.target.value)}
                                disabled={generatingReport}
                            >
                                <option value="">Seleccionar tipo de informe</option>
                                {templates.map(template => (
                                    <option key={template.id} value={template.id}>
                                        {template.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        
                        <div className="form-group">
                            <label>Formato:</label>
                            <select 
                                value={selectedFormat} 
                                onChange={(e) => setSelectedFormat(e.target.value)}
                                disabled={generatingReport}
                            >
                                <option value="markdown">Markdown</option>
                                <option value="html">HTML</option>
                                <option value="json">JSON</option>
                            </select>
                        </div>
                        
                        <button 
                            onClick={handleGenerateReport} 
                            disabled={!selectedTemplate || generatingReport}
                            className="generate-button"
                        >
                            {generatingReport ? 'Generando...' : 'Generar Informe'}
                        </button>
                    </div>
                </div>
                
                <div className="documents-section">
                    <h3>Informes Existentes</h3>
                    
                    {documents.length === 0 ? (
                        <div className="no-documents">
                            <p>No hay informes generados para este proyecto.</p>
                            <p>Utiliza el formulario para generar un nuevo informe.</p>
                        </div>
                    ) : (
                        <div className="documents-list">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Nombre</th>
                                        <th>Tipo</th>
                                        <th>Formato</th>
                                        <th>Fecha</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {documents.map((doc, index) => (
                                        <tr key={index}>
                                            <td>{doc.file_name}</td>
                                            <td>{doc.type}</td>
                                            <td>{getFormatName(doc.format)}</td>
                                            <td>{formatDate(doc.created_at)}</td>
                                            <td>
                                                <button 
                                                    onClick={() => handleViewDocument(doc.id)}
                                                    className="view-button"
                                                >
                                                    Ver
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ReportsPage;