import React, { useState } from 'react';
import { Card, Select, Button, message, Space } from 'antd';
import ReactECharts from 'echarts-for-react';
import { tasksAPI } from '../../services/api';
import type { ChartDataPoint } from '../../types';

const { Option } = Select;

const TaskChart: React.FC = () => {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<'week' | 'month' | 'all'>('week');
  const chartRef = React.useRef<any>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const { data } = await tasksAPI.getChartData(view);
      
      if (!data.data || data.data.length === 0) {
        message.warning('暂无数据');
        setChartData([]);
        return;
      }

      setChartData(data.data);
      message.success('图表生成成功');
    } catch (error) {
      message.error('生成图表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    if (!chartRef.current || chartData.length === 0) {
      message.error('没有可保存的图表');
      return;
    }

    try {
      const chart = chartRef.current.getEchartsInstance();
      const url = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff',
      });

      const link = document.createElement('a');
      link.download = `task-chart-${Date.now()}.png`;
      link.href = url;
      link.click();
      message.success('图表已保存');
    } catch (error) {
      message.error('保存图表失败');
    }
  };

  // 将小时数转换为"x小时xx分钟"格式
  const formatHours = (hours: number): string => {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    if (h === 0) {
      return `${m}分钟`;
    } else if (m === 0) {
      return `${h}小时`;
    } else {
      return `${h}小时${m}分钟`;
    }
  };

  const getOption = () => {
    if (chartData.length === 0) return {};

    const dates = chartData.map((d) => d.date);
    const studyHours = chartData.map((d) => d.study_hours);
    const completionRates = chartData.map((d) => d.completion_rate);

    return {
      title: {
        text: '学习时长与任务完成率统计',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        formatter: (params: any) => {
          let result = `${params[0].axisValue}<br/>`;
          params.forEach((item: any) => {
            if (item.seriesName === '学习时长') {
              result += `${item.marker}${item.seriesName}: ${formatHours(item.value)}<br/>`;
            } else {
              result += `${item.marker}${item.seriesName}: ${item.value.toFixed(1)}%<br/>`;
            }
          });
          return result;
        },
      },
      legend: {
        data: ['学习时长', '完成率'],
        top: 30,
      },
      xAxis: {
        type: 'category',
        data: dates,
        name: '日期',
      },
      yAxis: [
        {
          type: 'value',
          name: '学习时长(小时)',
          position: 'left',
        },
        {
          type: 'value',
          name: '完成率(%)',
          position: 'right',
          max: 100,
        },
      ],
      series: [
        {
          name: '学习时长',
          type: 'bar',
          data: studyHours,
          itemStyle: {
            color: '#1890ff',
          },
          yAxisIndex: 0,
        },
        {
          name: '完成率',
          type: 'line',
          data: completionRates,
          itemStyle: {
            color: '#52c41a',
          },
          yAxisIndex: 1,
          smooth: true,
        },
      ],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
      },
    };
  };

  return (
    <Card title="学习统计图表">
      <Space style={{ marginBottom: 20 }}>
        <Select value={view} onChange={setView} style={{ width: 120 }}>
          <Option value="week">最近一周</Option>
          <Option value="month">最近一月</Option>
          <Option value="all">全部</Option>
        </Select>
        <Button type="primary" onClick={handleGenerate} loading={loading}>
          生成图表
        </Button>
        {chartData.length > 0 && (
          <Button onClick={handleSave}>保存图表</Button>
        )}
      </Space>

      {chartData.length > 0 && (
        <ReactECharts
          ref={chartRef}
          option={getOption()}
          style={{ height: 400 }}
        />
      )}
    </Card>
  );
};

export default TaskChart;

