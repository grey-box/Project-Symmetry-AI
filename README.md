### Project-Symmetry-AI


Project Symmetry is an application using AI to accelerate Wikipedia's translation efforts in less-represented languages (less than 1 million articles) by building a semantic understanding of similar articles in various Wikipedia languages and providing relevant translations for missing information

### Goal

Improve the translation of content like Wikipedia in under-represented languages

### Scope

Living in a globalized country with fast-growing technologies, we need to have other sources for translation rather than just relying on the human translator.

There are great disparities in how Wikipedia can be accessed across various languages. At Grey-box, we believe that everyone should be able to access the same quality of information – regardless of their native language. This information should also be equivalent across various languages.

We want to translate content from one language in Wikipedia to another in order to improve the overall Wikipedia content, especially in underrepresented languages. For example, a local French scientist might have a great article in the French version of Wikipedia but he could be barely mentioned in the English version – or vice versa.

Project Symmetry is a collaboration between RMIT University’s students and Grey-box.

### Benefits

Translation plays an imperative part and makes the difference when it comes to establishing relations, spreading thoughts and conveying information worldwide. 

English is not the only language which should be considered as the focal point in a world where over 7000 languages are spoken. Wikipedia provides everyone with this inconceivably vast information about every single thing.

Grey-box is trying to provide digital education content translation in people’s own native language without any important content being cut out.

A data set consisting of hundreds of gigabytes of clean English content is scratched from the web. Recognizing that the most utility of transfer learning is the plausibility of leveraging pre-trained models in data-scarce settings, we discharge our code, information sets and pre-trained models. This adaptability is used by assessing execution on a wide assortment of English-based NLP issues, counting address replying document.

We are trying to improvise the existing solution by researching on all the implemented models (BERT, XLNET, Sequence-Sequence, RNN, NMT) and we proceeded by filtering the recent models such as RNN, T5 and Marian NMT.

BLEU (Bilingual Evaluation Understudy) considers different reference translations, each of which may utilize a distinctive word choice to interpret the same source word. The BLEU metric ranges from 0 to 1. Hence, this metric was used to measure the accuracy.

Few possible outcomes for the models were improvised and the accuracy was calculated using BLEU score. The first model was the T5 model for which we got the BLEU score as 87.89% when using the DeepL and a score of 88.74% when using google Translate. The second model was the Marian NMT model which was implemented under same circumstances and the BLEU score was 83.27% and 84.8% for the latter. Finally, comparing google translate using DeepL, which resulted in 93.68 % accuracy.

For future research, these algorithms can be tested using GPT-3 to obtain a different result. The problem faced so far is that the data set chosen was incredibly huge which resulted in trouble running it, because of the insufficient RAM. Since the whole article couldn’t be translated, it had to be split into sentences as it would exceed the length of the tokenizer.

For future work, other models implemented with these methods can be improvised.

### **Proposed Solution**

We do not have to limit ourselves to translate in only one direction. The goal is to **build a semantic understanding of similar articles in various Wikipedia languages and provide relevant translations for missing information** – and maybe even **identify conflicting information and biases.**  We can do this for multiple languages at the same time, where each of  the languages can contribute and benefit from the information contained  in the other languages.

Teams have and are working on **validating** the use case of various models for translation, including **pre-trained models** like **T5 and Marian** and models that require **training** like **RNN**.

An example of what contributes to Symmetry:  **BLEU (Bilingual Evaluation Understudy)** **considers different reference translations,** each of which may utilize a distinctive word choice to interpret the same source word. The BLEU **metric ranges from 0 to 1.** Hence, this metric was used to **measure the accuracy.**

![Untitled](https://github.com/user-attachments/assets/2e2aef18-4218-4639-a6ea-a3a6b548c79e)

