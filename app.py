#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
from bottle import get, post, run, request, template, redirect, response, url
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from functools import wraps
from vizualizacije import plotly1_html, df_c
import os

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

def include_file(filename):
    return bottle.static_file(filename, root='./views')

bottle.SimpleTemplate.defaults["include_file"] = include_file


repo = Repo()
auth = AuthService(repo)

def cookie_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie = request.get_cookie("vloga")
        if cookie:
            return f(*args, **kwargs)
        return template("vloga.html", url=url, napaka="Za ogled vizualizacij si moraš izbrati vlogo!", vloga=cookie, df_c = df_c)
    return decorated

@get('/')
@cookie_required
def index():
    vloga = request.get_cookie("vloga")
    plotly1 = plotly1_html
    return template('predstavitev_vizualizacij.html', url=url, vloga=vloga, plotly1 = plotly1, df_c = df_c)

@get('/vloga')
def prijava_get():
    return template("vloga.html", url=url, napaka=None, vloga=None, df_c = df_c)


@post('/vloga', name='vloga')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Vsak uporabnik si lahko izbere eno izmed sledečih vlog: novinec, entuziast, eskpert.
    Če je prijava vloge uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je prijava vloge neuspešna.
    """
    vloga = request.forms.get('vloga')

    if not auth.obstaja_vloga(vloga):
        return template("vloga.html", napaka="Vloga s tem imenom ne obstaja", vloga=vloga, url=url, df_c = df_c)

    response.set_cookie("vloga", vloga)
    redirect(url('/'))


@get('/odjava', name='odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi vlogi.
    """
    response.delete_cookie("vloga")
    return template('vloga.html', napaka=None, url=url, vloga=None, df_c = df_c)

@post('/') #, name='predstavitev_vizualizacij')
def izbira_drzave():
    # selected_options = request.forms.getall("country-filter")
    selected_options = request.forms.getall("country_filter")
    print("izbiranje države...")
    print(selected_options)
    # print(selected_options)
    nastavi_drzavo(drzava=selected_options)
    print(request.get_cookie("drzava"))
    redirect(url('/'))

def nastavi_drzavo(drzava="Vse"):
    staro = request.get_cookie("drzava")
    if drzava is None:
        response.delete_cookie("drzava")
    else:
        response.set_cookie("drzava", ",".join(drzava))
    return staro

@get('/test_graph', name="test_graph")
def test_graph():
    return template(r'graphs/red_cards.html')

if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
