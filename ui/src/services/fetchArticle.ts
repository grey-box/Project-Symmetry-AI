import { FetchArticleRequest } from '@/models/apis/FetchArticleRequest'
import { axiosInstance } from '@/services/axios'
import { FetchArticleResponse } from '@/models/apis/FetchArticleResponse'
import { AxiosResponse } from 'axios'

// Older fetcArticle function which was updated as we are no longer using earlier method of translation
/*
export function fetchArticle(body: FetchArticleRequest): Promise<AxiosResponse<FetchArticleResponse>> {
  return axiosInstance.post<FetchArticleResponse, any, FetchArticleRequest>(
    // 'translate/sourceArticle',
    'get_article',
    body,
  )
}
*/

// Updated logic which calls '/get_article' endpoint of FastAPI to get source article content
export function fetchArticle(sourceArticleUrl: string): Promise<AxiosResponse<FetchArticleResponse>> {
  return axiosInstance.get<FetchArticleResponse>('/get_article', {
    params: { url: sourceArticleUrl },
  });
}

