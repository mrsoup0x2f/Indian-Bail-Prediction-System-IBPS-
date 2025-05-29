// src/services/memoryService.js - Service for managing conversation memory

// Create a buffer of recent messages for context
export function createMemoryBuffer(messages, maxSize = 10) {
  // If messages are fewer than max size, return all messages
  if (messages.length <= maxSize) {
    return [...messages];
  }

  // Otherwise, return the most recent messages up to maxSize
  return messages.slice(messages.length - maxSize);
}



// Summarize older messages to maintain context while reducing token count
export async function summarizeIfNeeded(messages) {
  // In a real implementation, you would call an LLM to summarize
  // For example, using OpenAI:
  /*
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.REACT_APP_OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'Summarize the following conversation concisely, preserving key information:'
        },
        ...messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      ],
      temperature: 0.3,
      max_tokens: 150
    })
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
  */

  // For this example, we'll create a simple summary manually
  if (messages.length === 0) return null;

  const topicWords = extractKeyTopics(messages);
  return `Previous conversation covered topics: ${topicWords.join(', ')}`;
}

// Helper function to extract key topics from messages
function extractKeyTopics(messages) {
  // Simple implementation - extract common words
  const allText = messages.map(msg => msg.content).join(' ').toLowerCase();
  const words = allText.split(/\W+/);

  // Filter out common stop words
  const stopWords = new Set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
    'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
    'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
    'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
    'don', 'should', 'now'
  ]);

  // Count word frequency
  const wordCount = {};
  words.forEach(word => {
    if (word.length > 3 && !stopWords.has(word)) {
      wordCount[word] = (wordCount[word] || 0) + 1;
    }
  });

  // Get top 5 words
  return Object.entries(wordCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(entry => entry[0]);
}
