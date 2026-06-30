# Brand Extractor Project Analysis

## 1. My Approach
To build this extractor, I focused on a "Hybrid Model." I used **Regular Expressions (Regex)** for the initial search because it's fast and works well across different languages, and then used **Natural Language Processing (NLP)** via the `spaCy` library to filter out the tricky cases.

The strategy: For English, I utilized spaCy's POS tagging to disambiguate brands that double as common adjectives (like 'Clear' or 'Simple'). For Arabic, I relied on exact string matching of transliterated aliases. This was a sensible tradeoff because Arabic brand names are linguistically distinct from common vocabulary, making heavy NLP processing unnecessary for high-precision extraction.

## 2. Solving the Hard Cases

### The "Common Word" Problem (Always, Simple, Clear, Dove)
This was the most challenging part because words like "simple" or "clear" appear constantly in English without referring to a brand. 
*   **Capitalization:** I set a rule that for these specific English words, the first letter must be capitalized. In AI responses, brands are almost always properly capitalized, while adjectives are not.
*   **Grammar Check (POS Tagging):** I used `spaCy` to check the "Part of Speech." If the code finds the word "Clear," it checks if it's being used as a Noun or an Adjective. If the sentence is "Clear results take time," the NLP identifies "Clear" as an adjective and my code ignores it.
*   **Phrase Exclusions:** I created a small list of phrases that I noticed were causing issues, like "dove-soft" and "keep it simple," to filter them out immediately.

### Cross-lingual and Arabic Variants
For Arabic, I took a more direct approach:
*   **Mapping:** I mapped every Arabic alias and transliteration (like "Pantine") back to the canonical brand name (Pantene).
*   **Regex Strategy:** I avoided using word boundaries (`\b`) for Arabic script because they often fail to recognize characters correctly. Instead, I used literal matches. This ensures that even if a brand name has an Arabic prefix attached to it, the system can still find it.

## 3. Evaluation Results
I ran the extractor against the provided `gold_key.json` ground truth.

| Metric | Score |
| :--- | :--- |
| **Precision** | 1.0000 |
| **Recall** | 0.9500 |
| **F1 Score** | 0.9744 |

### Why these results?
*   **Precision (1.00):** This is perfect because the AI responses provided are very grammatically correct. The capitalization and POS tagging rules worked exactly as intended.
*   **Recall (0.95):** I missed a few mentions. This mostly happened in the Arabic responses where the spelling or elongation (Kashida) didn't perfectly match the aliases provided in the `brands.json` file.

## 4. Risks & Future Improvements
*   **Scaling:** Right now, the code loops through every brand one by one. If we had 5,000 brands, this would be very slow. 
*   **Better Arabic Support:** Arabic is a complex language where "and," "the," and "with" are often attached to the start of the brand name. 

## 5. Summary of Tradeoffs
Because I had a 3-5 hour window, I prioritized **Precision** over trying to find every possible spelling variation. In brand tracking, it is usually better to provide 100% accurate data than to include "guesses" that might be wrong. I also chose `spaCy` because it is lightweight and fast compared to using a massive AI model like BERT or GPT for a simple extraction task.