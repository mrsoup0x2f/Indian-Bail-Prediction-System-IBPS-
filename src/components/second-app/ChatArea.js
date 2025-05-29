// src/components/ChatArea.js - Main chat display area
import React from 'react';
import Message from './Message';
import './ChatArea.css';

function ChatArea({ messages, isLoading }) {
    // If no messages are available, show welcome screen
    if (messages.length === 0) {
        return (
            <div className="welcome-container">
                <h1>Welcome to the fastest court in the world. Just follow the below steps to try my fast decision making ability.</h1>
                <div className="getting-started">
                    <div className="step">
                        <h3>1. Upload or Input</h3>
                        <p> Upload documents or input information to know your background like your age, health conditions, past record etc.</p>
                    </div>

                    <div className="step">
                        <h3>2. Explain your case</h3>
                        <p>You have to explain your case in detail if not uploaded. Remember "Do not miss the details!".</p>
                    </div>

                    <div className="step">
                        <h3>3. Get your prediction</h3>
                        <p>Now just sit back and wait for the judge to tell you his decision.</p>
                    </div>

                    <div className="step">
                        <h3>4. Check the Explanations</h3>
                        <p>Confidence score and bail conditions along with decision etc will be shown to you for your understanding.</p>
                    </div>
                </div>
            </div>
        );
    }

    // Display all messages in the conversation
    return (
        <div className="messages-container">
            {messages.map((message, index) => (
                <Message key={index} message={message} />
            ))}

            {/* Show loading indicator when waiting for AI response */}
            {isLoading && (
                <div className="typing-indicator">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                </div>
            )}
        </div>
    );

}

export default ChatArea;
