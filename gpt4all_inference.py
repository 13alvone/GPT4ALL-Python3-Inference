#!/usr/bin/env python3

import sys
import time
import logging
import argparse
import sqlite3
from datetime import datetime
from io import StringIO
from gpt4all import GPT4All

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Global constant for maximum tokens
_max_tokens = 1000


# Database setup
def setup_database(db_name=None):
    if not db_name:
        epoch_week = int(time.time()) // 604800 * 604800  # Weekly epoch timestamp
        db_name = f"{epoch_week}_gpt4all_responses.db"
    _conn = sqlite3.connect(db_name)
    cursor = _conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_time TEXT,
            model_id INTEGER,
            model_name TEXT,
            response TEXT,
            pure_query TEXT UNIQUE,
            pure_response TEXT UNIQUE
        )
    ''')
    _conn.commit()
    return _conn


# Function to save response to database
def save_response_to_db(_conn, query_time, model_id, model_name, response, pure_query, pure_response):
    cursor = _conn.cursor()
    cursor.execute('''
        INSERT INTO responses (query_time, model_id, model_name, response, pure_query, pure_response)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (query_time, model_id, model_name, response, pure_query, pure_response))
    _conn.commit()


models = {  # Defaults to 1, if not provided.
    1: {
        "model": "mistral-7b-openorca.Q4_0.gguf",
        "data": {
            "SIZE": "3.83 GB",
            "RAM": "8 GB",
            "Description": "Best overall fast chat model",
            "Features": [
                "Fast responses",
                "Chat based model",
                "Trained by Mistral AI",
                "Finetuned on OpenOrca dataset curated via Nomic Atlas",
                "Licensed for commercial use"
            ]
        }
    },
    2: {
        "model": "mistral-7b-instruct-v0.1.Q4_0.gguf",
        "data": {
            "SIZE": "3.83 GB",
            "RAM": "8 GB",
            "SPEAKES_RATING": "9/10 (2 Reviews)",
            "Description": "Best overall fast instruction following model",
            "Features": [
                "Fast responses",
                "Trained by Mistral AI",
                "Uncensored",
                "Licensed for commercial use"
            ]
        }
    },
    3: {
        "model": "gpt4all-falcon-q4_0.gguf",
        "data": {
            "SIZE": "3.92 GB",
            "RAM": "8 GB",
            "Description": "Very fast model with good quality",
            "Features": [
                "Fastest responses",
                "Instruction based",
                "Trained by TII",
                "Finetuned by Nomic AI",
                "Licensed for commercial use"
            ]
        }
    },
    4: {
        "model": "orca-2-7b.Q4_0.gguf",
        "data": {
            "SIZE": "3.56 GB",
            "RAM": "8 GB",
            "Description": "Instruction based",
            "Features": [
                "Trained by Microsoft",
                "Cannot be used commercially"
            ]
        }
    },
    5: {
        "model": "orca-2-13b.Q4_0.gguf",
        "data": {
            "SIZE": "6.86 GB",
            "RAM": "16 GB",
            "Description": "Instruction based",
            "Features": [
                "Trained by Microsoft",
                "Cannot be used commercially"
            ]
        }
    },
    6: {
        "model": "wizardlm-13b-v1.2.Q4_0.gguf",
        "data": {
            "SIZE": "6.86 GB",
            "RAM": "16 GB",
            "Description": "Best overall larger model",
            "Features": [
                "Instruction based",
                "Gives very long responses",
                "Finetuned with only 1k of high-quality data",
                "Trained by Microsoft and Peking University",
                "Cannot be used commercially"
            ]
        }
    },
    7: {
        "model": "nous-hermes-llama2-13b.Q4_0.gguf",
        "data": {
            "SIZE": "6.86 GB",
            "RAM": "16 GB",
            "Description": "Extremely good model",
            "Features": [
                "Instruction based",
                "Gives long responses",
                "Curated with 300,000 uncensored instructions",
                "Trained by Nous Research",
                "Cannot be used commercially"
            ]
        }
    },
    8: {
        "model": "gpt4all-13b-snoozy-q4_0.gguf",
        "data": {
            "SIZE": "6.86 GB",
            "RAM": "16 GB",
            "Description": "Very good overall model",
            "Features": [
                "Instruction based",
                "Based on the same dataset as Groovy",
                "Slower than Groovy, with higher quality responses",
                "Trained by Nomic AI",
                "Cannot be used commercially"
            ]
        }
    },
    9: {
        "model": "mpt-7b-chat-merges-q4_0.gguf",
        "data": {
            "SIZE": "3.54 GB",
            "RAM": "8 GB",
            "Description": "Good model with novel architecture",
            "Features": [
                "Fast responses",
                "Chat based",
                "Trained by Mosaic ML",
                "Cannot be used commercially"
            ]
        }
    },
    10: {
        "model": "orca-mini-3b-gguf2-q4_0.gguf",
        "data": {
            "SIZE": "1.84 GB",
            "RAM": "4 GB",
            "Description": "Small version of new model with novel dataset",
            "Features": [
                "Instruction based",
                "Explain tuned datasets",
                "Orca Research Paper dataset construction approaches",
                "Cannot be used commercially"
            ]
        }
    },
    11: {
        "model": "replit-code-v1_5-3b-q4_0.gguf",
        "data": {
            "SIZE": "8.37 GB",
            "RAM": "4 GB",
            "Description": "Trained on subset of the Stack",
            "Features": [
                "Code completion based",
                "Licensed for commercial use",
                "WARNING: Not available for chat GUI"
            ]
        }
    },
    12: {
        "model": "starcoder-q4_0.gguf",
        "data": {
            "SIZE": "3.56 GB",
            "RAM": "8 GB",
            "Description": "Trained on subset of the Stack",
            "Features": [
                "Code completion based",
                "WARNING: Not available for chat GUI"
            ]
        }
    },
    13: {
        "model": "rift-coder-v0-7b-q4_0.gguf",
        "data": {
            "SIZE": "0.04 GB",
            "RAM": "1 GB",
            "Description": "Trained on collection of Python and TypeScript",
            "Features": [
                "Code completion based",
                "WARNING: Not available for chat GUI"
            ]
        }
    },
    14: {
        "model": "all-MiniLM-L6-v2-f16.gguf",
        "data": {
            "SIZE": "0.04 GB",
            "RAM": "1 GB",
            "Description": "LocalDocs text embeddings model",
            "Features": [
                "Necessary for LocalDocs feature",
                "Used for retrieval augmented generation (RAG)"
            ]
        }
    },
    15: {
        "model": "em_german_mistral_v01.Q4_0.gguf",
        "data": {
            "SIZE": "3.83 GB",
            "RAM": "8 GB",
            "Description": "Mistral-based model for German-language applications",
            "Features": [
                "Fast responses",
                "Chat based model",
                "Trained by ellamind",
                "Finetuned on German instruction and chat data",
                "Licensed for commercial use"
            ]
        }
    }
}


