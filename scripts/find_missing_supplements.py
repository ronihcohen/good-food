import os
import re
import glob

# Constants
FOOD_DIR = "content/food"
SUPPLEMENTS_DIR = os.path.join(FOOD_DIR, "supplements")

# Hebrew to English filename mapping for common vitamins and minerals
HEBREW_TO_FILENAME = {
    "ויטמין A": "vitamin-a",
    "ויטמין B1": "vitamin-b1",
    "ויטמין B2": "vitamin-b2",
    "ויטמין B3": "vitamin-b3",
    "ויטמין B5": "vitamin-b5",
    "ויטמין B6": "vitamin-b6",
    "ויטמין B7": "vitamin-b7",
    "ויטמין B9": "vitamin-b9",
    "ויטמין B12": "vitamin-b12",
    "ויטמין C": "vitamin-c",
    "ויטמין D": "vitamin-d",
    "ויטמין E": "vitamin-e",
    "ויטמין K": "vitamin-k",
    "סידן": "calcium",
    "ברזל": "iron",
    "מגנזיום": "magnesium",
    "אבץ": "zinc",
    "אשלגן": "potassium",
    "נתרן": "sodium",
    "יוד": "iodine",
    "סלניום": "selenium",
    "נחושת": "copper",
    "מנגן": "manganese",
    "כרום": "chromium",
    "פלואוריד": "fluoride",
    "זרחן": "phosphorus",
    "אומגה 3": "omega-3",
    "לציטין": "lecithin",
    "כולין": "choline",
}

def get_existing_supplements():
    if not os.path.exists(SUPPLEMENTS_DIR):
        return set()
    files = glob.glob(os.path.join(SUPPLEMENTS_DIR, "*.md"))
    return {os.path.basename(f).replace(".md", "") for f in files}

def find_mentions_in_food_files():
    mentions = set()
    food_files = glob.glob(os.path.join(FOOD_DIR, "*.md"))
    
    for file_path in food_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for hebrew_term in HEBREW_TO_FILENAME.keys():
                if hebrew_term in content:
                    mentions.add(hebrew_term)
    return mentions

def main():
    existing_supplements = get_existing_supplements()
    mentions = find_mentions_in_food_files()
    
    missing_supplements = []
    
    print("Found mentions:")
    for term in mentions:
        filename = HEBREW_TO_FILENAME.get(term)
        if filename:
            if filename not in existing_supplements:
                print(f"Missing: {term} -> {filename}")
                missing_supplements.append((term, filename))
            else:
                print(f"Exists: {term} -> {filename}")
    
    # Output easy to parse list for next step
    print("\n--- MISSING LIST ---")
    for term, filename in missing_supplements:
        print(f"{term}|{filename}")

if __name__ == "__main__":
    main()
