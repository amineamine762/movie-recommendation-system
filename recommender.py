import pickle

new_df = pickle.load(open("artifacts/new_df.pkl", "rb"))
similarity = pickle.load(open("artifacts/similarity.pkl", "rb"))

def recommend(movie):
    if movie not in new_df['title'].values:
        return "Movie not found"

    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    for i in movies_list:
        recommended_movies.append(new_df.iloc[i[0]].title)

    return recommended_movies

