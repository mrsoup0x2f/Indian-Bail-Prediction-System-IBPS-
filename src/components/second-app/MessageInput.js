// src/components/MessageInput.js - Input field for sending messages
import React, { useState } from 'react';
import './MessageInput.css';
import pdfToText from 'react-pdftotext';

function MessageInput({ onSendMessage, isLoading }) {
    const [message, setMessage] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContentUsed, setFileContentUsed] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            // const completeMessage = fileContentUsed
            //     ? `${message} [Attached: ${fileContentUsed}]`
            //     : message;
            onSendMessage(message, fileContentUsed);
            setMessage(''); // Clear input after sending
            setSelectedFile(null); // Clear selected file 
            setFileContentUsed(''); // Clear file content used
        }
    };

    // Handle input resize as user types (auto-expanding textarea)
    const handleInput = (e) => {
        const textarea = e.target;
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
        setMessage(textarea.value);
    };

    // Handle keyboard shortcuts (Enter to send, Shift+Enter for new line)
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        setSelectedFile(file);
        try {
            let fileContent = '';
            if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
                fileContent = await extractPdfContent(file);
            } else if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
                fileContent = await extractTxtContent(file);
            } else {
                alert('Only PDF and TXT files are supported');
                e.target.value = null;
                return;
            }
            // const fileContentUsed = fileContent.split(/\s+/).slice(0, 4500).join(' ');
            setFileContentUsed(fileContent.split(/\s+/).slice(0, 4500).join(' '));
            
        } catch (error) {
            console.error(`Error reading file ${file.name}:`, error);
            alert(`Error reading file ${file.name}.`);
        }
        e.target.value = null;
    };

    const extractPdfContent = async (file) => {
        try {
            const text = await pdfToText(file);
            return text;
        } catch (error) {
            console.error('Failed to extract text from PDF:', error);
            throw new Error('Failed to read PDF content');
        }
    };

    const extractTxtContent = (file) => {
        return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (event) => {
            resolve(event.target.result);
        };
        
        reader.onerror = (error) => {
            console.error('Error reading text file:', error);
            reject(new Error('Failed to read text file'));
        };
        
        reader.readAsText(file);
        });
    };

    return (
        <div className="message-input-container">
            <form onSubmit={handleSubmit}>
                <textarea
                    value={message}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder="Talk to us..."
                    disabled={isLoading}
                    rows={1}
                />
                <button
                    type="button"
                    className="file-upload-button"
                    disabled={isLoading}
                    tabIndex={-1}
                    style={{ background: 'none', border: 'none', cursor: isLoading ? 'not-allowed' : 'pointer', padding: 0, marginRight: '8px' }}
                    onClick={() => document.getElementById('file-upload-input').click()}
                    aria-label="Attach file"
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M16.5 6.5V17a4.5 4.5 0 01-9 0V7a3.5 3.5 0 017 0v10a2.5 2.5 0 01-5 0V7.5" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <input
                        id="file-upload-input"
                        type="file"
                        accept='.pdf, .txt, application/pdf, text/plain'
                        style={{ display: 'none' }}
                        disabled={isLoading}
                        onChange={handleFileChange}
                    />
                </button>
                <button
                    type="submit"
                    className="send-button"
                    disabled={!message.trim() || isLoading}
                >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                    </svg>
                </button>
            </form>
            {selectedFile && (
                <div className="selected-file-info">
                    File selected: {selectedFile.name}
                </div>
            )}
        </div>
    );
}

export default MessageInput;
