// frontend/src/components/BookingButton.jsx
import axios from 'axios';

function BookingButton() {
  const startBooking = async () => {
    try {
      await axios.post("http://localhost:8000/bookings/", {
        applicant_id: "APPL-1001",
        run_id: "run_123"
      });
      alert("Booking started! Browser will open on server.");
    } catch (err) {
      alert("Failed to start booking");
    }
  };

  return (
    <button onClick={startBooking} className="bg-blue-600 text-white px-4 py-2">
      🟢 Start Booking
    </button>
  );
}