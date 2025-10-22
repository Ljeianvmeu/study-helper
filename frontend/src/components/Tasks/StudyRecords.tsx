import React, { useState } from 'react';
import { Card, DatePicker, Button, Space, message, Descriptions, Checkbox, InputNumber, List } from 'antd';
import { tasksAPI } from '../../services/api';
import type { DailyTasksResponse, DailyTask } from '../../types';
import dayjs from 'dayjs';

const StudyRecords: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);
  const [data, setData] = useState<DailyTasksResponse | null>(null);
  const [studyHours, setStudyHours] = useState(0);
  const [studyMinutes, setStudyMinutes] = useState(0);
  const [completedTaskIds, setCompletedTaskIds] = useState<number[]>([]);

  const handleQuery = async () => {
    if (!selectedDate) {
      message.warning('请选择日期');
      return;
    }

    setLoading(true);
    try {
      const dateStr = selectedDate.format('YYYY-MM-DD');
      const { data: response } = await tasksAPI.getTasksByDate(dateStr);
      
      // 检查是否有任务
      if (response.total_tasks === 0) {
        message.warning('该日期还没有任务记录');
        setData(null);
        return;
      }
      
      setData(response);
      
      // 设置学习时长
      const hours = Math.floor(response.study_hours);
      const minutes = Math.round((response.study_hours - hours) * 60);
      setStudyHours(hours);
      setStudyMinutes(minutes);
      
      // 设置已完成的任务ID
      const completedIds = response.tasks
        .filter(task => task.completed)
        .map(task => task.id);
      setCompletedTaskIds(completedIds);
      
      message.success('查询成功');
    } catch (error: any) {
      if (error.response?.status === 404) {
        message.warning(error.response?.data?.detail || '该日期没有学习记录');
        setData(null);
      } else {
        message.error('查询失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTaskChange = (taskId: number, checked: boolean) => {
    if (checked) {
      setCompletedTaskIds([...completedTaskIds, taskId]);
    } else {
      setCompletedTaskIds(completedTaskIds.filter((id) => id !== taskId));
    }
  };

  const handleUpdate = async () => {
    if (!data) return;

    setLoading(true);
    try {
      await tasksAPI.updateStudyRecord({
        date: data.date,
        study_hours: studyHours,
        study_minutes: studyMinutes,
        completed_task_ids: completedTaskIds,
      });
      message.success('更新成功！');
      handleQuery(); // 重新查询刷新数据
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="历史记录查询">
      <Space style={{ marginBottom: 16 }}>
        <DatePicker
          value={selectedDate}
          onChange={setSelectedDate}
          placeholder="选择日期"
          format="YYYY-MM-DD"
        />
        <Button type="primary" onClick={handleQuery} loading={loading}>
          查询
        </Button>
      </Space>

      {data && (
        <div>
          <Descriptions bordered column={2} style={{ marginBottom: 16 }}>
            <Descriptions.Item label="日期">{data.date}</Descriptions.Item>
            <Descriptions.Item label="学习时长">
              {data.study_hours.toFixed(2)} 小时
            </Descriptions.Item>
            <Descriptions.Item label="完成任务数">
              {data.completed_tasks} / {data.total_tasks}
            </Descriptions.Item>
            <Descriptions.Item label="完成率">
              {data.completion_rate.toFixed(1)}%
            </Descriptions.Item>
          </Descriptions>

          <Card type="inner" title="修改学习时长" style={{ marginBottom: 16 }}>
            <Space>
              <InputNumber
                min={0}
                max={24}
                value={studyHours}
                onChange={(value) => setStudyHours(value || 0)}
                addonAfter="小时"
              />
              <InputNumber
                min={0}
                max={59}
                value={studyMinutes}
                onChange={(value) => setStudyMinutes(value || 0)}
                addonAfter="分钟"
              />
            </Space>
          </Card>

          <Card type="inner" title="修改完成任务" style={{ marginBottom: 16 }}>
            <List
              dataSource={data.tasks}
              renderItem={(task: DailyTask) => (
                <List.Item key={task.id}>
                  <Checkbox
                    checked={completedTaskIds.includes(task.id)}
                    onChange={(e) => handleTaskChange(task.id, e.target.checked)}
                  >
                    {task.task_name}
                  </Checkbox>
                </List.Item>
              )}
            />
          </Card>

          <Button type="primary" onClick={handleUpdate} loading={loading} block>
            保存修改
          </Button>
        </div>
      )}
    </Card>
  );
};

export default StudyRecords;
