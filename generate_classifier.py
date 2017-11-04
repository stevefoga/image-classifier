"""
generate_classifier.py

Purpose:

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 2.7.13

Source: http://www.ippatsuman.com/2014/08/13/day-and-night-an-image-classifier-
        with-scikit-learn/

...or...

https://web.archive.org/web/20160408173700/http://www.ippatsuman.com/2014/08/13/
day-and-night-an-image-classifier-with-scikit-learn/
"""


def generate_classifier(group_a, group_b, class_out, img_ext='.jpg'):
    """

    :param group_a: <str> path to 'good' images OR json files
    :param group_b: <str> path to 'bad' images OR json files
    :param class_out: <str> path and filename of output file
    :param img_ext: <str> image extension, e.g., '.jpg', '.png' (ignored if group_a and group_b are .json)
    :return:
    """

    import sys
    import os
    import glob
    import json
    import time
    from common import Common
    from sklearn import cross_validation
    from sklearn import svm
    from sklearn import grid_search
    from sklearn.externals import joblib
    import pickle

    def calc_img_vector(img_path):
        """

        :param img_path:
        :return:
        """
        return Common.process_image(Common.open_image(img_path))

    def train_classifier(train_a, train_b, class_out):
        """

        :param train_a: <list> feature vector of image A
        :param train_b: <list> feature vector of image B
        :param class_out: <str> path to output
        :return: <sklearn.grid_search.GridSearchCV> training model (also pickles to file)
        """
        # combine good and bad vectors
        data = train_a + train_b

        # allocate training classes for each image vector
        target = [1] * len(train_a) + [0] * len(train_b)

        # split training data in a train set and a test set.
        x_train, x_test, y_train, y_test = cross_validation.train_test_split(
            data,
            target,
            test_size=0.5)

        # define the parameter search space
        parameters = {'kernel': ['linear', 'rbf'],
                      'C': [1, 10, 100, 1000],
                      'gamma': [0.01, 0.001, 0.0001]}

        # search for the best classifier within the search space and return it
        clf = grid_search.GridSearchCV(svm.SVC(), parameters).fit(x_train,
                                                                  y_train)

        # write classifier parameters to file
        if clf:
            pickle.dump(clf, open(class_out, 'wb'))

        return clf

    def get_files(f_path, f_pattern):
        files = glob.glob(f_path + os.sep + '*' + f_pattern)

        if files:
            return files

        else:
            sys.exit("Could not find files in {0} using wildcard *{1}.".
                     format(f_path, f_pattern))

    def read_vector_file(vec_path):
        """

        :param vec_path:
        :return:
        """
        try:
            with open(vec_path) as f:
                output = json.load(f)

            print("Vector file {0} successfully read.".format(vec_path))

        except IOError:
            sys.exit("{0} could not be opened.".format(vec_path))

        return output

    def write_vector_file(vec_path, data):
        """

        :param vec_path:
        :param data:
        :return:
        """
        output = os.path.join(vec_path, 'image_vector_{0}.json'.format(time.strftime("%Y%m%d-%H%M%S")))

        try:
            with open(output, 'w') as f:
                json.dump(data, f)

            print("Vector data written to {0}".format(output))

        except IOError:
            sys.exit("Vector file could not be created.")

    # if the inputs are not JSON files, they are assumed to be images
    # generate vectors for all images
    ext_a = os.path.splitext(group_a[-1])
    ext_b = os.path.splitext(group_b[-1])

    if ext_a != '.json' and ext_b != '.json':
        vector_a = [calc_img_vector(i) for i in get_files(group_a, img_ext)]
        vector_b = [calc_img_vector(i) for i in get_files(group_b, img_ext)]

        # write vector files to disk
        write_vector_file(group_a, vector_a)
        write_vector_file(group_b, vector_b)

    elif ext_a == '.json' and ext_b == '.json':
        vector_a = read_vector_file(group_a)
        vector_b = read_vector_file(group_b)

    else:
        print("Incorrect extensions supplied. ext_a={0} | ext_b={1}".format(ext_a, ext_b))
        sys.exit(-1)

    # train the classifier for the image sets
    train_classifier(vector_a, vector_b, class_out)