import React from 'react';
import { Card, Row, Col, Button, message, Typography, Divider, List, Image } from 'antd';
import { essaysAPI } from '../../services/api';
import type { EssayAnalysisResponse } from '../../types';

const { Title, Paragraph, Text } = Typography;

interface EssayAnalysisProps {
  data: EssayAnalysisResponse;
  year: number;  // 添加年份参数
  essayType: string;  // 添加作文类型参数
}

const EssayAnalysis: React.FC<EssayAnalysisProps> = ({ data, year, essayType }) => {
  const handleSave = async () => {
    try {
      // 准备保存的完整数据
      const saveData = {
        topic: data.topic,
        essay_type: essayType,
        reference_essay: data.reference_essay,
        original_text: data.original_text,
        optimized_text: data.optimized_text,
        score: data.score,
        suggestions: data.suggestions
      };
      
      await essaysAPI.saveAnalysis(year, saveData);
      message.success('分析报告已保存为Markdown文件');
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <div>
      <Button type="primary" onClick={handleSave} style={{ marginBottom: 16 }}>
        保存为Markdown
      </Button>

      {/* AI评分展示 */}
      {data.score && (
        <Card 
          title="📊 AI评分" 
          style={{ marginBottom: 16 }}
          headStyle={{ backgroundColor: '#1890ff', color: 'white' }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Title level={2} style={{ color: '#1890ff', marginBottom: 8 }}>
                  {data.score.points}分
                </Title>
                <Text type="secondary">总分：{essayType === '小作文' ? '10' : '20'}分</Text>
              </div>
            </Col>
            <Col span={12}>
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Title level={4} style={{ marginBottom: 8 }}>
                  {data.score.level}
                </Title>
                <Text type="secondary">评分档位</Text>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      <Card title="📝 作文题目" style={{ marginBottom: 16 }}>
        {(data as any).topic_image_path ? (
          <Image
            src={`http://localhost:8000/${(data as any).topic_image_path}`}
            alt="作文题目"
            style={{ maxWidth: '100%', maxHeight: 400 }}
            fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
          />
        ) : (
          <Paragraph>{data.topic}</Paragraph>
        )}
      </Card>

      <Card title="📚 参考范文" style={{ marginBottom: 16 }}>
        <Paragraph style={{ whiteSpace: 'pre-wrap', textAlign: 'justify', lineHeight: '1.8' }}>
          {data.reference_essay}
        </Paragraph>
      </Card>

      <Card title="📊 作文对比" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={5}>原文</Title>
            <div
              style={{
                background: '#f5f5f5',
                padding: 16,
                borderRadius: 4,
                minHeight: 200,
                whiteSpace: 'pre-wrap',
                textAlign: 'justify',
                lineHeight: '1.8',
              }}
            >
              {data.original_text}
            </div>
          </Col>
          <Col span={12}>
            <Title level={5}>优化后</Title>
            <div
              style={{
                background: '#e6f7ff',
                padding: 16,
                borderRadius: 4,
                minHeight: 200,
                whiteSpace: 'pre-wrap',
                textAlign: 'justify',
                lineHeight: '1.8',
              }}
            >
              {data.optimized_text}
            </div>
          </Col>
        </Row>
      </Card>

      <Card title="💡 修改建议">
        <Title level={5}>1. 题意符合度</Title>
        {(() => {
          // 兼容两种字段名：topic_compliance（新）和 topic_relevance（旧）
          const topicContent = data.suggestions.topic_compliance || 
                              (data.suggestions.topic_relevance ? [data.suggestions.topic_relevance] : []);
          return Array.isArray(topicContent) && topicContent.length > 0 ? (
            <List
              dataSource={topicContent}
              renderItem={(item) => (
                <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                  <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
                </List.Item>
              )}
            />
          ) : (
            <Paragraph style={{ textAlign: 'justify', lineHeight: '1.8' }}>{topicContent}</Paragraph>
          );
        })()}
        <Divider />

        <Title level={5}>2. 拼写错误</Title>
        {data.suggestions.spelling_errors?.length > 0 ? (
          <List
            dataSource={data.suggestions.spelling_errors}
            renderItem={(item) => (
              <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
              </List.Item>
            )}
          />
        ) : (
          <Text type="success">无拼写错误 ✓</Text>
        )}
        <Divider />

        <Title level={5}>3. 语法错误</Title>
        {data.suggestions.grammar_errors?.length > 0 ? (
          <List
            dataSource={data.suggestions.grammar_errors}
            renderItem={(item) => (
              <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
              </List.Item>
            )}
          />
        ) : (
          <Text type="success">无语法错误 ✓</Text>
        )}
        <Divider />

        <Title level={5}>4. 单词优化</Title>
        {data.suggestions.word_optimization?.length > 0 ? (
          <List
            dataSource={data.suggestions.word_optimization}
            renderItem={(item) => (
              <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
              </List.Item>
            )}
          />
        ) : (
          <Text type="success">无需优化 ✓</Text>
        )}
        <Divider />

        <Title level={5}>5. 句式优化</Title>
        {data.suggestions.sentence_optimization?.length > 0 ? (
          <List
            dataSource={data.suggestions.sentence_optimization}
            renderItem={(item) => (
              <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
              </List.Item>
            )}
          />
        ) : (
          <Text type="success">无需优化 ✓</Text>
        )}
        <Divider />

        <Title level={5}>6. 结构优化</Title>
        {(() => {
          const structContent = data.suggestions.structure_optimization;
          return Array.isArray(structContent) ? (
            <List
              dataSource={structContent}
              renderItem={(item) => (
                <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                  <Text style={{ textAlign: 'justify', display: 'block', lineHeight: '1.8' }}>• {item}</Text>
                </List.Item>
              )}
            />
          ) : (
            <Paragraph style={{ textAlign: 'justify', lineHeight: '1.8' }}>{structContent}</Paragraph>
          );
        })()}
      </Card>
    </div>
  );
};

export default EssayAnalysis;

