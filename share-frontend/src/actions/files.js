export const uploadFile = async (file, url) => {
  try {
    const token = localStorage.getItem('access_token');

    const response = await fetch('http://localhost:8000/api/shared-files/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        file: url,
        file_name: file.name,
        file_size: file.size / 1000000 + 'MB',
        share_type: 'private',
        share_expiry: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        file_type: file.type.split('/')[1],
        shared_to: []
      })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    return { error: error.response?.data?.detail || 'File upload failed' };
  }
};

export const getFiles = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://localhost:8000/api/shared-files/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.log(error);
    return { error: error.response?.data?.detail || 'Failed to get files' };
  }
}

export const getFile = async (fileId) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://localhost:8000/api/shared-file/${fileId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    return { error: error.response?.data?.detail || 'Failed to get file' };
  }
}

export const editFile = async (fileId, data) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://localhost:8000/api/shared-files/${fileId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    const responseData = await response.json();
    return responseData;
  } catch (error) {
    return { error: error.response?.data?.detail || 'Failed to edit file' };
  }
}

export const deleteFile = async (fileId) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://localhost:8000/api/shared-files/${fileId}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    return { error: error.response?.data?.detail || 'Failed to delete file' };
  }
}

export const getSimiliarFiles = async (file_url) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://localhost:8000/api/similar-images/?image_url=${file_url}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    return { error: error.response?.data?.detail || 'Failed to get similar files' };
  }
}