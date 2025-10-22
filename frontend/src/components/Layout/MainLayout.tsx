import React from 'react';
import { Layout, Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  BarChartOutlined,
  EditOutlined,
  CalendarOutlined,
  RobotOutlined,
} from '@ant-design/icons';

const { Header, Content, Footer } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/scores',
      icon: <BarChartOutlined />,
      label: '分数统计',
    },
    {
      key: '/essays',
      icon: <EditOutlined />,
      label: '作文优化',
    },
    {
      key: '/tasks',
      icon: <CalendarOutlined />,
      label: '每日任务',
    },
    {
      key: '/ai',
      icon: <RobotOutlined />,
      label: 'AI助手',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{
            color: 'white',
            fontSize: 20,
            fontWeight: 'bold',
            marginRight: 48,
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          Study Helper
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content style={{ padding: '0 50px', marginTop: 24 }}>
        <div style={{ background: '#fff', minHeight: 'calc(100vh - 134px)' }}>
          <Outlet />
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Study Helper ©2024 - 你的学习助手
      </Footer>
    </Layout>
  );
};

export default MainLayout;

