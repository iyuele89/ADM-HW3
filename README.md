# Assignment 3  Book Recommendation

- The goal of the assignment is to build a book recommendation engine that based on the input query, which Simply describe the kind of book we are looking for by specifying book title, author, etc.. and the search engine returns similar 'likes' pulled from the best books ever list of GoodReads.

## Data collection
- To this end we have to build our own dataset and the search engine have to run on text documents
  - Get the list of books
  - Crawl books
  - Parse downloaded pages

## Search Engine
Create two different Search Engines that, given a query, it pulls a list of books that match the query. For this purpose, nltk library is used
- Conjunctive query
- Conjunctive query & Ranking score

## Define a new score
-  Build a new metric to rank books based on the queries of the users using a scoring function
- The output, must contain:
  -	bookTitle
  - Plot
  - Url
  - The similarity score of the documents with respect to the query

## Make a nice visualization (Bonus)
- Here the goal is to quantify and visualize the writers' production.

## Algorithmic Question
- Given a string written in English capital letters, find the maximum length of a subsequence of characters that is in alphabetical order.

## Script descriptions
- ADM-HW3.ipynb
  - Jupyter notebook script that contains the solutions to the given assignment 
