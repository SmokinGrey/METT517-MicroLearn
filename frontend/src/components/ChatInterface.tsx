import React, { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const styles: { [key: string]: React.CSSProperties } = {
  chatContainer: { marginTop: '2rem', border: '1px solid #444', borderRadius: '8px', padding: '1rem', backgroundColor: '#282c34' },
  title: { marginBottom: '1rem', color: '#61dafb', textAlign: 'left' },
  messageList: { height: '400px', overflowY: 'auto', marginBottom: '1rem', padding: '1rem', border: '1px solid #444', borderRadius: '4px', display: 'flex', flexDirection: 'column' },
  messageForm: { display: 'flex' },
  input: { flexGrow: 1, padding: '0.75rem', border: '1px solid #555', borderRadius: '4px', backgroundColor: '#333', color: 'white', marginRight: '0.5rem' },
  button: { padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', backgroundColor: '#61dafb', color: '#20232a', cursor: 'pointer', fontWeight: 'bold' },
  userMessage: { alignSelf: 'flex-end', backgroundColor: '#007bff', color: 'white', padding: '0.5rem 1rem', borderRadius: '15px 15px 0 15px', marginBottom: '0.5rem', maxWidth: '70%' },
  aiMessage: { alignSelf: 'flex-start', backgroundColor: '#444', color: 'white', padding: '0.5rem 1rem', borderRadius: '15px 15px 15px 0', marginBottom: '0.5rem', maxWidth: '70%' },
  sourcesContainer: { marginTop: '1.5rem', borderTop: '1px solid #555', paddingTop: '1rem' },
  sourceItem: { backgroundColor: '#3a3f47', border: '1px solid #555', borderRadius: '4px', padding: '0.75rem', marginBottom: '0.5rem', fontSize: '0.85em', whiteSpace: 'pre-wrap', lineHeight: '1.5', textAlign: 'left' },
};

interface Message { sender: 'user' | 'ai'; text: string; }
interface SourceDocument { page_content: string; metadata: any; }
interface ChatInterfaceProps { materialId: number; }

const ChatInterface: React.FC<ChatInterfaceProps> = ({ materialId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const token = useAuthStore((state) => state.token);
  const messageListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage, { sender: 'ai', text: '' }]);
    setSources([]); // 이전 답변의 근거 초기화
    
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/materials/${materialId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ question: currentInput }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred.');
      }
      if (!response.body) throw new Error("Response body is null.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;
          try {
            const parsed = JSON.parse(line);
            switch (parsed.type) {
              case 'token':
                setMessages(prev => {
                  const last = prev[prev.length - 1];
                  const updated = { ...last, text: last.text + parsed.data };
                  return [...prev.slice(0, -1), updated];
                });
                break;
              case 'source':
                setSources(prev => [...prev, parsed.data]);
                break;
              case 'error':
                setError(parsed.data);
                break;
            }
          } catch (e) {
            console.error("Failed to parse stream line:", line, e);
          }
        }
      }
    } catch (err: any) {
      setError(err.message);
      setMessages(prev => prev.slice(0, -2));
      setInput(currentInput);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.chatContainer}>
      <h3 style={styles.title}>자료와 대화하기</h3>
      <div style={styles.messageList} ref={messageListRef}>
        {messages.map((msg, index) => (
          <div key={index} style={msg.sender === 'user' ? styles.userMessage : styles.aiMessage}>
            {msg.text.split('\n').map((line, i) => <div key={i}>{line}</div>)}
          </div>
        ))}
        {isLoading && messages[messages.length -1]?.text === '' && <div style={{alignSelf: 'flex-start'}}><LoadingSpinner /></div>}
      </div>
      <form onSubmit={handleSubmit} style={styles.messageForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="질문을 입력하세요..."
          style={styles.input}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading} style={styles.button}>
          {isLoading ? '전송중...' : '전송'}
        </button>
      </form>
      {error && <ErrorMessage message={error} />}

      {sources.length > 0 && (
        <div style={styles.sourcesContainer}>
          <h4 style={{textAlign: 'left', marginBottom: '0.5rem'}}>답변 근거</h4>
          {sources.map((source, index) => (
            <div key={index} style={styles.sourceItem}>
              <p>{source.page_content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatInterface;