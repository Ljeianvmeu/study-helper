import React, { useState } from 'react';
import { Card, Tabs } from 'antd';
import ScoreForm from '../components/Scores/ScoreForm';
import ScoreList from '../components/Scores/ScoreList';
import ScoreChart from '../components/Scores/ScoreChart';

const ScorePage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSuccess = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div style={{ padding: 24 }}>
      <Card title="分数统计器">
        <Tabs
          items={[
            {
              key: '1',
              label: '添加分数',
              children: <ScoreForm onSuccess={handleSuccess} />,
            },
            {
              key: '2',
              label: '分数列表',
              children: <ScoreList refresh={refreshKey} />,
            },
            {
              key: '3',
              label: '分数图表',
              children: <ScoreChart />,
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default ScorePage;
