from hosts import seed
from request import do


if __name__ == "__main__":
    seed([
        "http://search.yahoo.com/",
        #"http://www.google.co.in",
        "http://amazon.com"
    ])

    do()
