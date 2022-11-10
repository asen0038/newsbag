from gensim.models import KeyedVectors
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseTermSimilarityMatrix, WordEmbeddingSimilarityIndex


def load_data():
    trained_model = KeyedVectors.load("newsbag_app/utils/trained_model", mmap='r')
    return trained_model


def getStopWordsList():
    stopwords = []
    with open("newsbag_app/utils/english", "r") as f:
        stopwords = f.read().split()
    return stopwords


def preprocess(sentence):
    return [w for w in sentence.lower().split() if w not in getStopWordsList()]


def constructMatrix(corpus):
    processed_corpus = []
    for docs in corpus:
        doc = preprocess(docs)
        processed_corpus.append(doc)

    dictionary = Dictionary(processed_corpus)
    semi_model_docs = []
    for docs in processed_corpus:
        mod = dictionary.doc2bow(docs)
        semi_model_docs.append(mod)

    tfidf = TfidfModel(semi_model_docs)
    model_docs = []
    for docs in semi_model_docs:
        doc = tfidf[docs]
        model_docs.append(doc)

    model = load_data()
    termsim_index = WordEmbeddingSimilarityIndex(model)
    termsim_matrix = SparseTermSimilarityMatrix(termsim_index, dictionary, tfidf)

    result = [model_docs, termsim_matrix]

    return result
