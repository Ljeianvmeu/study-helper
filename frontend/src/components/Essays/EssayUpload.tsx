import React, { useState, useEffect } from 'react';
import { Form, Select, Radio, Upload, Button, message, Alert, Card } from 'antd';
import { UploadOutlined, LoadingOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { essaysAPI } from '../../services/api';
import type { UploadFile } from 'antd/es/upload/interface';

const { Option } = Select;

interface EssayUploadProps {
  onAnalysisComplete: (data: any, year: number, essayType: string) => void;
  onOcrComplete?: (originalText: string) => void;
}

// 处理状态类型
type ProcessStatus = 'idle' | 'ocr' | 'optimizing' | 'completed';

const EssayUpload: React.FC<EssayUploadProps> = ({ onAnalysisComplete, onOcrComplete }) => {
  const [form] = Form.useForm();
  const [years, setYears] = useState<number[]>([]);
  const [essayTypes, setEssayTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [processStatus, setProcessStatus] = useState<ProcessStatus>('idle');
  const [ocrResult, setOcrResult] = useState<any>(null);

  useEffect(() => {
    loadYears();
  }, []);

  const loadYears = async () => {
    try {
      const { data } = await essaysAPI.getTopics();
      setYears(data.years);
      setEssayTypes(data.essay_types || ['小作文', '大作文']);
      // 设置默认值
      form.setFieldsValue({ essay_type: '小作文' });
    } catch (error) {
      message.error('获取年份列表失败');
    }
  };

  const handleSubmit = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请上传作文图片');
      return;
    }

    const file = fileList[0].originFileObj || fileList[0];
    if (!file) {
      message.error('文件对象无效');
      return;
    }

    setLoading(true);
    
    try {
      // 第一步：OCR识别
      setProcessStatus('ocr');
      const formData = new FormData();
      formData.append('year', values.year.toString());
      formData.append('essay_type', values.essay_type);
      formData.append('image', file as Blob);

      console.log('开始OCR识别...');
      const ocrResponse = await essaysAPI.ocrEssay(formData);
      console.log('OCR识别完成:', ocrResponse.data);
      
      // 保存OCR结果
      setOcrResult(ocrResponse.data);
      
      // 通知父组件OCR完成（如果有回调）
      if (onOcrComplete) {
        onOcrComplete(ocrResponse.data.original_text);
      }
      
      message.success('作文识别完成！开始优化分析...');
      
      // 第二步：优化作文
      setProcessStatus('optimizing');
      const analyzeData = {
        year: values.year,
        essay_type: values.essay_type,
        original_text: ocrResponse.data.original_text,
        topic_image_path: ocrResponse.data.topic_image_path,
        reference_essay: ocrResponse.data.reference_essay
      };

      console.log('开始优化分析...');
      const { data: analysisResult } = await essaysAPI.analyzeEssay(analyzeData);
      console.log('优化分析完成:', analysisResult);
      
      setProcessStatus('completed');
      message.success('作文分析完成！');
      
      onAnalysisComplete(analysisResult, values.year, values.essay_type);
      
    } catch (error: any) {
      console.error('作文分析错误:', error);
      setProcessStatus('idle');
      message.error(error.response?.data?.detail || '分析失败');
    } finally {
      setLoading(false);
    }
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

  // 获取进度状态显示
  const getProgressAlert = () => {
    if (processStatus === 'idle') return null;

    const statusConfig = {
      ocr: {
        type: 'warning' as const,
        message: '识别中',
        description: '正在识别手写作文内容...',
        showLoading: true,
      },
      optimizing: {
        type: 'info' as const,
        message: '优化中',
        description: 'AI正在分析并优化作文...',
        showLoading: true,
      },
      completed: {
        type: 'success' as const,
        message: '优化完成',
        description: '作文分析已完成，请查看结果！',
        showLoading: false,
      },
    };

    const config = statusConfig[processStatus];
    if (!config) return null;

    return (
      <Alert
        type={config.type}
        style={{ marginBottom: 16 }}
        message={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {config.showLoading ? (
              <LoadingOutlined style={{ fontSize: 16 }} />
            ) : (
              <CheckCircleOutlined style={{ fontSize: 16 }} />
            )}
            <span>{config.message}</span>
          </div>
        }
        description={config.description}
      />
    );
  };

  return (
    <div>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item
          name="year"
          label="选择年份"
          rules={[{ required: true, message: '请选择年份' }]}
        >
          <Select placeholder="选择作文年份">
            {years.map((year) => (
              <Option key={year} value={year}>
                {year}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="essay_type"
          label="作文类型"
          rules={[{ required: true, message: '请选择作文类型' }]}
        >
          <Radio.Group buttonStyle="solid">
            {essayTypes.map((type) => (
              <Radio.Button key={type} value={type}>
                {type}
              </Radio.Button>
            ))}
          </Radio.Group>
        </Form.Item>

        <Form.Item
          label="上传作文图片"
          required
        >
          <Upload {...uploadProps}>
            <Button icon={<UploadOutlined />}>选择图片</Button>
          </Upload>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            开始分析
          </Button>
        </Form.Item>
      </Form>

      {/* 处理进度显示 */}
      {getProgressAlert()}

      {/* OCR识别结果显示 */}
      {ocrResult && ocrResult.original_text && (
        <Card 
          title="📄 识别的原文" 
          style={{ marginTop: 16 }}
          headStyle={{ backgroundColor: '#f0f0f0' }}
        >
          <div style={{
            whiteSpace: 'pre-wrap',
            padding: '12px',
            backgroundColor: '#fafafa',
            borderRadius: '4px',
            border: '1px solid #d9d9d9',
            fontFamily: 'monospace',
            fontSize: '14px',
            lineHeight: '1.8',
            textAlign: 'justify'
          }}>
            {ocrResult.original_text}
          </div>
        </Card>
      )}
    </div>
  );
};

export default EssayUpload;