def get_args():
    parser = argparse.ArgumentParser(description='GPT4All Query Tool')
    parser.add_argument('-q', '--query', help='Query to Infer', type=str, required=True)
    parser.add_argument('-t', '--tokens', help='Max Tokens for return.', type=int, default=300)
    parser.add_argument('-m', '--model_id', help='ID of the target model.', type=int, choices=models.keys(),
                        required=False, default=2)
    parser.add_argument('-o', '--output', help='Output file.', type=str, default='output.log')
    return parser.parse_args()


def print_model_options():
    logging.info("[i] Available Models:")
    for model_id, model_info in models.items():
        print(f"[i] ID: {model_id} - Model: {model_info['model']}")


def print_elapsed_time(start_time):
    try:
        elapsed_seconds = round(time.time() - start_time, 2)
        minutes, remaining_seconds = divmod(elapsed_seconds, 60)
        print(f"[i] Time Elapsed: `{int(minutes):02d}:{int(remaining_seconds):02d}`")
    except TypeError:
        print("[x] Invalid start time provided.")


def gpt4all_response(query, model_id, verbose_query=True, verbose_response=True, max_tokens=_max_tokens):
    target_model = models[model_id]
    if verbose_query:
        features = '\n  * '.join(target_model['data']['Features'])
        print(f"[-] Model: {target_model['model']}\n[-] Features:\n  * {features}\n[-] Query: {query}\n---")
    model = GPT4All(target_model['model'])
    output = model.generate(query, max_tokens=max_tokens).strip()
    if verbose_response:
        print(f"[+] Response:\n{output}\n---")
    return output


def gpt4all_query(_conn, query, model_id, max_tokens=300, verbose=True, verbose_response_only=False, save_to_db=True):
    program_start_time = time.time()
    _time = datetime.fromtimestamp(program_start_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[+] Query Start Time: {_time}\n[-] Max Response Tokens: {max_tokens}")

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()

    if verbose:
        if verbose_response_only:
            response = gpt4all_response(query, model_id, max_tokens=max_tokens, verbose_query=False)
        else:
            response = gpt4all_response(query, model_id, max_tokens=max_tokens)
    else:
        response = gpt4all_response(query, model_id, max_tokens=max_tokens, verbose_query=False, verbose_response=False)

    if save_to_db and response:
        response = f"[!] BLANK RESPONSE TO QUERY: {query}" if response == "" else response
        # Save to database
        save_response_to_db(_conn, _time, model_id, models[model_id]["model"], buffer.getvalue(), query, response)

    # Reset stdout
    sys.stdout = old_stdout
    print(buffer.getvalue())

    print_elapsed_time(program_start_time)
    return response


if __name__ == "__main__":
    args = get_args()
    conn = setup_database()
    print_model_options()
    gpt4all_query(conn, args.query, args.model_id, max_tokens=args.tokens)
    conn.close()
    
