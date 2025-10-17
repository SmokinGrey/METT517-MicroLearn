import React, { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

// CSS를 위한 간단한 스타일 객체
const styles: { [key: string]: React.CSSProperties } = {
  chatContainer: {
    marginTop: '2rem',
    border: '1px solid #444',
    borderRadius: '8px',
    padding: '1rem',
    backgroundColor: '#282c34'
  },
  title: {
    marginBottom: '1rem',
    color: '#61dafb',
    textAlign: 'left'
  },
  messageList: {
    height: '400px',
    overflowY: 'auto',
    marginBottom: '1rem',
    padding: '1rem',
    border: '1px solid #444',
    borderRadius: '4px',
    display: 'flex',
    flexDirection: 'column',
  },
  messageForm: {
    display: 'flex',
  },
  input: {
    flexGrow: 1,
    padding: '0.75rem',
    border: '1px solid #555',
    borderRadius: '4px',
    backgroundColor: '#333',
    color: 'white',
    marginRight: '0.5rem'
  },
  button: {
    padding: '0.75rem 1.5rem',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#61dafb',
    color: '#20232a',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007bff',
    color: 'white',
    padding: '0.5rem 1rem',
    borderRadius: '15px 15px 0 15px',
    marginBottom: '0.5rem',
    maxWidth: '70%'
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#444',
    color: 'white',
    padding: '0.5rem 1rem',
    borderRadius: '15px 15px 15px 0',
    marginBottom: '0.5rem',
    maxWidth: '70%'
  }
};

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

interface ChatInterfaceProps {
  materialId: number;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ materialId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const token = useAuthStore((state) => state.token);
  const messageListRef = useRef<HTMLDivElement>(null);

  // 메시지 목록이 업데이트될 때마다 맨 아래로 스크롤
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/materials/${materialId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ question: currentInput }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '답변을 가져오는 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      const aiMessage: Message = { sender: 'ai', text: data.answer };
      setMessages((prev) => [...prev, aiMessage]);

    } catch (err: any) {
      setError(err.message);
      // 에러 발생 시 사용자 메시지 다시 입력창에 넣어주기
      setInput(currentInput);
      setMessages(prev => prev.slice(0, -1)); // 낙관적 업데이트 롤백
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
        {isLoading && <div style={{alignSelf: 'flex-start'}}><LoadingSpinner /></div>}
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
    </div>
  );
};

export default ChatInterface;
