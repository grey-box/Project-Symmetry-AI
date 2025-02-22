import { AxiosResponse } from 'axios'
import { axiosInstance } from '@/services/axios'
import { TranslateArticleRequest } from '@/models/apis/TranslateArticleRequest'
import { TranslateArticleResponse } from '@/models/apis/TranslateArticleResponse'

// API call for getting translated article
export function translateArticle(body: TranslateArticleRequest): Promise<AxiosResponse<TranslateArticleResponse>> {
  return axiosInstance.post<TranslateArticleResponse, any, TranslateArticleRequest>(
    'translate/targetArticle',
    body,
  )
}