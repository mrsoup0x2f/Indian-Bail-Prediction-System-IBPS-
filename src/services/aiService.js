// src/services/aiService.js - Service for interacting with AI models
import { InferenceClient } from '@huggingface/inference';
import { createMemoryBuffer, summarizeIfNeeded } from './memoryService';

// Maximum number of messages to include in context
const MAX_CONTEXT_MESSAGES = 20;
// Create the client using your HF token from .env
const hfClient = new InferenceClient(process.env.REACT_APP_HF_API_KEY);

//new code
async function chatWithLocalModel(formattedMessages) {
    return new Promise((resolve, reject) => {
        let confidenceScore = null;
        try {
            // Create WebSocket connection
            const socket = new WebSocket('ws://localhost:8000/chat');

            // Connection opened
            socket.addEventListener('open', (event) => {
                console.log('WebSocket connection established');
                // Send the messages to the server
                try {
                    const testJSON = JSON.stringify(formattedMessages);
                    console.log('Sending messages to server:', testJSON);
                } catch (error) {
                    console.error('Error stringifying messages:', error);
                    reject(new Error(`Error stringifying messages: ${error.message}`));
                }
                socket.send(JSON.stringify(formattedMessages));
            });

            // Listen for messages from the server
            let accumulatedResponse = '';
            socket.addEventListener('message', (event) => {
                let data;
                console.log('Message from server:', data);
                try {
                    data = JSON.parse(event.data);
                } catch {
                    data = event.data;
                }

                if (typeof data === "object" && data.type === "confidence_score") {
                    confidenceScore = data.value;
                    console.log("Received confidence score:", confidenceScore);
                } else if (data === "__end__") {
                    console.log("Final response:", accumulatedResponse);
                    resolve({
                        response: accumulatedResponse,
                        confidenceScore: confidenceScore
                    });
                    socket.close(1000, "Normal closure");
                } else {
                    accumulatedResponse += data;
                }

                // if (chunk === "__end__"){
                //     console.log("final response:", accumulatedResponse);
                //     resolve(accumulatedResponse);
                //     socket.close(1000, "Normal closure");
                // } else {
                //     accumulatedResponse += chunk;
                // }
            });

            // Handle errors
            socket.addEventListener('error', (error) => {
                console.error('WebSocket error:', error);
                reject(new Error(`WebSocket error: ${error.message}`));
            });

            // Handle connection close
            socket.addEventListener('close', (event) => {
                if (!event.wasClean) {
                    reject(new Error(`WebSocket connection closed unexpectedly: code ${event.code}`));
                }
            });
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
            reject(new Error(`WebSocket setup error: ${error.message}`));
        }
    });
}


// This function processes a message with the selected AI model
export async function processMessageWithAI(message, history, model) {
    // First, prepare the conversation history
    let conversationHistory = createMemoryBuffer(history, MAX_CONTEXT_MESSAGES);

    // If history is long, summarize older messages to prevent context overflow
    if (history.length > MAX_CONTEXT_MESSAGES) {
        const olderMessages = history.slice(0, history.length - MAX_CONTEXT_MESSAGES);
        const summary = await summarizeIfNeeded(olderMessages);

        // Add summary as system message at the beginning of context
        if (summary) {
            conversationHistory.unshift({
                role: 'system',
                content: `Previous conversation summary: ${summary}`
            });
        }
    }

    // Format messages for the API
    const formattedMessages = [
        // Optionally add a system prompt
        {
            role: 'system',
            content: 'Pose as a legal assistant whose name is IBPS and specializes in bail decisions (granted/denied). We need the following information: Type of bail application (regular/anticipatory/bail-cancellation), Statutes imposed on accused, Details of the incident, Past Criminal Record, Age and Health details, Date of arrest in case of Regular Bail Application. If any of these details are missing, politely ask the user to provide the missing information. Once you have the first three details, proceed to predict whether the bail application will be granted or denied, along with bail conditions and reasoning and for your prediction. Always give short, clear and concise response.'
        },
        ...conversationHistory.map(msg => ({
            role: msg.role,
            content: msg.content
        })),
        {
            role: 'user',
            content: message
        }
    ];

    // try {
    //     // Call the Hugging Face inference API using the SDK
    //     const chatCompletion = await hfClient.chatCompletion({
    //         provider: "hf-inference",
    //         model: "microsoft/phi-4",
    //         messages: formattedMessages,
    //         // You can add parameters if needed:
    //         // max_tokens, temperature, etc.

    //         temperature: 0.2
    //     });
    //     // Check if the response is valid
    //     if (!chatCompletion || !chatCompletion.choices || chatCompletion.choices.length === 0) {
    //         throw new Error('Invalid response from AI service');
    //     }
    //     console.log('AI response:', chatCompletion.choices);
    //     console.log('User sending Info:', formattedMessages);
    //     // Return the assistant's reply
    //     return chatCompletion.choices[0].message.content;
    // } catch (error) {
    //     console.error('Error calling Hugging Face API:', error);
    //     throw new Error(`AI service error: ${error.message}`);
    // }

    // Call the local model via WebSocket
    try {
        // Use WebSocket connection instead of Hugging Face API
        const { response, confidenceScore } = await chatWithLocalModel(formattedMessages);
        console.log('AI response:', response);
        console.log('User sending Info:', formattedMessages);

        // Return the assistant's reply
        return { response, confidenceScore };
    } catch (error) {
        console.error('Error communicating with local model:', error);
        throw new Error(`AI service error: ${error.message}`);
    }
}

