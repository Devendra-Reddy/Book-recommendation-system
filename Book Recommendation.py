
# ----------------------------------------------------------------------------------
# --------------------- Data Preparation -------------------------------------------
# ----------------------------------------------------------------------------------

import pandas as pd
from collections import defaultdict

# process  ratings dataset 
df = pd.read_csv('archive/Ratings.csv', sep=';', names=['UserID', 'ISBN', 'Rating'], skiprows=1)

# Create sequential ID mappings 
user_dict = {old: new+1 for new, old in enumerate(df['UserID'].unique())}
book_dict = {old: new+1 for new, old in enumerate(df['ISBN'].unique())}

# Store user ratings in  nested dictionary
ratings_dict = defaultdict(dict)

# Process each rating entry
for index, row in df.iterrows():
    mapped_user = user_dict[row['UserID']]
    mapped_book = book_dict[row['ISBN']]
    ratings_dict[mapped_user][mapped_book] = row['Rating']

# Generate output file
with open('ratings.libsvm', 'w') as output_file:
    for user in sorted(ratings_dict.keys()):
        # Format each rating as 'bookid:rating'
        formatted_ratings = [f'{book}:{rating}' for book, rating in sorted(ratings_dict[user].items())]
        # Write space-separated ratings for each user
        output_file.write(' '.join(formatted_ratings) + '\n')

print("created ratinsgs.libsvm")


# ----------------------------------------------------------------
# ----- Book Recomendation according to the required format-------
# ----------------------------------------------------------------


import math
from collections import defaultdict
from tqdm import tqdm

def load_data():
    """Load and preprocess data"""
    print("Loading books data...")
    # Create ISBN to title mapping from Books.csv
    isbn_to_title = {}
    book_id_to_isbn = {}
    
    with open('archive/Books.csv', 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for idx, line in enumerate(f, start=1):
            try:
                parts = line.strip().split(';')
                isbn = parts[0].strip()
                title = parts[1].strip()
                isbn_to_title[isbn] = title
                book_id_to_isbn[idx] = isbn
            except:
                continue

    print("Loading ratings from libsvm...")
    ratings_dict = defaultdict(dict)
    with open('ratings.libsvm', 'r') as f:
        for user_id, line in enumerate(f, start=1):
            ratings = line.strip().split()
            for rating in ratings:
                book_id, score = map(float, rating.split(':'))
                ratings_dict[user_id][int(book_id)] = score

    # Precompute user norms
    print("Computing user norms...")
    user_norms = {
        user: math.sqrt(sum(rating * rating for rating in ratings.values()))
        for user, ratings in ratings_dict.items()
        if sum(rating * rating for rating in ratings.values()) > 0
    }

    return ratings_dict, isbn_to_title, user_norms, book_id_to_isbn

def calculate_similarity(user1, user2, ratings_dict, user_norms):
    """Calculate cosine similarity between two users"""
    if user1 not in user_norms or user2 not in user_norms:
        return 0.0
    
    common_books = set(ratings_dict[user1].keys()) & set(ratings_dict[user2].keys())
    if not common_books:
        return 0.0
    
    dot_product = sum(ratings_dict[user1][book] * ratings_dict[user2][book] for book in common_books)
    denominator = user_norms[user1] * user_norms[user2]
    
    return dot_product / denominator if denominator > 0 else 0.0

def get_recommendations(target_user, ratings_dict, user_norms, k=10):
    """Get top 5 book recommendations"""
    similarities = []
    for other_user in ratings_dict:
        if other_user != target_user:
            sim = calculate_similarity(target_user, other_user, ratings_dict, user_norms)
            if sim > 0:
                similarities.append((other_user, sim))
    
    similar_users = sorted(similarities, key=lambda x: x[1], reverse=True)[:k]
    if not similar_users:
        return []
    
    user_books = set(ratings_dict[target_user].keys())
    recommendations = {}
    
    for similar_user, sim in similar_users:
        for book in ratings_dict[similar_user]:
            if book not in user_books:
                numerator = sum(ratings_dict[sim_user][book] * sim 
                              for sim_user, sim in similar_users 
                              if book in ratings_dict[sim_user])
                denominator = sum(sim for _, sim in similar_users)
                if denominator > 0:
                    recommendations[book] = numerator / denominator
    
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5]

def main():
    # Load data and precompute norms
    ratings_dict, isbn_to_title, user_norms, book_id_to_isbn = load_data()
    
    print("Generating recommendations...")
    total_users = len(ratings_dict)
    
    with open('recommendations.csv', 'w', encoding='utf-8', newline='') as f:
        f.write('User_ID,Book_ID,Book_Title,Recommendation_Score\n')
        for user in tqdm(ratings_dict.keys(), total=total_users, desc="Processing users"):
            recommendations = get_recommendations(user, ratings_dict, user_norms)
            for book_id, score in recommendations:
                # Get book title, use book_id as fallback if not found
                title = isbn_to_title.get(book_id_to_isbn.get(book_id, str(book_id)), f"Book_{book_id}")
                scaled_score = min(max(round(score * 2), 1), 10)
                f.write(f'{user},{book_id},"{title}",{scaled_score}\n')

    print("Recommendations generated successfully!")

main()


