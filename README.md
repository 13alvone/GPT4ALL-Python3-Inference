# README for GPT4All Query Tool

## Overview
This Python script is a command-line tool that acts as a wrapper around the `gpt4all-bindings` library. It is designed for querying different GPT-based models, capturing responses, and storing them in a SQLite database. The tool supports a variety of models with different features, making it versatile for various query types.

## Features
- Supports multiple GPT-based models with detailed descriptions and features.
- Allows specifying query, max tokens, model ID, and output file via command line arguments.
- Stores query responses in a SQLite database with a weekly epoch timestamp.
- Provides verbose options for detailed query and response logs.
- Includes logging for better tracking and debugging.

## Requirements
- Python 3
- `gpt4all` Python package
- `sqlite3` module for database operations

## Installation
Ensure you have Python 3 installed. Then install the `gpt4all` package using pip:
	pip install gpt4all

## Usage
Run the script from the command line, specifying the required arguments.

### Basic Command
	python gpt4all_query_tool.py -q "Your query here" -m [model_id]
	-q, --query: Query to infer (required).
	-m, --model_id: ID of the target model (optional, defaults to 2).
	-t, --tokens: Max tokens for return (optional, defaults to 300).
	-o, --output: Output file (optional, defaults to 'output.log').

### Model IDs
Use the following IDs for different models. These models match those available at https://gpt4all.io/index.html (Thank You GPT4ALL!):
- ID 1: Fast chat model
- ID 2: Fast instruction following model
- ...
- ID 15: German-language model

## Database
Responses are stored in a SQLite database named with a weekly epoch timestamp. The schema includes `id`, `query_time`, `model_id`, `model_name`, and `response`.

## Logging
Logs are generated for informational purposes, including available models, query start times, and elapsed times.

## Note
This tool is a wrapper around `gpt4all-bindings` and leverages its functionalities. It is important to adhere to the usage guidelines and licensing terms of the models and the `gpt4all` library.
