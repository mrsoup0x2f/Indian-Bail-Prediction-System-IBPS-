import React from "react";
import "./ConfidenceBar.css";

const ConfidenceBar = ({ 
    confidenceScore, 
    height = '100vh',
    width = '40px',
    bgColor = '#e0e0de',
    labelColor = '#fff',
    showLabel = true,
    className = ''
}) => {
  // Ensure score is between 0-100
    const normalizedScore = Math.min(Math.max(confidenceScore, 0), 100);
    
    const getColorByConfidence = (score) => {
    if (score >= 80) return '#4CAF50'; // High confidence - Green
    if (score >= 60) return '#8BC34A'; // Good confidence - Light Green
    if (score >= 40) return '#FFC107'; // Medium confidence - Amber
    if (score >= 20) return '#FF9800'; // Low confidence - Orange
    return '#F44336'; // Very low confidence - Red
    };

    const fillColor = getColorByConfidence(normalizedScore);
    return (
        <div className={`vertical-progress-container ${className}`} style={{ height, width }}>
        <div className="vertical-progress-bar" style={{ backgroundColor: bgColor }}>
            <div 
            className="vertical-progress-fill" 
            style={{ 
                height: `${normalizedScore}%`, 
                backgroundColor: fillColor,
                bottom: 0
            }}
            >
            {showLabel && (
                <span className="vertical-progress-label" style={{ color: labelColor }}>
                {normalizedScore.toFixed(0)}%
                </span>
            )}
            </div>
        </div>
        <div className="confidence-label">Confidence</div>
        </div>
    );
};

export default ConfidenceBar;