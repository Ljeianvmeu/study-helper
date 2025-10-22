import React, { useState } from 'react';
import { Form, Select, Button, message, Space } from 'antd';
import ReactECharts from 'echarts-for-react';
import { scoresAPI } from '../../services/api';
import type { ChartDataResponse } from '../../types';

const ScoreChart: React.FC = () => {
  const [chartData, setChartData] = useState<ChartDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const chartRef = React.useRef<any>(null);

  const handleGenerate = async (values: any) => {
    setLoading(true);
    try {
      const { data } = await scoresAPI.getChartData(
        values.subject,
        values.paper_type
      );

      if (!data.dates || data.dates.length === 0) {
        message.warning(data.message || '未查询到相关数据');
        setChartData(null);
        return;
      }

      setChartData(data);
      message.success('图表生成成功');
    } catch (error) {
      message.error('生成图表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    if (!chartRef.current) {
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
      link.download = `score-chart-${Date.now()}.png`;
      link.href = url;
      link.click();
      message.success('图表已保存');
    } catch (error) {
      message.error('保存图表失败');
    }
  };

  const getOption = () => {
    if (!chartData) return {};

    const maxScore = chartData.subject === '英语' ? 100 : 150;

    return {
      title: {
        text: `${chartData.subject}分数趋势图`,
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: chartData.dates,
        name: '日期',
      },
      yAxis: {
        type: 'value',
        name: '分数',
        min: 0,
        max: maxScore,
      },
      series: [
        {
          data: chartData.scores,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#1890ff',
          },
          lineStyle: {
            width: 2,
          },
          markPoint: {
            data: [
              { type: 'max', name: '最高分' },
              { type: 'min', name: '最低分' },
            ],
          },
          markLine: {
            data: [{ type: 'average', name: '平均值' }],
          },
        },
      ],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '15%',
      },
    };
  };

  return (
    <div>
      <Form layout="inline" onFinish={handleGenerate} style={{ marginBottom: 20 }}>
        <Form.Item
          name="subject"
          label="科目"
          rules={[{ required: true, message: '请选择科目' }]}
        >
          <Select style={{ width: 120 }} placeholder="选择科目">
            <Select.Option value="数学">数学</Select.Option>
            <Select.Option value="专业课">专业课</Select.Option>
            <Select.Option value="英语">英语</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item name="paper_type" label="试卷类型（可选）">
          <Select style={{ width: 150 }} placeholder="全部" allowClear>
            <Select.Option value="真题">真题</Select.Option>
            <Select.Option value="其他">其他</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading}>
              生成图表
            </Button>
            {chartData && (
              <Button onClick={handleSave}>保存图表</Button>
            )}
          </Space>
        </Form.Item>
      </Form>

      {chartData && chartData.dates.length > 0 && (
        <ReactECharts
          ref={chartRef}
          option={getOption()}
          style={{ height: 400 }}
        />
      )}
    </div>
  );
};

export default ScoreChart;
