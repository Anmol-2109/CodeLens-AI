import React, { useState, useRef, useEffect } from 'react';
import { Send, StopCircle, RefreshCw, User, Bot, Loader2 } from 'lucide-react';
import { getAuthHeaders, API_URL } from '../api/auth';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
}

export default function ChatPanel({ repositoryId }: { repositoryId: number }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;
    
    const newMessage: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsStreaming(true);

    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '' }]);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_URL}/repositories/${repositoryId}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ query: input }),
        signal: abortControllerRef.current.signal
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.event === 'token') {
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMsgId ? { ...msg, content: msg.content + data.text } : msg
                ));
              } else if (data.event === 'error') {
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMsgId ? { ...msg, content: msg.content + "\n\n**Error**: " + data.text } : msg
                ));
              } else if (data.event === 'message_complete') {
                setIsStreaming(false);
              }
            } catch (e) {
              console.error("Error parsing SSE data", e);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Stream stopped manually');
      } else {
        console.error("Chat error:", err);
      }
    } finally {
      setIsStreaming(false);
    }
  };

  const stopStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] border border-gray-700 rounded-lg bg-gray-900 overflow-hidden m-4">
      <div className="bg-gray-800 p-4 border-b border-gray-700 font-semibold flex justify-between items-center">
        <span>Repository Chat</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <Bot className="w-12 h-12 mb-4 opacity-50" />
            <p>Ask a question about this repository's codebase.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex space-x-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'}`}>
                  {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-gray-300" />}
                </div>
                <div className={`p-4 rounded-lg shadow-md ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-200'}`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                handleSend();
              }
            }}
            placeholder="Ask about this codebase... (Ctrl+Enter to send)"
            className="w-full bg-gray-900 border border-gray-700 rounded-md py-3 pl-4 pr-12 text-white resize-none h-14 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          {isStreaming ? (
            <button onClick={stopStream} className="absolute right-3 top-3 text-red-500 hover:text-red-400 p-1">
              <StopCircle className="w-6 h-6" />
            </button>
          ) : (
            <button onClick={handleSend} disabled={!input.trim()} className="absolute right-3 top-3 text-blue-500 hover:text-blue-400 disabled:text-gray-600 p-1">
              <Send className="w-6 h-6" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
