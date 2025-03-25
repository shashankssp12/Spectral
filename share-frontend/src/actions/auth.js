export const registerUser = async (formData) => {
  try {
    const response = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error('Failed to register user');
  }
}

export const loginUser = async (formData) => {
  try {
    const response = await fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error('Failed to login user');
  }
}

export const getProfile = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/profile/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error('Failed to get profile');
  }
}