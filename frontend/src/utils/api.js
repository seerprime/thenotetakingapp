import axios from "axios";

const API_BASE = "http://localhost:8000";

export const uploadAudio = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_BASE}/transcribe/`, formData);
  return res.data.transcription;
};

export const getKeyPoints = async (text) => {
  const res = await axios.post(`${API_BASE}/summarize/`, { text });
  return res.data.key_points;
};

export const queryJarvis = async (query, embedding) => {
  const res = await axios.post(`${API_BASE}/query/`, { query, embedding });
  return res.data.answer;
};
