import React from 'react';
import { Tabs } from 'antd';
import DailyTasks from '../components/Tasks/DailyTasks';
import StudyRecords from '../components/Tasks/StudyRecords';
import TaskChart from '../components/Tasks/TaskChart';

const TaskPage: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Tabs
        items={[
          {
            key: '1',
            label: '今日任务',
            children: <DailyTasks />,
          },
          {
            key: '2',
            label: '历史记录',
            children: <StudyRecords />,
          },
          {
            key: '3',
            label: '统计图表',
            children: <TaskChart />,
          },
        ]}
      />
    </div>
  );
};

export default TaskPage;

