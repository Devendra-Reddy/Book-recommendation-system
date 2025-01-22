# ----------------------------------------------------------------
# ---------------- Book Recomendation ----------------------------
# ----------------------------------------------------------------

import math
import gc
from multiprocessing import Pool
from collections import defaultdict

def load_libsvm(filename):
    """
    Building a dictionary of dictionaries to store the users along with their books & ratings as key value pairs
    """
    user_data = defaultdict(dict)
    with open(filename, 'r') as f:
        for user_id, line in enumerate(f, start=1):
            ratings = line.strip().split()
            for rating in ratings:
                book_id, score = map(float, rating.split(':'))
                user_data[user_id][int(book_id)] = score
    return user_data

def build_book_dict(user_data):
    """
    Build a dictionary where each book maps to a list of (user, rating) tuples.
    """
    book_dict = defaultdict(list)
    for user_id, books in user_data.items():
        for book_id, rating in books.items():
            book_dict[book_id].append((user_id, rating))
    return book_dict

def calculate_cosine_similarity(user1_ratings, user2_ratings):
    """
    Calculate cosine similarity between two users based on their ratings.
    """
    magnitude_user1 = math.sqrt(sum(rating**2 for rating in user1_ratings.values()))
    magnitude_user2 = math.sqrt(sum(rating**2 for rating in user2_ratings.values()))
    if magnitude_user1 == 0 or magnitude_user2 == 0:
        return 0
    else:
        dot_product = sum(user1_ratings[book] * user2_ratings[book] for book in user1_ratings if book in user2_ratings)
    return dot_product / (magnitude_user1 * magnitude_user2)

def find_similar_users(user_id, user_data, book_dict, top_n=10):
    """
    Find the top N most similar users to the target user using the book dictionary.
    """
    
    # Identify Candidate Users who have read similar books to the target user (refering to the books dictionary for easy access)
    candidate_users = set()
    for book in user_data[user_id]:
        if book in book_dict:
            candidate_users.update(book_dict[book].keys())
    candidate_users.discard(user_id)
    
    # Calculate cosine similarity for each candidate user => user_id: similarity_score
    similarities = {}
    # Only proceed if candidate_users is not empty
    if candidate_users:
        for user in candidate_users:
            similarity = calculate_cosine_similarity(user_ratings, user_data[other_user])
            similarities[other_user] = similarity
    
    # Return top N similar users
    return sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_n]

def recommend_books(target_user, user_data, top_similar_users, top_n=5):
    """
    Recommend books for the target user based on top similar users.
    """
    
    # Retrieves the books the target user has already rated to avoid recommending them again
    target_ratings = user_data[target_user]
    
    candidate_books = defaultdict(float)
    similarity_sums = defaultdict(float)
    
    # Aggregate ratings for each book that the candidate (similar users) users have read
    for similar_user, similarity in top_similar_users:
        for book, rating in user_data[similar_user].items():
            if book not in target_ratings:  # Only consider books the target user hasn't rated
                candidate_books[book] += rating * similarity
                similarity_sums[book] += similarity
    
    # Calculate recommendation scores for each book that the target user will be potentially recommended and has not read the book himself
    recommendations = {
        book: candidate_books[book] / similarity_sums[book]
        for book in candidate_books if similarity_sums[book] > 0
    }
    
    # Return top N recommendations
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]

# function to generate recommendations and run the code
def generate_recommendations(user_data, output_file, top_n=5):
    """
    Generate recommendations for all users and save them to a file.
    """
    book_dict = build_book_dict(user_data)

    batch_buffer = []
    with open(output_file, 'w') as f:
        for user_id in user_data.keys():
            top_similar_users = find_similar_users(user_id, user_data, book_dict)
            recommendations = recommend_books(user_id, user_data, top_similar_users, top_n)
            recommendation_str = ', '.join(f'BookID:{book}, Score:{score:.2f}' for book, score in recommendations)
            f.write(f'UserID:{user_id} -> {recommendation_str}\n')
                        # Add to batch buffer
            batch_buffer.append(f'UserID:{user_id} -> {recommendation_str}\n')
            
            # Write to file when batch is full
            if (idx + 1) % batch_size == 0:
                f.writelines(batch_buffer)
                batch_buffer = []  # Clear the buffer
    del book_dict  # Remove book_dict from memory
    del user_data
    gc.collect()   # Force garbage collection


user_data = load_libsvm('ratings.libsvm')
generate_recommendations(user_data, 'recommendations.csv')

