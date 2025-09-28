import { AxiosResponse } from 'axios'
import { getAxiosInstance } from '@/services/axios'
import { TranslateArticleResponse } from '@/models/apis/TranslateArticleResponse'

// API call for getting translated article
export async function translateArticle(title: string, language: string): Promise<AxiosResponse<TranslateArticleResponse>> {
  try {
    const axiosInstance = await getAxiosInstance();
    
    console.log('[DEBUG] translateArticle called with title:', title, 'language:', language);
    
    return axiosInstance.get<TranslateArticleResponse>('/wiki_translate/source_article', {
      params: {
        title: title,
        language: language
      }
    });
  } catch (error) {
    console.error('Failed to get axios instance:', error);
    throw error;
  }
}