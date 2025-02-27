// En un archivo como AnalysisDashboard.jsx
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ProjectAnalysisDashboard = ({ projectId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [trendData, setTrendData] = useState([]);

  // Cargar datos de análisis
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Solicitar análisis actual
        const analysisResponse = await fetch(`/analysis/projects/${projectId}`);
        if (!analysisResponse.ok) {
          throw new Error('Error al cargar datos de análisis');
        }
        const analysisData = await analysisResponse.json();
        setAnalysis(analysisData);
        
        // Solicitar datos de tendencia
        const trendResponse = await fetch(`/analysis/projects/${projectId}/trend`);
        if (!trendResponse.ok) {
          throw new Error('Error al cargar datos de tendencia');
        }
        const trendData = await trendResponse.json();
        setTrendData(trendData.data_points || []);
        
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (projectId) {
      fetchData();
    }
  }, [projectId]);

  if (loading) return <div className="loading-container">Cargando análisis...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!analysis) return <div>No hay datos de análisis disponibles</div>;

  // Determinar color según el estado
  const getStatusColor = (status) => {
    switch (status) {
      case 'on_track': return 'status-good';
      case 'needs_adjustment': return 'status-warning';
      case 'at_risk': return 'status-danger';
      default: return 'status-neutral';
    }
  };

  // Formatear números para métricas
  const formatMetric = (value) => {
    if (typeof value === 'string' && value.includes('%')) return value;
    if (typeof value === 'number') return `${(value * 100).toFixed(1)}%`;
    return value;
  };

  return (
    <div className="analysis-dashboard">
      <div className="dashboard-header">
        <h1>{analysis.project_name}</h1>
        
        <div className="status-container">
          <span className={`status-badge ${getStatusColor(analysis.status.status)}`}>
            {analysis.status.status === 'on_track' ? 'En buen camino' : 
             analysis.status.status === 'needs_adjustment' ? 'Necesita ajustes' : 'En riesgo'}
          </span>
          <span className="last-updated">
            Actualizado: {new Date(analysis.analyzed_at).toLocaleString()}
          </span>
          
          <button 
            onClick={() => window.location.reload()} 
            className="refresh-button"
          >
            Actualizar
          </button>
        </div>
      </div>

      {/* Resumen de métricas */}
      <div className="metrics-summary">
        <div className="metric-card">
          <h2>Puntuación general</h2>
          <div className="metric-value">
            {analysis.metrics.puntaje_general || formatMetric(analysis.metrics.overall_score)}
          </div>
          <div className="metric-trend">
            Tendencia: {analysis.trend === 'improving' ? '↗️ Mejorando' : 
                        analysis.trend === 'declining' ? '↘️ Deteriorando' : '→ Estable'}
          </div>
        </div>
        
        <div className="metric-card">
          <h2>Adherencia al proceso</h2>
          <div className="metric-value">
            {analysis.metrics.adherencia_proceso || formatMetric(analysis.metrics.process_adherence)}
          </div>
          <div className="metric-trend">
            Media organizacional: {formatMetric(0.72)}
          </div>
        </div>
        
        <div className="metric-card">
          <h2>Progreso hacia objetivo</h2>
          <div className="metric-value">
            {analysis.metrics.progreso_objetivo || formatMetric(analysis.metrics.target_achievement)}
          </div>
          <div className="metric-trend">
            Ciclo de experimentos: {analysis.metrics.tiempo_ciclo_experimentos || 
                                  `${analysis.metrics.experiment_cycle_time.toFixed(1)} días`}
          </div>
        </div>
      </div>

      {/* Gráfico de tendencia */}
      {trendData.length > 0 && (
        <div className="trend-chart-container">
          <h2>Tendencia del proyecto</h2>
          <div className="trend-chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis 
                  domain={[0, 1]} 
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} 
                />
                <Tooltip 
                  formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Puntuación']} 
                  labelFormatter={(label) => `Fecha: ${label}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="overall_score" 
                  name="Puntuación general" 
                  stroke="#3182ce" 
                  activeDot={{ r: 8 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="adherence" 
                  name="Adherencia" 
                  stroke="#10b981" 
                />
                <Line 
                  type="monotone" 
                  dataKey="target_progress" 
                  name="Progreso objetivo" 
                  stroke="#8b5cf6" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Insights y Recomendaciones */}
      <div className="insights-recommendations">
        <div className="insights-container">
          <h2>Insights clave</h2>
          <ul className="insights-list">
            {analysis.insights.map((insight, index) => (
              <li key={index} className={`insight-item ${insight.type}`}>
                <div className="insight-content">
                  <p>{insight.description}</p>
                  {insight.related_metric && (
                    <p className="related-metric">
                      Relacionado con: {insight.related_metric.replace(/_/g, ' ')}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="recommendations-container">
          <h2>Recomendaciones</h2>
          <ul className="recommendations-list">
            {analysis.recommendations.map((rec, index) => (
              <li key={index} className={`recommendation-item priority-${rec.priority}`}>
                <div className="recommendation-content">
                  <div className="priority-tag">{rec.priority}</div>
                  <p className="recommendation-action">{rec.action}</p>
                  <p className="recommendation-impact">{rec.impact}</p>
                  <p className="recommendation-time">Tiempo estimado: {rec.estimated_time}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Factores de riesgo */}
      {analysis.status.risk_factors && analysis.status.risk_factors.length > 0 && (
        <div className="risk-factors-container">
          <h2>Factores de riesgo</h2>
          <ul className="risk-list">
            {analysis.status.risk_factors.map((risk, index) => (
              <li key={index} className="risk-item">
                <span className="risk-icon">⚠️</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Obstáculos bloqueantes */}
      {analysis.status.blocking_obstacles && analysis.status.blocking_obstacles.length > 0 && (
        <div className="obstacles-container">
          <h2>Obstáculos bloqueantes</h2>
          <table className="obstacles-table">
            <thead>
              <tr>
                <th>Obstáculo</th>
                <th>Prioridad</th>
                <th>Días abierto</th>
              </tr>
            </thead>
            <tbody>
              {analysis.status.blocking_obstacles.map((obstacle, index) => (
                <tr key={index}>
                  <td>{obstacle.description}</td>
                  <td>
                    <span className={`priority-badge priority-${obstacle.priority}`}>
                      {obstacle.priority}
                    </span>
                  </td>
                  <td>{obstacle.days_open}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ProjectAnalysisDashboard;