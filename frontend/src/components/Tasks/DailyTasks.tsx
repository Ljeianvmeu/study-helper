import React, { useState, useEffect } from 'react';
import { 
  Card, Checkbox, InputNumber, Button, message, Space, Row, Col, 
  Statistic, DatePicker, Input, Popconfirm, List 
} from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { tasksAPI } from '../../services/api';
import type { DailyTasksResponse, DailyTask } from '../../types';
import dayjs, { Dayjs } from 'dayjs';

const DailyTasks: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DailyTasksResponse | null>(null);
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [studyHours, setStudyHours] = useState(0);
  const [studyMinutes, setStudyMinutes] = useState(0);
  const [completedTaskIds, setCompletedTaskIds] = useState<number[]>([]);
  const [newTaskName, setNewTaskName] = useState('');
  const [addingTask, setAddingTask] = useState(false);

  useEffect(() => {
    loadTasks();
  }, [selectedDate]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const dateStr = selectedDate.format('YYYY-MM-DD');
      const { data: response } = await tasksAPI.getTasksByDate(dateStr);
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
    } catch (error) {
      message.error('加载任务失败');
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

  const handleSave = async () => {
    if (!data) return;

    setLoading(true);
    try {
      await tasksAPI.saveStudyRecord({
        date: data.date,
        study_hours: studyHours,
        study_minutes: studyMinutes,
        completed_task_ids: completedTaskIds,
      });
      message.success('保存成功！');
      loadTasks();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async () => {
    if (!newTaskName.trim()) {
      message.warning('请输入任务名称');
      return;
    }

    setAddingTask(true);
    try {
      await tasksAPI.addTask({
        date: selectedDate.format('YYYY-MM-DD'),
        task_name: newTaskName,
      });
      message.success('任务添加成功！');
      setNewTaskName('');
      loadTasks();
    } catch (error) {
      message.error('添加任务失败');
    } finally {
      setAddingTask(false);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await tasksAPI.deleteTask(taskId);
      message.success('任务删除成功！');
      loadTasks();
    } catch (error) {
      message.error('删除任务失败');
    }
  };

  const completionRate = data
    ? (completedTaskIds.length / data.total_tasks) * 100
    : 0;

  return (
    <Card title="每日任务" loading={loading}>
      {/* 日期选择器 */}
      <div style={{ marginBottom: 24 }}>
        <Space>
          <span style={{ fontWeight: 'bold' }}>选择日期：</span>
          <DatePicker
            value={selectedDate}
            onChange={(date) => date && setSelectedDate(date)}
            format="YYYY-MM-DD"
            allowClear={false}
          />
          <Button 
            type="default" 
            onClick={() => setSelectedDate(dayjs())}
          >
            今天
          </Button>
        </Space>
      </div>

      {data && (
        <>
          {/* 统计信息 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Statistic
                title="当前日期"
                value={selectedDate.format('YYYY年MM月DD日')}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="已完成任务"
                value={completedTaskIds.length}
                suffix={`/ ${data.total_tasks}`}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="完成率"
                value={completionRate.toFixed(1)}
                suffix="%"
              />
            </Col>
          </Row>

          {/* 任务列表 */}
          <Card type="inner" title="任务列表" style={{ marginBottom: 16 }}>
            <List
              dataSource={data.tasks}
              renderItem={(task: DailyTask) => (
                <List.Item
                  key={task.id}
                  actions={[
                    <Popconfirm
                      title="确定要删除这个任务吗？"
                      onConfirm={() => handleDeleteTask(task.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button 
                        type="text" 
                        danger 
                        icon={<DeleteOutlined />}
                        size="small"
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <Checkbox
                    checked={completedTaskIds.includes(task.id)}
                    onChange={(e) => handleTaskChange(task.id, e.target.checked)}
                  >
                    {task.task_name}
                  </Checkbox>
                </List.Item>
              )}
            />
            
            {/* 添加新任务 */}
            <div style={{ marginTop: 16 }}>
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  placeholder="输入新任务名称..."
                  value={newTaskName}
                  onChange={(e) => setNewTaskName(e.target.value)}
                  onPressEnter={handleAddTask}
                />
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={handleAddTask}
                  loading={addingTask}
                >
                  添加任务
                </Button>
              </Space.Compact>
            </div>
          </Card>

          {/* 学习时长 */}
          <Card type="inner" title="学习时长" style={{ marginBottom: 16 }}>
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

          {/* 保存按钮 */}
          <Button type="primary" onClick={handleSave} loading={loading} block size="large">
            保存记录
          </Button>
        </>
      )}
    </Card>
  );
};

export default DailyTasks;
