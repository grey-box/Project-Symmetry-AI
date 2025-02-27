/*
This file is critical as it handles all the rendering work on frontend.
Whether rendering source article from API call, providing translation languages in dropdown or
providing translated article, all the logic is handled here.
*/


import { useForm } from 'react-hook-form'
import { ChevronRight, Info } from 'lucide-react'
import { useCallback, useState } from 'react'

// Importing UI components and necessary services
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { SelectData } from '@/models/SelectData'
import { fetchArticle } from '@/services/fetchArticle'
import { useAppContext } from '@/context/AppContext'
import { translateArticle } from '@/services/translateArticle'
import { TranslationFormType } from '@/models/TranslationFormType'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'

// Translation languages available for selection
const TRANSLATION_LANGUAGES = [
  { value: 'english', label: 'English' },
  { value: 'french', label: 'French' },
  { value: 'hindi', label: 'Hindi' },
  { value: 'arabic', label: 'Arabic' },
]


const TranslationSection = () => {
  // Function to assign background color based on suggestion type
  const getColorClass = (type: any) => {
    switch (type) {
      case 'change':
        return 'bg-green-100';
      case 'addition':
        return 'bg-red-100';
      default:
        return '';
    }
  };
  
  // State variables for storing available translation languages and article data
  const [availableTranslationLanguages, setAvailableTranslationLanguages] = useState<SelectData<string>[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [texts, setTexts] = useState([
    {
      editing: "",
      reference: "",
      suggestedContribution: "",
      suggestionType: ""
    }
  ]);

  // Setting up form handling with default values
  const form = useForm<TranslationFormType>({
    defaultValues: {
      sourceArticleUrl: '',
      targetArticleLanguage: 'English',
      sourceArticleContent: '',
      translatedArticleContent: '',
    },
  })

  // Accessing global context values
  const { translationTool, APIKey } = useAppContext()

  // Extracting form methods
  const {
    handleSubmit,
    setValue,
  } = form
  
  // Function to handle form submission and fetch article data
  const onSubmit = useCallback(async (data: TranslationFormType) => {
    console.log("Translate button is hit")
    try {
      setIsLoading(true)
      // Fetch the article content from the given URL
      const response = await fetchArticle(data.sourceArticleUrl)
      setValue('sourceArticleContent', response.data.sourceArticle)
      
      // Store fetched article content in texts array
      setTexts(prevTexts => [
        ...prevTexts,
        {
          editing: response.data.sourceArticle,
          reference: response.data.sourceArticle,
          suggestedContribution: '',
          suggestionType: 'change',
        },
      ]);

      // Set available translation languages
      setAvailableTranslationLanguages(
        Object.entries(response.data.articleLanguages).map(([key, value]) => ({
          value,
          label: value,
        })))
      
    } catch (error) {
      console.log(error)
      alert(error)
    } finally {
      setIsLoading(false)
    }
  }, [setValue, translationTool, APIKey])
  
  // Function to handle language selection and translation
  const onLanguageChange = useCallback(async (translateArticleUrl: string) => {
    try {
      setIsLoading(true)
      const response = await translateArticle({ targetArticleUrl: translateArticleUrl })
      console.log(response.data.text)
      setValue('translatedArticleContent', response.data.text)
    } catch (error) {
      console.log(error)
    } finally {
      setIsLoading(false)
    }
  }, [setValue])

  return (
    <section className="bg-white mt-6 rounded-xl shadow-md">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          {/* Top section with instructions and buttons */}
          <div className="flex items-center justify-between p-4">
            <div className="inline-flex items-center gap-x-2">
              <Info size={16} />
              <span className="text-zinc-700 text-xs">
                Here will be instruction regarding translation.
              </span>
            </div>
            <div className="flex gap-x-2">
              <Button 
                disabled={isLoading} 
                type="button" 
                variant="outline" 
                onClick={() => { 
                  console.log("Clear button clicked")
                  setTexts([]) // Clear the texts state
                  form.setValue('sourceArticleContent', '')
                  form.setValue('translatedArticleContent', '')
                }}
              >
                Clear
              </Button>
              <Button disabled={isLoading} variant="default" type="submit">Submit</Button>
              <Button disabled className="flex gap-x-2">Compare <ChevronRight size={16} /></Button>
            </div>
          </div>

          {/* Input fields for source article URL and target language selection */}
          <div className="flex justify-between py-2 px-5 mt-2 h-fit">
            <FormField
              control={form.control}
              name="sourceArticleUrl"
              render={({ field }) => (
                <FormItem className="w-2/5 flex items-center gap-x-4">
                  <FormLabel className="shrink-0">Source Article URL</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter a URL" className="!mt-0" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="targetArticleLanguage"
              render={({ field }) => (
                <FormItem className="w-2/5 flex items-center gap-x-4">
                  <FormLabel className="shrink-0">Target Article Language</FormLabel>
                  <FormControl>
                    <Select
                      onValueChange={(value) => {
                        field.onChange(value);
                      }}
                      defaultValue={field.value}
                      disabled={isLoading || availableTranslationLanguages.length === 0}
                    >
                      <SelectTrigger className="!mt-0">
                        <SelectValue placeholder="Language" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableTranslationLanguages.map(language => (
                          <SelectItem value={language.value} key={language.value}>
                            {language.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <div>
            {texts.map((text, index) => (
              <div key={index} className={getColorClass(text.suggestionType)}>
                <p className="font-medium">{text.reference}</p>
              </div>
            ))}
          </div>
        </form>
      </Form>
    </section>
  )
}

export default TranslationSection
