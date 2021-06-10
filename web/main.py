#!/usr/bin/python3
""" Flask Web Application """
from flask import Blueprint, render_template, request, redirect, url_for, flash
from engine import storage
from flask_login import login_required, current_user
from models.books import Book
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
        return render_template('profile.html', name=current_user.FirstName)

@main.route('/postBook')
@login_required
def addBook():
    return render_template('postBook.html')

@main.route('/postBook', methods=['POST'])
@login_required
def postBook():
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
        alert = "ISBN Not Found"
        return render_template('postBook.html', alertIsbn=alert)
    newDict['Status'] = 'Available'
    newDict['Cover'] = openl.get('Cover')
    print (newDict)

    newBook = Book(**newDict)
    storage.new(newBook)
    storage.save()
    
    return render_template('postBook.html', alertIsbn="Your book has been successfully registered")
    
"""Get methods for Index"""
@main.route('/books')
def books():
    return "Books"

@main.route('/idbook')
def thisBook():
    return "This books"

@main.route('/available_books')
def availableBooks():
    return "Available books"

@main.route('/postbook')
@main.route('/postbook/<newBook>', methods=['POST'])
def NewBook():
    return "New Book"

@main.route('/about')
def about():
    return "About"

def apiGoogle(ISBN):
    # Get info from APIs
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

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    url = 'https://openlibrary.org/isbn/{}.json'
    r = requests.get(url.format(ISBN), allow_redirects=True, headers=header)
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
        Cover = 'https://covers.openlibrary.org/b/id/{}-L.jpg'.format(idCover)
    else:
        Cover = "No cover"
    newDict = {'Title': Title, 'Authors': Authors, 'Description': Description, 'Cover': Cover}
    return newDict

