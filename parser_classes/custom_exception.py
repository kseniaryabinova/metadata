class DBException(Exception):
    def __init__(self, message):
        Exception.__init__(self, "redundant attribute in {}".format(message))


class KeyException(Exception):
    def __init__(self, message):
        Exception.__init__(self, "error in attributes: {} was expected".format(message))
