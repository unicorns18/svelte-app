import json
import os
import sys
import time
sys.path.append(os.path.expanduser('~/plex-stuff/'))
from orionoid import *
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['search_history_db']
collection = db['search_history']

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
# TODO: make QUALITIES_SETS configurable via the UI (unicorns)
QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    print("data: %s (/search)" % data)
    search_term = data.get('search_term')

    if not search_term.strip():
        return jsonify({'error': 'Search term cannot be empty'}), 400

    existing_search = collection.find_one({ 'search_term': search_term })
    if existing_search:
        results = existing_search['results']
        print("Using cached results for search term: %s (/search)" % search_term)
    else:
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params={
                'api_key': 'cea9c08287d26a002386e865744fafc8',
                'query': search_term
            }
        )

        if response.status_code != 200:
            return jsonify({'error': 'An error occurred while searching'}), 500
        
        results = response.json().get('results', [])

        # TODO: Change this value or make it customizable via the UI
        if collection.count_documents({}) > 10:
            oldest_document = collection.find().sort('timestamp', 1).limit(1)[0]
            collection.delete_one({ '_id': oldest_document['_id'] })

        collection.insert_one({ 'search_term': search_term, 'results': results, 'timestamp': time.time() })

    return jsonify(results)

@app.route('/retrieve_search_history', methods=['GET'])
def retrieve_search_history():
    search_history = list(collection.find({}))

    for item in search_history:
        item['_id'] = str(item['_id'])

    return jsonify(search_history)

@app.route('/select', methods=['POST'])
def select():
    data = request.get_json()
    print("data: %s (/select)" % data)
    title = data.get('title', None)
    id = data.get('id', None)

    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}')

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch details from TMDB'}), 500

    details = response.json()

    imdb_id = details.get('imdb_id', None)

    print("response: {'title': %s, 'imdb_id': %s} (/select)" % (title, imdb_id))
    return jsonify({'title': title, 'imdb_id': imdb_id})

@app.route('/search_for_title', methods=['POST'])
def search_for_title():
    data = request.get_json()
    print("data: %s (/search_for_title)" % data)
    imdb_id = data.get('imdb_id')

    if imdb_id:
        search_best_qualities(imdb_id, QUALITIES_SETS, FILENAME_PREFIX)

        results_dir = os.path.join(os.getcwd(), 'results')
        result_files = []
        start_time = time.time()
        while not result_files and time.time() - start_time < 60:  # wait up to 60 seconds
            result_files = [f for f in os.listdir(results_dir) if f.startswith(imdb_id)]
            time.sleep(1)  # wait a second before checking again

        results = []
        for result in result_files:
            with open(os.path.join(results_dir, result), 'r') as f:
                results.extend(json.load(f))  # use extend instead of append if the files contain lists

        filtered_results = [result for result in results if not result.get('has_excluded_extension', False)]
        sorted_results = sorted(filtered_results, key=lambda r: r.get('score', 0), reverse=True)

        print("Results: %s (/search_for_title)" % sorted_results)

        return jsonify(sorted_results)
    else:
        return jsonify({'error': 'No IMDb ID provided'}), 500

if __name__ == '__main__':
    app.run(debug=True)