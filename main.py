from typing import Any, Dict, Iterable
from alldebrid import APIError, AllDebrid
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from flask_cors import CORS
from flask import Flask, request, jsonify
import json
import os
import sys
import time
sys.path.append(os.path.expanduser('~/plex-stuff/'))

load_dotenv()

SEARCH_METHOD = os.getenv('SEARCH_METHOD')  # 'ip' or 'local'
# TODO: make QUALITIES_SETS configurable via the UI (unicorns)
QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"

if SEARCH_METHOD != 'local':
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    db_name = os.getenv('MONGO_DB', 'search_history_db')
    collection_name = os.getenv('MONGO_COLLECTION', 'search_history')
    db = client[db_name]
    collection = db[collection_name]
    # print("db: %s, collection: %s" % (db, collection))

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# TODO: Remove process_magnet and replace it a server call
ad = AllDebrid(apikey=os.getenv('ALLDEBRID_API_KEY'))

def process_magnet(magnet: str) -> None:
    """
    Process a magnet link, check if it's instant, upload it, and save uptobox.com torrent links.

    :param magnet: The magnet link to process.
    """

    def save_link(link: str) -> None:
        """
        Save a link using the ad module.

        :param link: The link to save.
        """
        if not link or not isinstance(link, str):
            print(f"Invalid link: {link}")
            return

        try:
            res_saved_links: Dict[str, Any] = ad.save_new_link(link=link)
            if res_saved_links['status'] == 'success':
                print(f"Saved link: {link}")
            else:
                print(f"Error saving link: {link}")
        except APIError as exc:
            print(f"Error saving link: {link}: {exc}")
        except ValueError as exc:
            print(f"Error saving link: {link}: {exc}")
        except Exception as exc:
            print(f"Error saving link: {link}: {exc}")

    def filter_uptobox_links(magnet_links: List[Dict[str, str]]) -> Iterable[str]:
        """
        Filter uptobox.com links from a list of magnet links.

        :param magnet_links: A list of magnet link dictionaries.
        :return: A generator yielding uptobox.com links.
        """
        if not isinstance(magnet_links, list):
            raise ValueError("The magnet_links argument must be a list.")

        for link in magnet_links:
            if not isinstance(link, dict):
                raise ValueError(
                    "Each item in magnet_links must be a dictionary.")
            elif 'link' not in link:
                raise ValueError(
                    "Each dictionary in magnet_links must contain a 'link' key.")
            elif not isinstance(link['link'], str):
                raise ValueError(
                    "The 'link' value in the dictionaries in magnet_links must be a string.")
            elif 'uptobox.com' in link['link']:
                yield link['link']

    start_time = time.perf_counter()

    # Check if the provided magnet is in the URL format
    if magnet.startswith('http'):
        try:
            magnet = ad.download_file_then_upload_to_alldebrid(magnet)
            print(f"Magnet: {magnet}")
        except (ValueError, APIError) as exc:
            print(f"Error downloading and uploading file to AllDebrid: {exc}")
            return

    try:
        res: Dict[str, Any] = ad.check_magnet_instant(magnet)
        instant: bool = res['data']['magnets'][0]['instant']
    except (ValueError, APIError) as exc:
        print(f"Error checking magnet instant: {exc}")
        return

    if instant:
        try:
            res_upload: Dict[str, Any] = ad.upload_magnets(magnet)
            upload_id: str = res_upload['data']['magnets'][0]['id']
            res_status: Dict[str, Any] = ad.get_magnet_status(upload_id)
            torrent_links: Iterable[str] = filter_uptobox_links(
                res_status['data']['magnets']['links'])
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet or getting status: {exc}")
            return

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(save_link, link)
                           for link in torrent_links}
                for _ in concurrent.futures.as_completed(futures):
                    pass
        except (ValueError, APIError) as exc:
            print(f"Error processing torrent links: {exc}")
            return
    else:
        try:
            res_upload = ad.upload_magnets(magnet)
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet: {exc}")
            return

    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time - start_time:0.4f} seconds")

@app.route('/upload_to_debrid', methods=['POST'])
def upload_to_debrid():
    magnet = request.args.get('magnet')

    if not magnet:
        return jsonify({'error': 'Magnet is required'}), 400
    
    process_magnet(magnet)

    return jsonify({'success': 'Magnet added to debrid!'})

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    print("data: %s (/search)" % data)
    search_term = data.get('search_term')

    if not search_term.strip():
        return jsonify({'error': 'Search term cannot be empty'}), 400

    if SEARCH_METHOD != 'local':
        existing_search = collection.find_one({'search_term': search_term})
    else:
        existing_search = False

    if existing_search:
        results = existing_search['results']
        print("Using cached results for search term: %s (/search)" % search_term)
    else:
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params={
                'api_key': TMDB_API_KEY,
                'query': search_term
            }
        )

        if response.status_code != 200:
            return jsonify({'error': 'An error occurred while searching'}), 500

        results = response.json().get('results', [])

        # TODO: Change this value or make it customizable via the UI
        if SEARCH_METHOD != 'local':
            if collection.count_documents({}) > 10:
                oldest_document = collection.find().sort(
                    'timestamp', 1).limit(1)[0]
                collection.delete_one({'_id': oldest_document['_id']})
            collection.insert_one(
                {'search_term': search_term, 'results': results, 'timestamp': time.time()})

    return jsonify(results)


@app.route('/retrieve_search_history', methods=['GET'])
def retrieve_search_history():
    search_history = list(collection.find({}).sort([('timestamp', -1)]))

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

    print(
        "response: {'title': %s, 'imdb_id': %s} (/select)" % (title, imdb_id))
    return jsonify({'title': title, 'imdb_id': imdb_id})




@app.route('/search_for_title', methods=['POST'])
def search_for_title():
    data = request.get_json()
    print("data: %s (/search_for_title)" % data)
    imdb_id = data.get('imdb_id')

    if imdb_id:
        if SEARCH_METHOD == 'ip':
            headers = {
                'apikey': os.getenv('API_KEY')
            }
            response = requests.post(
                f'http://206.81.16.199:1337/search_id?imdb_id={imdb_id}', headers=headers)
            if response.status_code == 200:
                results = response.json()
                filtered_results = [result for result in results if not result.get(
                    'has_excluded_extension', False)]
                sorted_results = sorted(
                    filtered_results, key=lambda r: r.get('score', 0), reverse=True)
                return jsonify(sorted_results)
            else:
                return jsonify({'error': 'Request to external server failed'}), 500
        else:
            # Use the local search method
            search_best_qualities(imdb_id, QUALITIES_SETS, FILENAME_PREFIX)

            results_dir = os.path.join(os.getcwd(), 'results')
            result_files = []
            start_time = time.time()
            while not result_files and time.time() - start_time < 60:  # wait up to 60 seconds
                result_files = [f for f in os.listdir(
                    results_dir) if f.startswith(imdb_id)]
                time.sleep(1)  # wait a second before checking again

            results = []
            for result in result_files:
                with open(os.path.join(results_dir, result), 'r') as f:
                    # use extend instead of append if the files contain lists
                    results.extend(json.load(f))

        filtered_results = [result for result in results if not result.get(
            'has_excluded_extension', False)]
        sorted_results = sorted(
            filtered_results, key=lambda r: r.get('score', 0), reverse=True)

        print("Results: %s (/search_for_title)" % sorted_results)

        return jsonify(sorted_results)
    else:
        return jsonify({'error': 'No IMDb ID provided'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=6942)
