import React, { useState } from 'react';
import { Card, Empty, Tabs } from 'antd';
import EssayUpload from '../components/Essays/EssayUpload';
import EssayAnalysis from '../components/Essays/EssayAnalysis';
import TopicManagement from '../components/Essays/TopicManagement';
import type { EssayAnalysisResponse } from '../types';

const { TabPane } = Tabs;

const EssayPage: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<EssayAnalysisResponse | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2023);
  const [selectedEssayType, setSelectedEssayType] = useState<string>('小作文');
  const [activeTab, setActiveTab] = useState('1');

  const handleAnalysisComplete = (data: EssayAnalysisResponse, year: number, essayType: string) => {
    setAnalysisData(data);
    setSelectedYear(year);
    setSelectedEssayType(essayType);
  };

  return (
    <div style={{ padding: 24 }}>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="作文分析" key="1">
          <Card title="英语作文优化" style={{ marginBottom: 24 }}>
            <EssayUpload onAnalysisComplete={handleAnalysisComplete} />
          </Card>

          {analysisData ? (
            <EssayAnalysis 
              data={analysisData} 
              year={selectedYear} 
              essayType={selectedEssayType} 
            />
          ) : (
            <Card>
              <Empty description="上传作文图片开始分析" />
            </Card>
          )}
        </TabPane>

        <TabPane tab="题目管理" key="2">
          <Card title="作文题目管理">
            <TopicManagement />
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default EssayPage;

