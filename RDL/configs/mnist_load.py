import numpy as np
from urllib import request
import os
import gzip
import pickle


def load_synth(num_train=60_000, num_val=10_000):
    """Load some very basic synthetic data that should be easy to classify. Two features, so that we can plot the
    decision boundary (which is an ellipse in the feature space).

    :param num_train: Number of training instances (Default value = 60_000)
    :param num_val: Number of test/validation instances (Default value = 10_000)
    :param num_features: Number of features per instance
    :returns: Two tuples (xtrain, ytrain), (xval, yval) the training data is a floating point numpy array:

    """

    THRESHOLD = 0.6
    quad = np.asarray([[1, 0.5], [1, 0.2]])

    ntotal = num_train + num_val

    x = np.random.randn(ntotal, 2)

    # compute the quadratic form
    q = np.einsum("bf, fk, bk -> b", x, quad, x)
    y = (q > THRESHOLD).astype(np.int)

    return (x[:num_train, :], y[:num_train]), (x[num_train:, :], y[num_train:]), 2


def load_mnist(final=False, flatten=True):
    """Load the MNIST data

    :param final: If true, return the canonical test/train split. If false, split some validation data from the training
       data and keep the test data hidden. (Default value = False)
    :param flatten: return: (Default value = True)

    """

    if not os.path.isfile("mnist.pkl"):
        init()

    xtrain, ytrain, xtest, ytest = load()
    xtl, xsl = xtrain.shape[0], xtest.shape[0]

    if flatten:
        xtrain = xtrain.reshape(xtl, -1)
        xtest = xtest.reshape(xsl, -1)

    if not final:  # return the flattened images
        return (xtrain[:-5000], ytrain[:-5000]), (xtrain[-5000:], ytrain[-5000:]), 10

    return (xtrain, ytrain), (xtest, ytest), 10


# Numpy-only MNIST loader. Courtesy of Hyeonseok Jung
# https://github.com/hsjeong5/MNIST-for-Numpy

filename = [
    ["training_images", "train-images-idx3-ubyte.gz"],
    ["test_images", "t10k-images-idx3-ubyte.gz"],
    ["training_labels", "train-labels-idx1-ubyte.gz"],
    ["test_labels", "t10k-labels-idx1-ubyte.gz"],
]


def download_mnist():
    """ """
    base_url = "http://yann.lecun.com/exdb/mnist/"
    for name in filename:
        print("Downloading " + name[1] + "...")
        request.urlretrieve(base_url + name[1], name[1])
    print("Download complete.")


def save_mnist():
    """ """
    mnist = {}
    for name in filename[:2]:
        with gzip.open(name[1], "rb") as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=16).reshape(
                -1, 28 * 28
            )
    for name in filename[-2:]:
        with gzip.open(name[1], "rb") as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=8)
    with open("mnist.pkl", "wb") as f:
        pickle.dump(mnist, f)
    print("Save complete.")


def init():
    """ """
    download_mnist()
    save_mnist()


def load():
    """ """
    with open("mnist.pkl", "rb") as f:
        mnist = pickle.load(f)
    return (
        mnist["training_images"],
        mnist["training_labels"],
        mnist["test_images"],
        mnist["test_labels"],
    )
