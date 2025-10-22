import React, { useState, useRef, useEffect } from 'react';
import { Button, message as antdMessage, Spin, Image, Modal } from 'antd';
import { PictureOutlined, SendOutlined, SaveOutlined, DeleteOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css'; // 导入KaTeX样式
import axios from 'axios';
import './ChatWindow.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  image_url?: string;
}

function ChatWindow() {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 处理图片选择
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        antdMessage.error('请选择图片文件');
        return;
      }

      // 验证文件大小（限制10MB）
      if (file.size > 10 * 1024 * 1024) {
        antdMessage.error('图片大小不能超过10MB');
        return;
      }

      setUploadedImage(file);
      // 创建预览URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // 移除选中的图片
  const removeImage = () => {
    setUploadedImage(null);
    setPreviewImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 发送消息
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && !uploadedImage) return;
    if (isLoading) return;

    // 构建用户消息
    const userMessage: Message = {
      role: 'user',
      content: inputText || '请分析这张图片',
      image_url: previewImage || undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // 构建FormData
      const formData = new FormData();
      formData.append('message', userMessage.content);
      
      if (uploadedImage) {
        formData.append('image', uploadedImage);
      }

      // 添加历史记录（只发送纯文本部分）
      const historyForAPI = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      formData.append('history', JSON.stringify(historyForAPI));

      const response = await axios.post('http://127.0.0.1:8000/api/v1/chat', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const aiMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };

      setMessages(prev => [...prev, aiMessage]);

      // 清除图片
      removeImage();

    } catch (error) {
      console.error("Error fetching AI response:", error);
      const errorMessage: Message = {
        role: 'assistant',
        content: '❌ 抱歉，连接AI服务时出现错误。请检查后端服务是否正常运行。'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 保存聊天记录
  const saveChatHistory = async () => {
    if (messages.length === 0) {
      antdMessage.warning('没有聊天记录可保存');
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/v1/chat/save', {
        messages: messages
      });

      antdMessage.success(`聊天记录已保存: ${response.data.filename}`);
    } catch (error) {
      console.error("Error saving chat history:", error);
      antdMessage.error('保存聊天记录失败');
    }
  };

  // 清空聊天记录
  const clearChat = () => {
    Modal.confirm({
      title: '确认清空',
      content: '确定要清空所有聊天记录吗？此操作不可恢复。',
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        setMessages([]);
        antdMessage.success('聊天记录已清空');
      }
    });
  };

  return (
    <div className="chat-container">
      {/* 工具栏 */}
      <div className="chat-toolbar">
        <Button 
          icon={<SaveOutlined />} 
          onClick={saveChatHistory}
          disabled={messages.length === 0}
        >
          保存记录
        </Button>
        <Button 
          icon={<DeleteOutlined />} 
          onClick={clearChat}
          disabled={messages.length === 0}
          danger
        >
          清空对话
        </Button>
      </div>

      {/* 消息区域 */}
      <div className="messages-area">
        {messages.length === 0 && (
          <div className="empty-state">
            <h3>👋 你好！我是你的考研学习助手</h3>
            <p>我可以帮你解答数学、858信号与系统、政治、英语等科目的问题</p>
            <p>你可以直接输入文字，或上传题目图片向我提问</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {/* 如果有图片，显示图片 */}
              {msg.image_url && (
                <div className="message-image">
                  <Image
                    src={msg.image_url}
                    alt="上传的图片"
                    style={{ maxWidth: '300px', borderRadius: '8px' }}
                  />
                </div>
              )}
              
              {/* 消息内容 */}
              {msg.role === 'assistant' ? (
                <div className="markdown-content">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="text-content">{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <Spin size="small" /> 正在思考中...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="input-area">
        {/* 图片预览 */}
        {previewImage && (
          <div className="image-preview-container">
            <div className="image-preview">
              <img src={previewImage} alt="预览" />
              <Button
                type="text"
                danger
                size="small"
                onClick={removeImage}
                className="remove-image-btn"
              >
                ✕
              </Button>
            </div>
          </div>
        )}

        {/* 输入框和按钮 */}
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageSelect}
            accept="image/*"
            style={{ display: 'none' }}
          />
          
          <Button
            type="default"
            icon={<PictureOutlined />}
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="upload-btn"
          >
            图片
          </Button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="输入你的问题，或上传图片..."
            disabled={isLoading}
            className="text-input"
          />

          <Button
            type="primary"
            icon={<SendOutlined />}
            htmlType="submit"
            disabled={isLoading || (!inputText.trim() && !uploadedImage)}
            className="send-btn"
          >
            发送
          </Button>
        </form>
      </div>
    </div>
  );
}

export default ChatWindow;
