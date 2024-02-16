import tensorflow as tf
import tensorflow_hub as hub
from sentence_transformers import SentenceTransformer
import pandas as pd
import umap
import hdbscan
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


# load intents dataset
data_sample = pd.read_json('cleaned_thread_titles_without_stopwords.json')
# data_sample = pd.read_json('cleaned_thread_titles.json')
all_intents = list(data_sample['text'])

print(len(all_intents))

# define the document embedding models to use for comparison
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model_use = hub.load(module_url)
model_st1 = SentenceTransformer('all-mpnet-base-v2')
model_st2 = SentenceTransformer('all-MiniLM-L6-v2')
model_st3 = SentenceTransformer('paraphrase-mpnet-base-v2')

def embed(model, model_type, sentences):
    """
    wrapper function for generating message embeddings
    """
    if model_type == 'use':
        embeddings = model(sentences)
    elif model_type == 'sentence transformer':
        embeddings = model.encode(sentences)

    return embeddings

def generate_clusters(message_embeddings,
                      n_neighbors,
                      n_components, 
                      min_cluster_size,
                      random_state = 42):
    """
    Generate HDBSCAN cluster object after reducing embedding dimensionality with UMAP
    """
    
    umap_embeddings = (umap.UMAP(n_neighbors=n_neighbors, 
                                n_components=n_components, 
                                metric='cosine', 
                                random_state=random_state)
                            .fit_transform(message_embeddings))

    clusters = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size,
                               metric='euclidean', 
                               cluster_selection_method='eom').fit(umap_embeddings)

    return clusters

def score_clusters(clusters, prob_threshold = 0.05):
    """
    Returns the label count and cost of a given cluster supplied from running hdbscan
    """
    
    cluster_labels = clusters.labels_
    label_count = len(np.unique(cluster_labels))
    total_num = len(clusters.labels_)
    cost = (np.count_nonzero(clusters.probabilities_ < prob_threshold)/total_num)
    
    return label_count, cost

# generate embeddings for each model
# embeddings_use = embed(model_use, 'use', all_intents)
# embeddings_st1 = embed(model_st1, 'sentence transformer', all_intents)
embeddings_st2 = embed(model_st2, 'sentence transformer', all_intents)
# embeddings_st3 = embed(model_st3, 'sentence transformer', all_intents)

print(embeddings_st2.shape)

embeddings_use = embeddings_st2 / np.linalg.norm(embeddings_st2, axis=1, keepdims=True)


clustering_model = KMeans(n_clusters=3)
clustering_model.fit(embeddings_st2)
cluster_assignment = clustering_model.labels_
# print(cluster_assignment)

# Assuming X is your data and kmeans.labels_ are the cluster labels
plt.scatter(embeddings_st2[:, 0], embeddings_st2[:, 1], c=clustering_model.labels_, cmap='rainbow')
plt.scatter(clustering_model.cluster_centers_[:, 0], clustering_model.cluster_centers_[:, 1], s=100, marker='X', c='black')
plt.title('K-means Clustering')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.savefig('cluster.png')

plt.show()

# clusters = generate_clusters(embeddings_use, 200, 5, 5)

# label_count, cost = score_clusters(clusters)
# print(label_count, cost )

