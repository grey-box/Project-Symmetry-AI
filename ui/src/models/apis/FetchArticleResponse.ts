/*
export type FetchArticleResponse = {
  keys: any;
  articleLanguages: Record<string, string>;
  sourceArticle: { text: string, title: string }
}
*/
// Defines the source article API response structure (output)
export type FetchArticleResponse = {
  keys: any;
  sourceArticle: string; // Assuming 'article' contains 'text' and 'title'
  articleLanguages: Record<string, string>; // Assuming 'languages' is a map of language codes to language names
}
