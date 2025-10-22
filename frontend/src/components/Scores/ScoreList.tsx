import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Popconfirm, message, Modal, Form, Select, InputNumber, DatePicker } from 'antd';
import { scoresAPI } from '../../services/api';
import type { Score } from '../../types';
import dayjs from 'dayjs';

const ScoreList: React.FC<{ refresh: number }> = ({ refresh }) => {
  const [scores, setScores] = useState<Score[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [editingScore, setEditingScore] = useState<Score | null>(null);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadScores();
  }, [page, pageSize, refresh]);

  const loadScores = async () => {
    setLoading(true);
    try {
      const { data } = await scoresAPI.getScores({ page, page_size: pageSize });
      setScores(data.data);
      setTotal(data.total);
    } catch (error) {
      message.error('加载分数列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await scoresAPI.deleteScore(id);
      message.success('删除成功');
      loadScores();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleEdit = (score: Score) => {
    setEditingScore(score);
    form.setFieldsValue({
      ...score,
      input_date: dayjs(score.input_date),
    });
    setEditModalVisible(true);
  };

  const handleUpdate = async () => {
    try {
      const values = await form.validateFields();
      await scoresAPI.updateScore(editingScore!.id, {
        ...values,
        input_date: values.input_date.format('YYYY-MM-DD'),
      });
      message.success('更新成功');
      setEditModalVisible(false);
      loadScores();
    } catch (error) {
      message.error('更新失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '科目',
      dataIndex: 'subject',
      key: 'subject',
      width: 100,
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 80,
    },
    {
      title: '试卷类型',
      dataIndex: 'paper_type',
      key: 'paper_type',
      width: 150,
    },
    {
      title: '分数',
      dataIndex: 'score',
      key: 'score',
      width: 80,
    },
    {
      title: '录入日期',
      dataIndex: 'input_date',
      key: 'input_date',
      width: 120,
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: any, record: Score) => (
        <Space>
          <Button type="link" size="small" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Table
        columns={columns}
        dataSource={scores}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page);
            setPageSize(pageSize);
          },
        }}
      />

      <Modal
        title="编辑分数"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => setEditModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="subject" label="科目" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="数学">数学</Select.Option>
              <Select.Option value="专业课">专业课</Select.Option>
              <Select.Option value="英语">英语</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="year" label="年份" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="paper_type" label="试卷类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="真题">真题</Select.Option>
              <Select.Option value="其他">其他</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="score" label="分数" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} step={0.5} />
          </Form.Item>
          <Form.Item name="input_date" label="录入日期" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default ScoreList;
