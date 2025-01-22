# Book Recommendation System

## Overview

This repository contains a Python-based book recommendation system developed between October 2022 and January 2025. The system utilizes collaborative filtering and cosine similarity to provide personalized book recommendations for a large-scale dataset of over 100,000 users and 340,000 books.

## Key Features

- **Collaborative Filtering**: Implements user-based collaborative filtering to generate recommendations based on user preferences and behavior.
- **Cosine Similarity**: Utilizes cosine similarity to measure the similarity between users and books.
- **Sparse Matrix**: Efficiently handles large-scale data using a sparse matrix representation.
- **Optimized Performance**: Implements precomputed user norms and weighted ratings to improve computational efficiency.
- **Scalability**: Capable of generating over 275,000 personalized book suggestions.

## Installation

```bash
git clone https://github.com/yourusername/book-recommendation-system.git
cd book-recommendation-system
pip install -r requirements.txt
```

## Usage

```python
from recommender import BookRecommender

# Initialize the recommender
recommender = BookRecommender()

# Load data
recommender.load_data('path/to/user_data.csv', 'path/to/book_data.csv')

# Get recommendations for a user
user_id = 12345
recommendations = recommender.get_recommendations(user_id, top_n=10)

print(recommendations)
```

## Data

The system is designed to work with a dataset containing:
- 100,000+ users
- 340,000+ books
- User ratings and interactions

Ensure your data is in the correct format before using the system.

## Performance

- Generates 275,000+ personalized book suggestions
- Improved computational efficiency through optimization techniques

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
