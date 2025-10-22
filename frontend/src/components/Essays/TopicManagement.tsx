import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Upload, message, Image, Popconfirm } from 'antd';
import { UploadOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { essaysAPI } from '../../services/api';
import type { UploadFile } from 'antd/es/upload/interface';

const { Option } = Select;
const { TextArea } = Input;

const TopicManagement: React.FC = () => {
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    setLoading(true);
    try {
      // 获取所有年份
      const { data } = await essaysAPI.getTopics();
      const years = data.years;
      const essayTypes = data.essay_types || ['小作文', '大作文'];

      // 获取每个年份+类型的详细信息
      const topicsData = [];
      for (const year of years) {
        for (const type of essayTypes) {
          try {
            const response = await essaysAPI.getTopicDetail(year, type);
            topicsData.push({
              year,
              essayType: type,
              ...response.data
            });
          } catch (error) {
            // 某些年份+类型组合可能不存在
            console.log(`未找到 ${year} ${type}`);
          }
        }
      }
      setTopics(topicsData);
    } catch (error) {
      message.error('加载题目列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    form.resetFields();
    setFileList([]);
    setModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请上传题目图片');
      return;
    }

    const file = fileList[0].originFileObj || fileList[0];
    if (!file) {
      message.error('文件对象无效');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('year', values.year.toString());
      formData.append('essay_type', values.essay_type);
      formData.append('topic_image', file as Blob);
      formData.append('reference', values.reference);

      await essaysAPI.addTopic(formData);
      message.success('题目添加成功');
      setModalVisible(false);
      loadTopics();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (year: number, essayType: string) => {
    setLoading(true);
    try {
      await essaysAPI.deleteTopic(year, essayType);
      message.success('删除成功');
      loadTopics();
    } catch (error) {
      message.error('删除失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewImage = async (year: number, essayType: string) => {
    const imageUrl = `http://localhost:8000/api/v1/essays/topics/image/${year}/${essayType}`;
    setPreviewImage(imageUrl);
    setPreviewOpen(true);
  };

  const uploadProps = {
    onRemove: () => {
      setFileList([]);
    },
    beforeUpload: (file: File) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('只能上传图片文件！');
        return false;
      }
      const isLt5M = file.size / 1024 / 1024 < 5;
      if (!isLt5M) {
        message.error('图片大小不能超过 5MB！');
        return false;
      }
      setFileList([file as any]);
      return false;
    },
    fileList,
  };

  const columns = [
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      sorter: (a: any, b: any) => b.year - a.year,
    },
    {
      title: '作文类型',
      dataIndex: 'essayType',
      key: 'essayType',
      filters: [
        { text: '小作文', value: '小作文' },
        { text: '大作文', value: '大作文' },
      ],
      onFilter: (value: any, record: any) => record.essayType === value,
    },
    {
      title: '题目图片',
      key: 'topic_image',
      render: (_: any, record: any) => (
        <Button type="link" onClick={() => handlePreviewImage(record.year, record.essayType)}>
          查看图片
        </Button>
      ),
    },
    {
      title: '参考范文',
      dataIndex: '参考范文',
      key: 'reference',
      ellipsis: true,
      width: 300,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Popconfirm
          title="确定要删除这个题目吗？"
          onConfirm={() => handleDelete(record.year, record.essayType)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加题目
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={topics}
        rowKey={(record) => `${record.year}_${record.essayType}`}
        loading={loading}
      />

      <Modal
        title="添加作文题目"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="year"
            label="年份"
            rules={[{ required: true, message: '请输入年份' }]}
          >
            <Input type="number" placeholder="例如: 2024" />
          </Form.Item>

          <Form.Item
            name="essay_type"
            label="作文类型"
            rules={[{ required: true, message: '请选择作文类型' }]}
          >
            <Select placeholder="选择作文类型">
              <Option value="小作文">小作文</Option>
              <Option value="大作文">大作文</Option>
            </Select>
          </Form.Item>

          <Form.Item label="题目图片" required>
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>选择题目图片</Button>
            </Upload>
          </Form.Item>

          <Form.Item
            name="reference"
            label="参考范文"
            rules={[{ required: true, message: '请输入参考范文' }]}
          >
            <TextArea rows={6} placeholder="输入参考范文..." />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              添加
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={previewOpen}
        title="题目图片预览"
        footer={null}
        onCancel={() => setPreviewOpen(false)}
        width={800}
      >
        {previewImage && (
          <Image
            src={previewImage}
            alt="题目图片"
            style={{ width: '100%' }}
          />
        )}
      </Modal>
    </div>
  );
};

export default TopicManagement;

