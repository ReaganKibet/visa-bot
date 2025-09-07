// frontend/src/api.js
import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000' });

export const startMonitor = () => API.post('/monitors/', { flow: 'mozambique-to-portugal' });
export const createBooking = () => API.post('/bookings/', { applicant_id: 'APPL-1001', run_id: 'run_123' });
export const getStatus = () => API.get('/status/');