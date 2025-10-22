import React, { useState, useEffect } from 'react';
import { Form, Select, InputNumber, DatePicker, Button, message } from 'antd';
import { scoresAPI } from '../../services/api';
import dayjs from 'dayjs';
import type { ScoreCreateRequest } from '../../types';

const { Option } = Select;

const ScoreForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const [form] = Form.useForm();
  const [paperTypes, setPaperTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<string>('数学');

  useEffect(() => {
    loadPaperTypes('数学');
  }, []);

  const loadPaperTypes = async (subject: string) => {
    try {
      const { data } = await scoresAPI.getPaperTypes(subject);
      setPaperTypes(data.paper_types);
      form.setFieldsValue({ paper_type: data.paper_types[0] });
    } catch (error) {
      message.error('获取试卷类型失败');
    }
  };

  const handleSubjectChange = (value: string) => {
    setSelectedSubject(value);
    loadPaperTypes(value);
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const data: ScoreCreateRequest = {
        ...values,
        input_date: values.input_date.format('YYYY-MM-DD'),
      };
      await scoresAPI.createScore(data);
      message.success('分数添加成功！');
      form.resetFields();
      form.setFieldsValue({ input_date: dayjs() });
      onSuccess();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        subject: '数学',
        input_date: dayjs(),
      }}
    >
      <Form.Item
        name="subject"
        label="科目"
        rules={[{ required: true, message: '请选择科目' }]}
      >
        <Select onChange={handleSubjectChange}>
          <Option value="数学">数学</Option>
          <Option value="专业课">专业课</Option>
          <Option value="英语">英语</Option>
        </Select>
      </Form.Item>

      <Form.Item
        name="year"
        label="年份"
        rules={[
          { required: true, message: '请输入年份' },
          { type: 'number', min: 2000, max: 2100, message: '年份范围: 2000-2100' },
        ]}
      >
        <InputNumber style={{ width: '100%' }} placeholder="例如: 2024" />
      </Form.Item>

      <Form.Item
        name="paper_type"
        label="试卷类型"
        rules={[{ required: true, message: '请选择试卷类型' }]}
      >
        <Select>
          {paperTypes.map((type) => (
            <Option key={type} value={type}>
              {type}
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="score"
        label="分数"
        rules={[
          { required: true, message: '请输入分数' },
          {
            validator: (_, value) => {
              if (selectedSubject === '英语' && (value < 0 || value > 100)) {
                return Promise.reject('英语分数范围: 0-100');
              }
              if (['数学', '专业课'].includes(selectedSubject) && (value < 0 || value > 150)) {
                return Promise.reject('分数范围: 0-150');
              }
              return Promise.resolve();
            },
          },
        ]}
      >
        <InputNumber
          style={{ width: '100%' }}
          step={0.5}
          placeholder="请输入分数"
        />
      </Form.Item>

      <Form.Item
        name="input_date"
        label="录入日期"
        rules={[{ required: true, message: '请选择日期' }]}
      >
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          添加分数
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ScoreForm;
