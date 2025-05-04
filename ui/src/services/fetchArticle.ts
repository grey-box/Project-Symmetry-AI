import { FetchArticleRequest } from '@/models/apis/FetchArticleRequest'
import { axiosInstance } from '@/services/axios'
import { FetchArticleResponse } from '@/models/apis/FetchArticleResponse'
import { AxiosResponse } from 'axios'

// API for getting Wikipedia articles
// Note for future maintainers: Please add support for the 'lang' parameter!
export function fetchArticle(sourceArticleUrl: string): Promise<AxiosResponse<FetchArticleResponse>> {
  return axiosInstance.get<FetchArticleResponse>('/symmetry/v1/wiki/articles', {
    params: { query: sourceArticleUrl },
  });
}

