import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

// Register Chart.js components
ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Custom plugin to draw a vertical line following the cursor
const verticalLinePlugin = {
  id: 'verticalLine',
  afterDatasetsDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    const xScale = scales.x;
    const yScale = scales.y;

    // Get the active elements (hovered points)
    const activeElements = chart.tooltip.getActiveElements();

    if (activeElements.length) {
      const activePoint = activeElements[0];
      const x = activePoint.element.x; // X position of the hovered point

      // Draw the vertical line
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(x, chartArea.top);
      ctx.lineTo(x, chartArea.bottom);
      ctx.lineWidth = 1;
      ctx.strokeStyle = '#1D2521'; // Dark gray line to match the design
      ctx.stroke();
      ctx.restore();
    }
  },
  afterEvent(chart, args) {
    // Update the tooltip position as the cursor moves
    const { event } = args;
    if (event.type === 'mousemove') {
      const x = event.x;
      const y = event.y;
      const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: false }, true);
      if (points.length) {
        chart.tooltip.setActiveElements(
          [{ datasetIndex: points[0].datasetIndex, index: points[0].index }],
          { x, y }
        );
        chart.draw();
      }
    }
  }
};

// Register the custom plugin
ChartJS.register(verticalLinePlugin);

const WeightChart = ({ historical, predicted }) => {
  const data = {
    datasets: [
      {
        label: 'Historical Weights',
        data: historical.map(item => ({ x: item.date, y: item.weight })),
        borderColor: '#007AFF', // Apple’s signature blue
        backgroundColor: '#007AFF',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
        fill: false,
      },
      {
        label: 'Predicted Weights',
        data: predicted.map(item => ({ x: item.date, y: item.weight })),
        borderColor: '#FF3B30', // Apple’s muted red
        backgroundColor: '#FF3B30',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
        fill: false,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          displayFormats: {
            day: 'MMM d' // e.g., "Aug 11"
          }
        },
        title: {
          display: true,
          text: 'Date',
          color: '#1D2521',
          font: {
            family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 14,
            weight: '500',
          },
          padding: 10,
        },
        ticks: {
          color: '#1D2521',
          font: {
            family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 12,
          },
        },
        grid: {
          display: false,
        },
      },
      y: {
        title: {
          display: true,
          text: 'Weight (lbs)',
          color: '#1D2521',
          font: {
            family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 14,
            weight: '500',
          },
          padding: 10,
        },
        ticks: {
          color: '#1D2521',
          font: {
            family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 12,
          },
        },
        grid: {
          color: '#E5E7EB',
          borderDash: [5, 5],
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#1D2521',
          font: {
            family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 12,
            weight: '500',
          },
          usePointStyle: true,
          pointStyle: 'rectRounded',
          padding: 20,
        },
      },
      tooltip: {
        enabled: true,
        mode: 'nearest',
        intersect: false,
        backgroundColor: '#1D2521',
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        titleFont: {
          family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          size: 12,
          weight: '500',
        },
        bodyFont: {
          family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          size: 12,
        },
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          title: function(tooltipItems) {
            const date = new Date(tooltipItems[0].parsed.x);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); // e.g., "Aug 11"
          },
          label: function(context) {
            const label = context.dataset.label || '';
            const value = Math.round(context.parsed.y);
            return `${label}: ${value}`;
          }
        }
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart',
    },
    maintainAspectRatio: false,
    interaction: {
      mode: 'nearest',
      intersect: false,
      axis: 'x',
    },
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Line data={data} options={options} />
    </div>
  );
};

export default WeightChart;