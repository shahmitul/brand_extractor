import json
import os
from extractor import BrandExtractor

def main():
    # Load data
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    with open(os.path.join(data_dir, 'brands.json'), 'r', encoding='utf-8') as f:
        brands_data = json.load(f)
    
    with open(os.path.join(data_dir, 'responses.json'), 'r', encoding='utf-8') as f:
        responses = json.load(f)['responses']

    extractor = BrandExtractor(brands_data)
    
    output = {}
    for resp in responses:
        mentions = extractor.extract(resp['response_text'])
        output[resp['id']] = mentions

    # Save extractions
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(responses)} responses. Results saved to output.json")

    # Quick Eval against gold_key if available
    gold_path = os.path.join(data_dir, 'gold_key.json')
    if os.path.exists(gold_path):
        run_evaluation(output, gold_path)

def run_evaluation(pred, gold_path):
    with open(gold_path, 'r') as f:
        gold = json.load(f)['gold']
    
    tp, fp, fn = 0, 0, 0
    
    for rid, gold_mentions in gold.items():
        pred_mentions = pred.get(rid, [])
        
        gold_set = {(m['canonical'], m['start']) for m in gold_mentions}
        pred_set = {(m['canonical'], m['start']) for m in pred_mentions}
        
        tp += len(gold_set & pred_set)
        fp += len(pred_set - gold_set)
        fn += len(gold_set - pred_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n--- Evaluation Results ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

if __name__ == "__main__":
    main()