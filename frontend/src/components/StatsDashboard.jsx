// frontend/src/components/StatsDashboard.jsx
import { Bar } from 'react-chartjs-2';

function StatsDashboard() {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Slots Found',
      data: [0, 1, 0, 2, 1],
      backgroundColor: 'rgba(59, 130, 246, 0.6)',
    }]
  };

  return (
    <div className="p-4">
      <h3 className="font-bold">Booking Statistics</h3>
      <Bar data={data} />
    </div>
  );
}