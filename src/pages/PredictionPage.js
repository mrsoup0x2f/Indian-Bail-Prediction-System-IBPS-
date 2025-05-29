// src/App.js - Main application component
import React, { useState, useEffect, useRef } from 'react';
import './PredictionPage.css';
import Sidebar from '../components/second-app/Sidebar';
import ChatArea from '../components/second-app/ChatArea';
import MessageInput from '../components/second-app/MessageInput';
import ConfidenceBar from '../components/second-app/ConfidenceBar';
import { processMessageWithAI } from '../services/aiService';


function PredictionPage() {
    // State for managing messages in the current conversation
    const [messages, setMessages] = useState([]);
    // State for managing conversation history (for sidebar display)
    const [conversations, setConversations] = useState([]);
    // State to track confidence score from AI service
    const [confidenceScore, setConfidenceScore] = useState(0);
    // State to track current model selection
    const [selectedModel, setSelectedModel] = useState('gpt-4');
    // State to track loading state when waiting for AI response
    const [isLoading, setIsLoading] = useState(false);
    // Reference to chat container for auto-scrolling
    const chatContainerRef = useRef(null);


    // Effect to scroll to bottom when messages change
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    // Handle sending a new message
    const handleSendMessage = async (content, fileContent = '') => {
        if (!content.trim()) return;

        const completeMessage = fileContent
            ? `${content} [Attached file content: ${fileContent}]`
            : content;
        // Add user message to the conversation
        const userMessage = {
            role: 'user',
            content,
            timestamp: new Date()
        };
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setIsLoading(true);

        try {
            // Process the message with the AI service, including conversation history for context
            const aiResponse = await processMessageWithAI(
                completeMessage,
                messages,
                selectedModel
            );

            // Add AI response to the conversation
            const aiMessage = {
                role: 'assistant',
                content: aiResponse.response,
                timestamp: new Date()
            };
            setMessages(prevMessages => [...prevMessages, aiMessage]);
            // Update confidence score
            setConfidenceScore(Number((aiResponse.confidenceScore * 100).toFixed(2)));

            // Update conversation history if this is a new conversation
            if (messages.length === 0) {
                const newConversation = {
                    id: Date.now().toString(),
                    title: content.substring(0, 30) + (content.length > 30 ? '...' : ''),
                    messages: [userMessage, aiMessage]
                };
                setConversations(prev => [newConversation, ...prev]);
            }
        } catch (error) {
            console.error('Error getting AI response:', error);
            // Add error message to the conversation
            setMessages(prevMessages => [
                ...prevMessages,
                { role: 'error', content: 'Sorry, there was an error processing your request.', timestamp: new Date() }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    // Handle starting a new conversation
    const handleNewChat = () => {
        setMessages([]);
    };

    // Handle model selection change
    const handleModelChange = (model) => {
        setSelectedModel(model);
    };

    return (
        <div className="app-container" style={{
            backgroundImage: 'url("/bg.jpg")',
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
            minHeight: '100vh'
        }}>

            <Sidebar
                conversations={conversations}
                onNewChat={handleNewChat}
                selectedModel={selectedModel}
                onModelChange={handleModelChange}
            />

            {confidenceScore > 0 && (
                <div className="confidence-score-container">
                    <ConfidenceBar
                        confidenceScore={confidenceScore}
                    // fillColor={confidenceScore > 70 ? "#4CAF50" : confidenceScore > 40 ? "#FFC107" : "#F44336"}
                    />
                </div>
            )}

            <main className="chat-container">
                <div className="chat-area" ref={chatContainerRef}>
                    <ChatArea messages={messages} isLoading={isLoading} />
                </div>
                <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
            </main>
        </div>
    );
}

export default PredictionPage;
