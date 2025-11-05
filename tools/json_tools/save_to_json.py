from tools.json_tools.load_existing_data import load_existing_data
import json

def save_to_json(data, filename="matches_data.json"):
    """Сохраняет данные в JSON, добавляя к существующим"""
    existing_data = load_existing_data(filename)
    
    existing_urls = {match['url'] for match in existing_data.get('matches', [])}
    
    new_matches = []
    for match in data:
        if match['url'] not in existing_urls:
            new_matches.append(match)
            existing_urls.add(match['url'])
    
    existing_data['matches'].extend(new_matches)
    existing_data['matches_found'] = len(existing_data['matches'])
    
    if 'source_url' in data[0] if data else False:
        source_url = data[0]['source_url']
        if source_url not in existing_data.get('source_urls', []):
            existing_data.setdefault('source_urls', []).append(source_url)
    
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"Добавлено новых матчей: {len(new_matches)}")
    return len(new_matches)