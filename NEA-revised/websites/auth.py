from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify

from .models import User, Note, Scores

from werkzeug.security import generate_password_hash, check_password_hash

from . import db

from flask_login import login_user, login_required, logout_user, current_user

import json

from datetime import datetime

import sqlite3

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password, try again.', category='error')
        else:
            flash('Email does not exist', category='error')
    
    return render_template('login.html', user=current_user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exist', category='error')

        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) <2:
            flash('First name must be greater than 2 characters', category='error')
        elif password1 != password2:
            flash('Password don\'t match ', category='error')
        elif len(password1) < 7:
            flash('Password is too short, password must be greater than 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            
            login_user(user, remember=True)

            flash('Account successfully created', category='success')
            return redirect(url_for('views.home'))


    return render_template('sign_up.html', user=current_user)

@auth.route('/flashcard', methods=['GET', 'POST'])
@login_required
def flash_card():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('flashcard is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('flashcard added!', category='success')
    return render_template('notes.html', user=current_user)

@auth.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@auth.route('/paper2')
@login_required
def paper2():
    return render_template('paper2.html', user=current_user)

@auth.route('/2016paper2')
@login_required
def paper2_2016():
    return render_template('2016paper2.html', user=current_user)

@auth.route('/2016paper2MS', methods=['GET', 'POST'])
@login_required
def paper2MS_2016():
    if request.method == 'POST':
        mark = request.form.get('score')
        if len(mark) < 1:
            flash('Not a Valid Mark!', category='error')
        else:
            new_mark = Scores(Marks=mark, user_id=current_user.id)
            db.session.add(new_mark)
            db.session.commit()
            flash('Mark added!', category='success')
    return render_template('2016P2MS.html', user=current_user)

@auth.route('/2016analysis', methods=['GET', 'POST'])
@login_required
def graph_2016():
    database = sqlite3.connect('./instance/database.db')
    cur = database.cursor()
    statement = "SELECT Marks FROM scores "
    cur.execute(statement)
    rows =  [r[0] for r in cur]
    y_axes_2016 = []
    for row in rows:
        y_axes_2016.append(row)
    statement2 = "SELECT Time2016 FROM scores "
    cur.execute(statement2) 
    rows_time = [r1[0] for r1 in cur ]
    x_axes_2016 = []
    for row1 in rows_time:
         x_axes_2016.append(row1)

    return render_template('2016analysis.html', user=current_user,  y_axes_2016= y_axes_2016, x_axes_2016 = x_axes_2016)
    