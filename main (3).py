import os
import re
import base64
from requests import post, get
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv() #per major segurat i protecció dels tokens d'accés utilitzem un arxiu .env que és ocult i on podem emmagatzemar les claus de forma segura. 

def get_token(): ##Funció per obtenir el token d'autenticació
    auth_string: str = client_id + ":" + client_secret #generem la string d'autorització amb el clientid i clientsecret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8") #generem el codi d'autorització en base64

    url = "https://accounts.spotify.com/api/token" #enllaç bàsic de sol.licitud pel token
    headers = { #headers pel protocol https
        "Authorization": "Basic " + auth_base64, #definim els headers i el contingut que inclourà cadascun
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"} #definim la informació de la sol.licitud del protocol HTTPS
    result = post(url, headers=headers, data=data) #unim les diferents parts de la sol.licitud a la variable result
    json_result = json.loads(result.content) #emmagatzemem a json_result la resposta que hem rebut a la nostra sol.licitud
    token = json_result["access_token"] #dins de token tindrem el token d'accés que necessitem
    return token #treiem la variable token del 'scope' de la funció.

def get_auth_header(token): #Un cop tinguem el token podrem obtenir l'autorització amb aquesta funció
    return {"Authorization": "Bearer " + token}

#---------------------------------------------------------------TOKEN---------------------------------------------------

def search_for_artist(token, artist_name): #Aq
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    return json_result[0]

#-----------------------------------ARTISTES----------------------------------------------------------------------------
def get_playlist_id(playlist_urls):
    playlist_ids = []
    for playlist_url in playlist_urls:
        if 'playlist/' in playlist_url:
            playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
            print(playlist_id)
            playlist_ids.append(playlist_id)
        else:
            print(f"Invalid playlist URL: {playlist_url}")
    return playlist_ids

def get_playlist_info(playlist_id, token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks" #aquesta url serveix per mirar les cançons que composen una playlist
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "fields": "items(track(name,artists(name,genres),album(name))),next", #en aquests paràmetres establim les dades que volem rebre
        "market": "ES"
    }

    songs = [] #emmagatzemem aquí les cançons

    while url:
        response = requests.get(url, headers=headers, params=params) #a response guardem la resposta de la API
        data = response.json() #transformem la resposta en json

        if 'error' in data: #serveix per detectar errors
            print('Error:', data['error']['message'])
            return songs

        for item in data['items']: #iterem a través de cada cançó ->items
            track = item['track'] #obtenim la informació requerida
            artists = track['artists'] #recollim els artistes
            artist_names = '; '.join([artist['name'] for artist in artists]) #per evitar que es solapin artistes i tenir-los emmagatzemats correctament els "netejem" i desem
            song_info = { #informació enllaçada a cada cançó
                'name': eliminar_comas(track['name']),
                'artists': eliminar_comas(artist_names),
                'album': eliminar_comas(track['album']['name']),
            }
            songs.append(song_info) #afegim la información a la llista songs.

        url = data['next'] #amb això saltem a la següent cançó de forma iterativa.

    return songs #tornem els resultats de songs fora de la url.

def extract_playlist_data(token, playlist_ids): 
    all_data = []

    for playlist_id in playlist_ids: #iterem per cada playlist
        songs = get_playlist_info(playlist_id, token) 
        if songs is None:
            continue
        playlist_data = { #emmagatzemem la informació que tenim de la playlist
            'Playlist ID': playlist_id, #identificador
            'Songs': songs, #llistat de cançons
        }
        all_data.append(playlist_data) #afegim la informació a all_data.

    playlist_dfs = [] #dataframe buit
    for playlist_data in all_data: #afegim la informació al dataframe des de playlist_data 
        playlist_id = playlist_data['Playlist ID'] 
        songs = playlist_data['Songs']
        df = pd.DataFrame(songs) 
        df['Playlist ID'] = playlist_id 
        playlist_dfs.append(df) 

    df_final = pd.concat(playlist_dfs) #unim els diversos dataframes

    return df_final


def eliminar_comas(cadena): #petita funció per netejar les comes dels noms d'artistes i cançons.
    cadena_limpia = cadena.replace(',', '')
    return cadena_limpia

def concatenate_strings(strings):
    concatenated_string = ';'.join(strings)
    return concatenated_string




## Extract playlist data------------------------------------------------PLAYLISTS--------------------------------------------------------------tify.com/playlist/37i9dQZF1DXcpG5daApEnA?si=b3e345f782734c8f"]get_playlist_id(Playlists)
token = get_token()

playlists = [
    "https://open.spotify.com/playlist/37i9dQZF1DXcpG5daApEnA",
    "https://open.spotify.com/playlist/37i9dQZF1DX9zzf8V7JAQ5",
    "https://open.spotify.com/playlist/37i9dQZF1DWVBAKsA3f6Ck",
    "https://open.spotify.com/playlist/37i9dQZF1DX4f5T2OF14nZ",
    "https://open.spotify.com/playlist/37i9dQZF1DXdHJoK6pY7Oh",
    "https://open.spotify.com/playlist/37i9dQZF1DX1bd6S1wAnbF",
    "https://open.spotify.com/playlist/37i9dQZF1DXag6GMMWZSZ4",
    "https://open.spotify.com/playlist/37i9dQZF1DX25bh4Tsdtts",
    "https://open.spotify.com/playlist/37i9dQZF1DX0ywbtKZmG0E",
    "https://open.spotify.com/playlist/37i9dQZF1DX8EdanpjeYXD",
    "https://open.spotify.com/playlist/37i9dQZF1DX0rX3xBmXrDn",
    "https://open.spotify.com/playlist/37i9dQZF1DX8ri0Q7eg1qe",
    "https://open.spotify.com/playlist/37i9dQZF1DX5aHrtH3szCF",
    "https://open.spotify.com/playlist/37i9dQZF1DWVqckwNwncJY",
    "https://open.spotify.com/playlist/37i9dQZF1DX5S2RzqA1qg6",
    "https://open.spotify.com/playlist/37i9dQZF1DXax0Fz6Uds7a"]


playlist_ids = get_playlist_id(playlists)
df_final = extract_playlist_data(token, playlist_ids)

df_final.to_csv("playlist_data2.csv", index=False, sep='/')


