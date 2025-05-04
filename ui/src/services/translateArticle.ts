import { AxiosResponse } from 'axios'
import { axiosInstance } from '@/services/axios'
import { TranslateArticleRequest } from '@/models/apis/TranslateArticleRequest'
import { TranslateArticleResponse } from '@/models/apis/TranslateArticleResponse'

/*
Note that this completely diverges from the design on the FastAPI side:
translate/sourceArticle was a GET request, not POST, and the parameters do not
line up with TranslateArticleRequest. Only URL is provided, no language.
As the API team's tenure is coming to an end, unfortunately we don't have time to
address this.
Future maintainers, please use the same endpoint as fetchArticle and delete this.
 */
// API call for getting translated article
export function translateArticle(body: TranslateArticleRequest): Promise<AxiosResponse<TranslateArticleResponse>> {
  return axiosInstance.post<TranslateArticleResponse, any, TranslateArticleRequest>(
    'translate/sourceArticle',
    body,
  )
}