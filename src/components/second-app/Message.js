// // src/components/Message.js - Individual message component
// import React from 'react';
// import './Message.css';
// import { formatTimestamp } from '../utils/dateUtils';

// function Message({ message }) {
//     // Determine CSS class based on message role
//     const messageClass = `message ${message.role}-message`;

//     // Format code blocks within messages
//     const formatContent = (content) => {
//         // Simple regex to identify code blocks (text between triple backticks)
//         const codeBlockRegex = /``````/g;

//         // Split content by code blocks
//         const parts = content.split(codeBlockRegex);

//         if (parts.length === 1) {
//             // No code blocks found, return regular text
//             return <p>{content}</p>;
//         }

//         // Return formatted content with code blocks
//         return parts.map((part, index) => {
//             // Even indices are regular text, odd indices are code
//             if (index % 2 === 0) {
//                 return part ? <p key={index}>{part}</p> : null;
//             } else {
//                 return (
//                     <pre key={index} className="code-block">
//                         <code>{part}</code>
//                     </pre>
//                 );
//             }
//         });
//     };

//     return (
//         <div className={messageClass}>
//             <div className="message-avatar">
//                 {message.role === 'user' ? 'U' : 'AI'}
//             </div>
//             <div className="message-content">
//                 {formatContent(message.content)}
//                 <div className="message-timestamp">
//                     {formatTimestamp(message.timestamp)}
//                 </div>
//             </div>
//         </div>
//     );
// }

// export default Message;




// src/components/Message.js - Individual message component
import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Message.css';
import { formatTimestamp } from '../../utils/dateUtils';

function Message({ message }) {
    // Determine CSS class based on message role
    const messageClass = `message ${message.role}-message`;

    return (
        <div className={messageClass}>
            <div className="message-avatar">
                {message.role === 'user' ? 'U' : 'IBPS'}
            </div>
            <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
                <div className="message-timestamp">
                    {formatTimestamp(message.timestamp)}
                </div>
            </div>
        </div>
    );
}

export default Message;
