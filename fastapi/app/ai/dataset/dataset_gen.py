import json
import sys
from pathlib import Path
from refine_compare import semantic_compare


def read_text_file(filepath):
    """Read and return the contents of a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)


def align_sentences_semantically(original_text, translated_text, source_lang, target_lang, sim_threshold=0.75):
    """
    Use semantic comparison to get sentence pairs from both texts.
    Returns the sentences from the semantic_compare function.
    """
    result = semantic_compare(
        original_blob=original_text,
        translated_blob=translated_text,
        source_language=source_lang,
        target_language=target_lang,
        sim_threshold=sim_threshold
    )

    if not result["success"]:
        print("Warning: Semantic comparison was not fully successful")
        print("Continuing with available data...")

    return result["original_sentences"], result["translated_sentences"]


def create_qna_pairs(original_sentences, translated_sentences, source_lang, target_lang):
    """
    Create QnA pairs from original and translated sentences.

    Returns a list of QnA dictionaries with:
    - Individual sentence pairs (1:1)
    - Batched sentence pairs (10:10)
    - Both directions (original->translated and translated->original)

    Optimized to process each sentence only once.
    """
    qna_dataset = []

    # Determine the minimum length to avoid index errors
    min_length = min(len(original_sentences), len(translated_sentences))

    # Process all individual sentences in one loop
    for i in range(min_length):
        # Original -> Translated
        qna_dataset.append({
            "question": f"Translate this article from {source_lang} to {target_lang}: {original_sentences[i]}",
            "answer": translated_sentences[i],
            "type": "single_sentence",
            "direction": f"{source_lang}_to_{target_lang}",
            "index": i
        })

        # Translated -> Original (Reverse)
        qna_dataset.append({
            "question": f"Translate this article from {target_lang} to {source_lang}: {translated_sentences[i]}",
            "answer": original_sentences[i],
            "type": "single_sentence",
            "direction": f"{target_lang}_to_{source_lang}",
            "index": i
        })

    # Process batched sentences
    batch_size = 10
    for i in range(0, min_length, batch_size):
        end_idx = min(i + batch_size, min_length)

        # Combine sentences once
        original_batch = " ".join(original_sentences[i:end_idx])
        translated_batch = " ".join(translated_sentences[i:end_idx])

        # Original -> Translated
        qna_dataset.append({
            "question": f"Translate this article from {source_lang} to {target_lang}: {original_batch}",
            "answer": translated_batch,
            "type": "batch_sentences",
            "direction": f"{source_lang}_to_{target_lang}",
            "batch_start": i,
            "batch_end": end_idx,
            "batch_size": end_idx - i
        })

        # Translated -> Original (Reverse) - reuse the same batch strings
        qna_dataset.append({
            "question": f"Translate this article from {target_lang} to {source_lang}: {translated_batch}",
            "answer": original_batch,
            "type": "batch_sentences",
            "direction": f"{target_lang}_to_{source_lang}",
            "batch_start": i,
            "batch_end": end_idx,
            "batch_size": end_idx - i
        })

    return qna_dataset


def generate_dataset(original_file, translated_file, source_lang, target_lang,
                     sim_threshold=0.75, output_file="dataset.json"):
    """
    Main function to generate QnA dataset from two text files using semantic comparison.
    """
    print(f"Reading original file: {original_file}")
    original_text = read_text_file(original_file)

    print(f"Reading translated file: {translated_file}")
    translated_text = read_text_file(translated_file)

    print(f"Performing semantic comparison between {source_lang} and {target_lang}...")
    print(f"Using similarity threshold: {sim_threshold}")

    original_sentences, translated_sentences = align_sentences_semantically(
        original_text,
        translated_text,
        source_lang,
        target_lang,
        sim_threshold
    )

    print(f"Found {len(original_sentences)} sentences in original text")
    print(f"Found {len(translated_sentences)} sentences in translated text")

    print("Generating QnA pairs...")
    qna_dataset = create_qna_pairs(original_sentences, translated_sentences, source_lang, target_lang)

    # Create output structure
    output_data = {
        "metadata": {
            "source_language": source_lang,
            "target_language": target_lang,
            "original_file": str(original_file),
            "translated_file": str(translated_file),
            "similarity_threshold": sim_threshold,
            "original_sentence_count": len(original_sentences),
            "translated_sentence_count": len(translated_sentences),
            "total_qna_pairs": len(qna_dataset)
        },
        "qna_pairs": qna_dataset
    }

    print(f"Writing dataset to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Successfully generated dataset with {len(qna_dataset)} QnA pairs")
    print(f"  - Single sentence pairs: {len([q for q in qna_dataset if q['type'] == 'single_sentence'])}")
    print(f"  - Batch sentence pairs: {len([q for q in qna_dataset if q['type'] == 'batch_sentences'])}")

    return output_data


def main():
    # ============================================
    # CONFIGURE YOUR INPUT FILES HERE
    # ============================================

    original_file = "door_eng.txt"  # Path to original text file
    translated_file = "door_spanish.txt"  # Path to translated text file
    source_lang = "en"  # Source language code
    target_lang = "es"  # Target language code
    sim_threshold = 0.75  # Similarity threshold for semantic matching (0.0-1.0)
    output_file = "dataset.json"  # Output JSON file path

    # ============================================

    generate_dataset(
        original_file,
        translated_file,
        source_lang,
        target_lang,
        sim_threshold,
        output_file
    )


if __name__ == "__main__":
    main()