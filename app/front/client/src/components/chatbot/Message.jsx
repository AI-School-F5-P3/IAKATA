import React from 'react';

const Message = ({ message }) => {
  const hasAnalysis = message.sender === 'bot' && message.analysis_data;

  return (
    <div className={`chat-message ${message.sender}`}>
      {message.text}

      {hasAnalysis && (
        <div className="analysis-summary">
          <h4>Análisis de Proyecto: {message.analysis_data.project_name}</h4>
          <p>Estado: {message.analysis_data.status}</p>
          <p>Puntuación: {message.analysis_data.overall_score}</p>

          <h5>Insights:</h5>
          <ul>
            {message.analysis_data.insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>

          <a href={`/analysis/${message.board_id}`}>Ver análisis completo</a>
        </div>
      )}
    </div>
  );
};

export default Message;
