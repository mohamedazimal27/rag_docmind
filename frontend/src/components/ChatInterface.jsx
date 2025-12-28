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
        <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', height: '100vh', fontFamily: 'Arial, sans-serif' }}>
            {/* Left Sidebar: Data Source */}
            <div style={{ borderRight: '1px solid #ddd', padding: '20px', backgroundColor: '#f9f9f9', display: 'flex', flexDirection: 'column' }}>
                <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Data Sources</h2>

                {/* Upload */}
                <div style={{ marginBottom: '20px' }}>
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
                            display: 'block',
                            padding: '10px',
                            backgroundColor: isUploading ? '#ccc' : '#28a745',
                            color: 'white',
                            textAlign: 'center',
                            cursor: isUploading ? 'default' : 'pointer',
                            borderRadius: '4px'
                        }}
                    >
                        {isUploading ? 'Uploading...' : 'Upload Document'}
                    </label>
                    {error && <small style={{ color: 'red', marginTop: '5px', display: 'block' }}>{error}</small>}
                </div>

                {/* File List */}
                <div style={{ flex: 1, overflowY: 'auto' }}>
                    <h3 style={{ fontSize: '1rem', color: '#666' }}>Your Files ({files.length})</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {files.map((file, index) => (
                            <li key={index} style={{ padding: '8px 0', borderBottom: '1px solid #eee', fontSize: '0.9rem' }}>
                                📄 {file}
                            </li>
                        ))}
                        {files.length === 0 && <li style={{ color: '#999', fontStyle: 'italic' }}>No files uploaded.</li>}
                    </ul>
                </div>

                <button onClick={handleLogout} style={{ marginTop: 'auto', padding: '8px', border: '1px solid #ccc', background: 'white', cursor: 'pointer' }}>
                    Logout
                </button>
            </div>

            {/* Right: Chat Window */}
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                {/* Messages */}
                <div style={{ flex: 1, padding: '20px', overflowY: 'auto', backgroundColor: 'white' }}>
                    {chatHistory.map((msg, index) => (
                        <div key={index} style={{ marginBottom: '20px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                            <div style={{
                                display: 'inline-block',
                                padding: '10px 15px',
                                borderRadius: '15px',
                                backgroundColor: msg.isError ? '#ffebee' : (msg.role === 'user' ? '#007bff' : '#f1f0f0'),
                                color: msg.role === 'user' ? 'white' : 'black',
                                maxWidth: '70%',
                                textAlign: 'left'
                            }}>
                                <div>{msg.content}</div>
                                {/* Sources Display */}
                                {msg.sources && (
                                    <div style={{
                                        marginTop: '8px',
                                        borderTop: '1px solid rgba(0,0,0,0.1)',
                                        paddingTop: '5px',
                                        fontSize: '0.8rem',
                                        fontFamily: 'monospace',
                                        color: '#555',
                                        whiteSpace: 'pre-wrap'
                                    }}>
                                        <strong>Sources:</strong><br />
                                        {msg.sources}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div style={{ padding: '20px', borderTop: '1px solid #ddd', backgroundColor: 'white' }}>
                    <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Ask a question about your documents..."
                            style={{ flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
                        />
                        <button type="submit" disabled={!message.trim()} style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
