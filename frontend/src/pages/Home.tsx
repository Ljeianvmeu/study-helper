import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Button, Modal, Form, Input, Upload, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  BarChartOutlined,
  EditOutlined,
  CalendarOutlined,
  RobotOutlined,
  SettingOutlined,
  FileOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { systemAPI } from '../services/api';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [apiConfigured, setApiConfigured] = useState(false);
  const [dailyTasksExists, setDailyTasksExists] = useState(false);
  const [apiModalVisible, setApiModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  // 加载系统状态
  useEffect(() => {
    loadSystemStatus();
  }, []);

  const loadSystemStatus = async () => {
    try {
      const response = await systemAPI.getStatus();
      setApiConfigured(response.data.api_configured);
      setDailyTasksExists(response.data.daily_tasks_exists);
    } catch (error) {
      console.error('加载系统状态失败:', error);
    }
  };

  // 处理API密钥配置
  const handleApiConfig = () => {
    if (apiConfigured) {
      message.info('API密钥已配置');
      return;
    }
    setApiModalVisible(true);
  };

  const handleApiSubmit = async (values: any) => {
    setLoading(true);
    try {
      await systemAPI.saveAPIKeys({
        modelscope_api_key: values.modelscope_api_key,
        dashscope_api_key: values.dashscope_api_key,
      });
      message.success('API密钥保存成功');
      setApiModalVisible(false);
      form.resetFields();
      loadSystemStatus();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'API密钥保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理每日任务文件上传
  const handleDailyTasksUpload = async (file: File) => {
    if (dailyTasksExists) {
      message.info('daily_tasks.xlsx 文件已存在');
      return false;
    }

    try {
      await systemAPI.uploadDailyTasks(file);
      message.success('daily_tasks.xlsx 上传成功');
      loadSystemStatus();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '文件上传失败');
    }
    return false; // 阻止自动上传
  };

  const modules = [
    {
      title: '分数统计器',
      description: '记录和分析各科目考试分数，生成趋势图表',
      icon: <BarChartOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      path: '/scores',
      color: '#e6f7ff',
    },
    {
      title: '英语作文优化',
      description: '上传作文图片，获取AI智能批改和优化建议',
      icon: <EditOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      path: '/essays',
      color: '#f6ffed',
    },
    {
      title: '每日任务',
      description: '管理每日学习任务，记录学习时长，统计完成率',
      icon: <CalendarOutlined style={{ fontSize: 48, color: '#faad14' }} />,
      path: '/tasks',
      color: '#fffbe6',
    },
    {
      title: '通用AI助手',
      description: '智能问答助手，解答学习中的各种问题',
      icon: <RobotOutlined style={{ fontSize: 48, color: '#722ed1' }} />,
      path: '/ai',
      color: '#f9f0ff',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 36, marginBottom: 16 }}>Study Helper</h1>
        <p style={{ fontSize: 18, color: '#666' }}>
          你的个人学习助手 - 让学习更高效
        </p>
      </div>

      {/* 配置区域 */}
      <div style={{ 
        marginBottom: 32, 
        padding: '16px 24px',
        background: '#f5f5f5',
        borderRadius: 8,
        display: 'flex',
        justifyContent: 'center',
        gap: 16,
        flexWrap: 'wrap'
      }}>
        <Button
          type={apiConfigured ? 'default' : 'primary'}
          icon={<SettingOutlined />}
          onClick={handleApiConfig}
          disabled={apiConfigured}
          style={{ minWidth: 180 }}
        >
          {apiConfigured ? 'API密钥已配置' : '配置API密钥'}
        </Button>

        <Upload
          beforeUpload={handleDailyTasksUpload}
          showUploadList={false}
          accept=".xlsx"
          disabled={dailyTasksExists}
        >
          <Button
            type={dailyTasksExists ? 'default' : 'primary'}
            icon={dailyTasksExists ? <FileOutlined /> : <UploadOutlined />}
            disabled={dailyTasksExists}
            style={{ minWidth: 180 }}
          >
            {dailyTasksExists ? '任务文件已上传' : '上传任务文件'}
          </Button>
        </Upload>
      </div>

      <Row gutter={[24, 24]}>
        {modules.map((module, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              hoverable
              className="module-card"
              style={{
                textAlign: 'center',
                backgroundColor: module.color,
                height: '100%',
                borderRadius: 12,
              }}
              onClick={() => navigate(module.path)}
            >
              <div style={{ marginBottom: 16 }}>{module.icon}</div>
              <h3 style={{ fontSize: 20, marginBottom: 12 }}>{module.title}</h3>
              <p style={{ color: '#666', fontSize: 14 }}>{module.description}</p>
            </Card>
          </Col>
        ))}
      </Row>

      {/* API配置弹窗 */}
      <Modal
        title="配置API密钥"
        open={apiModalVisible}
        onCancel={() => {
          setApiModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleApiSubmit}
        >
          <Form.Item
            label="ModelScope API Key"
            name="modelscope_api_key"
            rules={[{ required: true, message: '请输入ModelScope API Key' }]}
            extra="用于英语作文分析功能"
          >
            <Input.Password placeholder="请输入ModelScope API Key" />
          </Form.Item>

          <Form.Item
            label="DashScope API Key"
            name="dashscope_api_key"
            rules={[{ required: true, message: '请输入DashScope API Key' }]}
            extra="用于通用AI助手功能"
          >
            <Input.Password placeholder="请输入DashScope API Key" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Home;

