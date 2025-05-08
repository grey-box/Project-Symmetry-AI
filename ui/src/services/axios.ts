import axios from 'axios'

const AppConstants = await window.electronAPI.getAppConfig();

export const axiosInstance = axios.create({
  baseURL: AppConstants.BACKEND_BASE_URL,
})