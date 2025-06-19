import csv
import os
import shutil
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration
BEEG_USER_ID = os.getenv('BEEG_USER_ID')  # Replace with Beeg's actual Discord user ID
BEEG_MENTION = f"<@{BEEG_USER_ID}>"

def backup_file(filename):
    """Create a backup of the original file"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✅ Created backup: {backup_name}")
        return True
    return False

def replace_beeg_with_mention(text):
    """Replace all instances of 'Beeg' with the Discord mention"""
    # Use word boundaries to avoid replacing parts of other words
    # This will match "Beeg", "Beeg's", "BEEG", "beeg", etc.
    pattern = r'\bBeeg\b'
    return re.sub(pattern, BEEG_MENTION, text, flags=re.IGNORECASE)

def update_phrases(filename='beeg_summoning_phrases.csv'):
    """Replace Beeg with mention in summoning phrases"""
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return False
    
    # Create backup
    backup_file(filename)
    
    # Read all rows and track changes
    rows = []
    changes_count = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            original_phrase = row['phrase']
            updated_phrase = replace_beeg_with_mention(original_phrase)
            
            if original_phrase != updated_phrase:
                changes_count += 1
            
            row['phrase'] = updated_phrase
            rows.append(row)
    
    # Write back to file
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Updated {changes_count} phrases in {filename} (out of {len(rows)} total)")
    return True

def update_haikus(filename='beeg_summoning_haikus.csv'):
    """Replace Beeg with mention in haikus"""
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return False
    
    # Create backup
    backup_file(filename)
    
    # Read all rows and track changes
    rows = []
    changes_count = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            original_haiku = row['haiku']
            updated_haiku = replace_beeg_with_mention(original_haiku)
            
            if original_haiku != updated_haiku:
                changes_count += 1
            
            row['haiku'] = updated_haiku
            rows.append(row)
    
    # Write back to file
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Updated {changes_count} haikus in {filename} (out of {len(rows)} total)")
    return True

def preview_changes(filename, num_examples=5):
    """Preview what the changes will look like"""
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return
    
    print(f"\n🔍 Preview of changes for {filename}:")
    print("=" * 80)
    
    examples_shown = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if examples_shown >= num_examples:
                break
            
            if 'phrase' in row:
                original = row['phrase']
                updated = replace_beeg_with_mention(original)
                
                # Only show examples that actually change
                if original != updated:
                    print(f"Row {row['number']}:")
                    print(f"BEFORE: {original}")
                    print(f"AFTER:  {updated}")
                    print("-" * 50)
                    examples_shown += 1
                    
            elif 'haiku' in row:
                original = row['haiku']
                updated = replace_beeg_with_mention(original)
                
                # Only show examples that actually change
                if original != updated:
                    print(f"Row {row['number']}:")
                    print(f"BEFORE: {original}")
                    print(f"AFTER:  {updated}")
                    print("-" * 50)
                    examples_shown += 1
    
    if examples_shown == 0:
        print("No changes found in preview (no instances of 'Beeg' to replace)")

def count_beeg_instances(filename):
    """Count how many messages contain 'Beeg'"""
    if not os.path.exists(filename):
        return 0
    
    count = 0
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            text = row.get('phrase', '') or row.get('haiku', '')
            if re.search(r'\bBeeg\b', text, re.IGNORECASE):
                count += 1
    
    return count

def main():
    print("🔮 Beeg → Mention Replacement Script 🔮")
    print("=" * 50)
    
    # Update the user ID at the top of this script first!
    print(f"Beeg will be replaced with: {BEEG_MENTION}")
    print(f"Make sure BEEG_USER_ID ({BEEG_USER_ID}) is correct!")
    
    # Check which files exist
    phrases_exist = os.path.exists('beeg_summoning_phrases.csv')
    haikus_exist = os.path.exists('beeg_summoning_haikus.csv')
    
    if not phrases_exist and not haikus_exist:
        print("❌ No CSV files found! Make sure the files are in the same directory.")
        return
    
    print(f"\n📁 Files found:")
    if phrases_exist:
        beeg_count_phrases = count_beeg_instances('beeg_summoning_phrases.csv')
        print(f"✅ beeg_summoning_phrases.csv ({beeg_count_phrases} messages contain 'Beeg')")
    if haikus_exist:
        beeg_count_haikus = count_beeg_instances('beeg_summoning_haikus.csv')
        print(f"✅ beeg_summoning_haikus.csv ({beeg_count_haikus} messages contain 'Beeg')")
    
    # Show preview
    if phrases_exist:
        preview_changes('beeg_summoning_phrases.csv')
    if haikus_exist:
        preview_changes('beeg_summoning_haikus.csv')
    
    # Confirm before proceeding
    print("\n⚠️  This will replace all instances of 'Beeg' with Discord mentions")
    print("📁 Backups will be created automatically")
    response = input("Continue? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Process files
    print("\n🔄 Processing files...")
    
    if phrases_exist:
        update_phrases()
    
    if haikus_exist:
        update_haikus()
    
    print("\n🎉 All done! 'Beeg' has been replaced with Discord mentions.")
    print("📁 Original files have been backed up with timestamps.")
    print("\n💡 Tip: You may need to restart your bot or reload the messages for changes to take effect.")
    print(f"🏷️  All instances of 'Beeg' are now {BEEG_MENTION} and will ping him!")

if __name__ == "__main__":
    main()