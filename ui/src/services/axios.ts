import axios from 'axios'
import { AppConstants } from '@/constants/AppConstants'

export const axiosInstance = axios.create({
  baseURL: AppConstants.BACKEND_BASE_URL,
})