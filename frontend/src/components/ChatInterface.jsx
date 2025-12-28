import React, { useState, useEffect, useRef } from 'react';
import api from '../api';

const ChatInterface = () => {
    const [files, setFiles] = useState([]);
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState('');
    const bottomRef = useRef(null);

    useEffect(() => {
        fetchFiles();
    }, []);

    useEffect(() => {
        // Scroll to bottom on new message
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory])

    const fetchFiles = async () => {
        try {
            const response = await api.get('/files');
            setFiles(response.data.files);
        } catch (err) {
            console.error("Failed to fetch files", err);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Limits check could be here too, but backend enforces it.

        setIsUploading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            await api.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setIsUploading(false);
            fetchFiles(); // Refresh list
        } catch (err) {
            console.error("Upload failed", err);
            setError(err.response?.data?.detail || 'Upload failed');
            setIsUploading(false);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        const userMsg = { role: 'user', content: message };
        setChatHistory(prev => [...prev, userMsg]);
        setMessage('');

        try {
            const response = await api.post('/chat', { question: userMsg.content });
            const rawAnswer = response.data.answer;

            // Critical Parsing Logic: Split Answer and Sources
            const parts = rawAnswer.split('Sources:');
            const answerText = parts[0].replace('Answer:', '').trim();
            const sourcesText = parts.length > 1 ? parts[1].trim() : '';

            const botMsg = {
                role: 'assistant',
                content: answerText,
                sources: sourcesText
            };

            setChatHistory(prev => [...prev, botMsg]);
        } catch (err) {
            console.error("Chat failed", err);
            const botMsg = {
                role: 'assistant',
                content: "Sorry, I had trouble connecting to the server.",
                isError: true
            };
            setChatHistory(prev => [...prev, botMsg]);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(250px, 300px) 1fr', height: '100vh', width: '100vw', fontFamily: 'Inter, sans-serif', backgroundColor: 'var(--bg-primary)' }}>
            {/* Left Sidebar: Data Source */}
            <div style={{
                borderRight: '1px solid var(--border-color)',
                padding: '24px',
                backgroundColor: 'var(--bg-secondary)',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '2px 0 5px rgba(0,0,0,0.2)'
            }}>
                <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', fontWeight: '600', color: 'var(--text-primary)' }}>Data Sources</h2>

                {/* Upload */}
                <div style={{ marginBottom: '24px' }}>
                    <input
                        type="file"
                        id="file-upload"
                        style={{ display: 'none' }}
                        onChange={handleUpload}
                        disabled={isUploading}
                    />
                    <label
                        htmlFor="file-upload"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '12px',
                            backgroundColor: isUploading ? 'var(--bg-tertiary)' : 'var(--accent-color)',
                            color: 'white',
                            textAlign: 'center',
                            cursor: isUploading ? 'default' : 'pointer',
                            borderRadius: '8px',
                            fontWeight: '500',
                            transition: 'background-color 0.2s',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}
                    >
                        {isUploading ? 'Uploading...' : '+ Upload Document'}
                    </label>
                    {error && <small style={{ color: 'var(--error-color)', marginTop: '8px', display: 'block' }}>{error}</small>}
                </div>

                {/* File List */}
                <div style={{ flex: 1, overflowY: 'auto' }}>
                    <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                        Your Files ({files.length})
                    </h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {files.map((file, index) => (
                            <li key={index} style={{
                                padding: '10px 12px',
                                borderBottom: '1px solid var(--border-color)',
                                fontSize: '0.95rem',
                                color: 'var(--text-primary)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}>
                                <span style={{ opacity: 0.7 }}>📄</span> {file}
                            </li>
                        ))}
                        {files.length === 0 && <li style={{ color: 'var(--text-secondary)', fontStyle: 'italic', padding: '10px 0' }}>No files uploaded.</li>}
                    </ul>
                </div>

                <button onClick={handleLogout} style={{ marginTop: '20px', padding: '10px', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer', borderRadius: '6px' }}>
                    Logout
                </button>
            </div>

            {/* Right: Chat Window */}
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: 'var(--bg-primary)' }}>
                {/* Header */}
                <div style={{
                    padding: '16px 24px',
                    borderBottom: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                    zIndex: 10
                }}>
                    <h1 style={{
                        fontSize: '1.2rem',
                        fontWeight: '700',
                        margin: 0,
                        color: 'var(--text-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                    }}>
                        <span style={{ fontSize: '1.5rem' }}>🧠</span> DocuMind Pro
                    </h1>
                </div>

                {/* Messages */}
                <div style={{ flex: 1, padding: '30px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {chatHistory.map((msg, index) => (
                        <div key={index} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '75%' }}>
                            <div style={{
                                padding: '16px 20px',
                                borderRadius: '12px',
                                borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
                                borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                                backgroundColor: msg.isError ? '#3e1b1b' : (msg.role === 'user' ? 'var(--msg-user-bg)' : 'var(--msg-bot-bg)'),
                                color: msg.isError ? 'var(--error-color)' : (msg.role === 'user' ? 'var(--msg-user-text)' : 'var(--msg-bot-text)'),
                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                                lineHeight: '1.6'
                            }}>
                                <div>{msg.content}</div>
                                {/* Sources Display */}
                                {msg.sources && (
                                    <div style={{
                                        marginTop: '12px',
                                        borderTop: '1px solid rgba(255,255,255,0.1)',
                                        paddingTop: '8px',
                                        fontSize: '0.85rem',
                                        fontFamily: 'monospace',
                                        color: 'var(--text-secondary)',
                                        whiteSpace: 'pre-wrap'
                                    }}>
                                        <strong style={{ color: 'var(--accent-color)' }}>Sources:</strong><br />
                                        {msg.sources}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div style={{ padding: '24px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
                    <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '12px', maxWidth: '900px', margin: '0 auto' }}>
                        <input
                            type="text"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Ask a question about your documents..."
                            style={{
                                flex: 1,
                                padding: '14px',
                                border: '1px solid var(--border-color)',
                                borderRadius: '8px',
                                backgroundColor: 'var(--bg-tertiary)',
                                color: 'var(--text-primary)',
                                fontSize: '1rem'
                            }}
                        />
                        <button type="submit" disabled={!message.trim()} style={{
                            padding: '14px 28px',
                            backgroundColor: 'var(--accent-color)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            fontSize: '1rem'
                        }}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
