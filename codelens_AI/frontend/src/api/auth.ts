export const API_URL = 'http://localhost:8000/api/v1';

export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

export const getFormHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

export const login = async (formData: FormData) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    body: formData,
    // Note: Do NOT set Content-Type for FormData, browser sets it with boundary
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  return response.json();
};

export const register = async (data: any) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }
  return response.json();
};

export const getMe = async () => {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
};
