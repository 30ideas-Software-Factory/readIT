#!/usr/bin/python3
""" Flask Web Application """
from flask import Blueprint, render_template, request, redirect, url_for, flash
from engine import storage
from flask_login import login_required, current_user
from models.books import Book
import requests
main = Blueprint('main', __name__)


@main.route('/index')
@main.route('/')
def index():
    """ Methods for Index """
    return render_template('index.html')

@main.route('/about')
def about():
    """ Methods for about """
    return render_template('about.html')

@main.route('/profile')
@login_required
def profile():
    """ Methods for profile """
    return render_template('profile.html', name=current_user.FirstName)

@main.route('/postBook', methods=['GET', 'POST'])
@login_required
def postBook():
    if request.method == 'GET':
        return render_template('postBook.html')
    if request.method == 'POST':
        ISBN = request.form.get('ISBN')
        google = apiGoogle(ISBN)
        openl = apiOpenl(ISBN)

        # Create new Dict merging GoogleApi and openLibrary 
        newDict = {}
        print(google)
        if google != None:
            if google.get('Title'):
                newDict['Title'] = google.get('Title')
            else:
                newDict['Title'] = openl.get('Title')
            if google.get('Authors'):
                newDict['Authors'] = google.get('Authors')
            else:
                newDict['Authors'] = openl.get('Authors')
            if google.get('Description'): 
                newDict['Description'] = google.get('Description')
            else:
                newDict['Description'] = openl.get('Description')
        elif openl != None:
            newDict['Title'] = openl.get('Title')
            newDict['Authors'] = openl.get('Authors')
            newDict['Description'] = openl.get('Description')
        else:
            alert = "Try again or introduce a valid ISBN"
            return render_template('postBook.html', alertIsbn=alert)
        print("Pasé todos los if")
        newDict['Status'] = 'Available'
        newDict['Cover'] = openl.get('Cover')
        newDict['ISBN'] = ISBN
        newBook = Book(**newDict)
        storage.new(newBook)
        storage.save()
        print(newBook)
        return render_template('postBook.html', alertIsbn="Your book has been successfully registered")
    
@main.route('/books')
def books():
    """Get method to show all books"""
    books = storage.all(Book).values()
    books = sorted(books, key=lambda k: k.Title)
    return render_template('books.html', books=books)


@main.route('/idBook')
@main.route('/idBook/<BookId>')
def thisBook(BookId=None):
    """Get method for idBook"""
    IdBook = "Book." + BookId
    books = storage.all(Book)
    book = books.get(IdBook)
    return render_template('idBook.html', book=book)

@main.route('/available_books')
@main.route('/available_books/<Title>')
def availableBooks(Title=None):
    """Get method for availableBooks"""
    books = storage.all(Book)
    booksAvailable = {}
    print(books)
    for book in books:
        print(books.get(book))
    return "Available books"

def apiGoogle(ISBN):
    """ Get info from Google API """
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    url= 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'
    r = requests.get(url.format(ISBN), allow_redirects=False, headers=header)
    if r.json().get('totalItems') > 0:
        Title = r.json().get('items')[0].get('volumeInfo').get('title')
        Authors = r.json().get('items')[0].get('volumeInfo').get('authors')[0]
        Description  = r.json().get('items')[0].get('volumeInfo').get('description')
    else:
        return None
    newDict = {'Title': Title, 'Authors': Authors, 'Description': Description}
    return newDict

def apiOpenl(ISBN):
    """ Get info from OpenLibrary API """
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    url = 'https://openlibrary.org/isbn/{}.json'
    try:
        r = requests.get(url.format(ISBN), allow_redirects=True, headers=header)
    except:
        print("no request")
        return None
    if r.status_code == 200:
        dic = r.json()
    else:
        return None
    if dic.get('title'):
        Title = dic.get('title')
    else:
        Title = "No title"
    if dic.get('authors'):
        allauthors = []
        authors = dic.get('authors')
        for author in authors:
            allauthors.append(author.get('key'))
        url2 = 'https://openlibrary.org{}.json'
        names = []
        for item in allauthors:
            r2 = requests.get(url2.format(item), headers=header).json()
            names.append(r2.get('name'))
        for name in names:
            if len(names) > 1 and name == names[-1]:
                Authors = '& {}'.format(name)
            elif len(names) > 1 and name == names[-2]:
                Authors = '{} '.format(name)
            elif len(names) == 1:
                Authors = name
            else:
                Authors = '{}, '.format(name)
    else:
        Authors = "No Authors found"
    if dic.get('description'):
        try:
            Description = dic.get('description').get('value')
        except:
            Description = dic.get('description')
    else:
        Description = "No description"    
                
    if dic.get('covers'):
        idCover = dic.get('covers')[0]
        Cover = 'https://covers.openlibrary.org/b/id/{}-M.jpg'.format(idCover)
    else:
        Cover = 'https://bit.ly/3wfAdaW'
    newDict = {'Title': Title, 'Authors': Authors, 'Description': Description, 'Cover': Cover}
    return newDict
