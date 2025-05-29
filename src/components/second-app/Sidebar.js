// src/components/Sidebar.js - Sidebar component with conversation history
import React from 'react';
import './Sidebar.css';

function Sidebar({ conversations, onNewChat, selectedModel, onModelChange }) {
    // Available AI models
    const models = [
        { id: 'gpt-3.5', name: 'Phi 3' },
        { id: 'gpt-4', name: 'Phi 4' },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo" >
                    <img src="/generated-image.png" alt="IBPS Logo" className="ibps-logo" style={{ width: "100%" }}/>
                </div>
                <button className="new-chat-btn" style={{width: "100%"}} onClick={onNewChat}>+ New chat</button>
            </div>

            {/* <div className="model-selector">
                <label htmlFor="model-select">Select Model:</label>
                <select
                    id="model-select"
                    value={selectedModel}
                    onChange={(e) => onModelChange(e.target.value)}
                >
                    {models.map(model => (
                        <option key={model.id} value={model.id}>
                            {model.name}
                        </option>
                    ))}
                </select>
            </div> */}

            <div className="conversations-list">
                <h2>Recent conversations</h2>
                {conversations.length > 0 ? (
                    conversations.map(convo => (
                        <div key={convo.id} className="conversation-item">
                            {convo.title}
                        </div>
                    ))
                ) : (
                    <p className="no-conversations">No conversations yet</p>
                )}
            </div>

            <div className="sidebar-footer">
                <div className="user-info">
                    <img src="/man.png" alt="User" className="user-avatar" />
                    <span>User</span>
                </div>
            </div>
        </aside>
    );
}

export default Sidebar;
