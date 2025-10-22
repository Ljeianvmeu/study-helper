import React from 'react';
import { Card } from 'antd';
import ChatWindow from '../components/ChatWindow';

const AIPage: React.FC = () => {
  return (
    <div style={{ 
      padding: 24, 
      height: 'calc(100vh - 64px)', // 减去顶部导航栏高度
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Card 
        title="通用AI助手"
        style={{ 
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        bodyStyle={{
          flex: 1,
          padding: 0,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        <ChatWindow />
      </Card>
    </div>
  );
};

export default AIPage;

