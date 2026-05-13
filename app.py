from flask import Flask, render_template, request, redirect
import sqlite3
import requests

app = Flask(__name__)


@app.route("/") #Sākumlapa
def sakums():
    return render_template("index.html")


@app.route('/vienkarsi')  # Vienkāršā laikapstākļu lapa ar pašreizējo temperatūru
def vienkarsi():
    city = request.args.get("city", "Riga")
    cities = {
        "Riga": (56.95, 24.11),
        
    }

    lat, lon = cities.get(city, (56.95, 24.11))

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,weathercode",
        "timezone": "Europe/Riga"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        current = data["current"]
        weather = {
            "city": city,
            "temperature": round(current["temperature_2m"]),
            "feels_like": round(current["apparent_temperature"]),
            "condition": get_condition(current["weathercode"])
        }

        return render_template("vienkarsi.html", weather=weather)
    except:
        return render_template("vienkarsi.html", error="Neizdevās iegūt laika datus")



@app.route('/detalizeti') # Detalizētā laikapstākļu lapa ar 7 dienu prognozi
def detalizeti():
    city = request.args.get("city", "Riga")


    cities = {
        "Riga": (56.95, 24.11),
    }

    lat, lon = cities.get(city, (56.95, 24.11))
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,weathercode",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "Europe/Riga",
        "forecast_days": 7
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        current = data["current"]
        daily = data["daily"]
        weather = {
            "city": city,
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "condition": get_condition(current["weathercode"])
        }


        forecast = []
        for i in range(7):
            forecast.append({
                "date": daily["time"][i],
                "max_temp": daily["temperature_2m_max"][i],
                "min_temp": daily["temperature_2m_min"][i],
                "condition": get_condition(daily["weathercode"][i])
            })

        return render_template("detalizeti.html", 
                               weather=weather, 
                               forecast=forecast)
    except:
        return render_template("detalizeti.html", error="Neizdevās iegūt laika datus :(")

def get_condition(code):
    conditions = {
        0: "Skaidrs", 
        1: "Galvenokārt skaidrs", 
        2: "Daļēji mākoņains",
        3: "Mākoņains", 
        45: "Migla", 
        51: "Viegla smidzināšana",
        61: "Lietus", 
        71: "Sniegs", 
        95: "Pērkona negaiss"
    }
    return conditions.get(code, "Mainīgs laiks")


@app.route("/kovilkt") # Apģērbu ieteikumu lapa pēc temperatūras un laikapstākļiem
def kovi_lkt():
    temperatura = request.args.get("temperatura", type=int)
    laiks = request.args.get("laiks")
    dzimums = request.args.get("dzimums")

    if temperatura is None or not laiks:
        return render_template("kovilkt.html")

    apgerbi = []


    if laiks == "Lietus":

        if temperatura <= 0:
            apgerbi = [
                {"nosaukums": "ziemas jaka", "veids": "virsdrēbes"},
                {"nosaukums": "silts džemperis", "veids": "augša"},
                {"nosaukums": "bikses", "veids": "apakša"},
                {"nosaukums": "ūdensizturīgi zābaki", "veids": "apavi"},
                {"nosaukums": "cepure", "veids": "aksesuāri"}
            ]

        elif 1 <= temperatura <= 7:
            apgerbi = [
                {"nosaukums": "vējjaka", "veids": "virsdrēbes"},
                {"nosaukums": "džemperis", "veids": "augša"},
                {"nosaukums": "bikses", "veids": "apakša"},
            ]

        elif 8 <= temperatura <= 15:
            apgerbi = [
                {"nosaukums": "lietus jaka", "veids": "virsdrēbes"},
                {"nosaukums": "krekls", "veids": "augša"},
                {"nosaukums": "bikses", "veids": "apakša"},

            ]

        elif 16 <= temperatura <= 22:
            apgerbi = [
                {"nosaukums": "plāna lietus jaka", "veids": "virsdrēbes"},
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "vieglas bikses", "veids": "apakša"},

            ]

        else:
            apgerbi = [
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "šorti", "veids": "apakša"},
                {"nosaukums": "plāna lietus jaka", "veids": "virsdrēbes"},
            ]

    # SKAIDRS
    elif laiks == "Skaidrs":

        if temperatura <= 0:
            apgerbi = [
                {"nosaukums": "ziemas jaka", "veids": "virsdrēbes"},
                {"nosaukums": "silts džemperis", "veids": "augša"},
                {"nosaukums": "ziemas bikses", "veids": "apakša"},
                {"nosaukums": "zābaki", "veids": "apavi"},
                {"nosaukums": "cimdi", "veids": "aksesuāri"}
            ]

        elif 1 <= temperatura <= 10:
            apgerbi = [
                {"nosaukums": "džemperis", "veids": "augša"},
                {"nosaukums": "vējjaka", "veids": "virsdrēbes"},
                {"nosaukums": "bikses", "veids": "apakša"},

            ]

        elif 11 <= temperatura <= 18:
            apgerbi = [
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "plāna jaka", "veids": "virsdrēbes"},
                {"nosaukums": "bikses", "veids": "apakša"}
            ]

        elif 19 <= temperatura <= 25:
            apgerbi = [
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "šorti", "veids": "apakša"},
                {"nosaukums": "sporta apavi", "veids": "apavi"}
            ]

        else:
            apgerbi = [
                {"nosaukums": "bezpiedurkņu krekls", "veids": "augša"},
                {"nosaukums": "šorti", "veids": "apakša"},
                {"nosaukums": "sandales", "veids": "apavi"},
                {"nosaukums": "saulesbrilles", "veids": "aksesuāri"}
            ]


    elif laiks == "Mākoņains":

        if temperatura <= 5:
            apgerbi = [
                {"nosaukums": "silts džemperis", "veids": "augša"},
                {"nosaukums": "jaka", "veids": "virsdrēbes"},
                {"nosaukums": "biezas bikses", "veids": "apakša"}
            ]

        elif 6 <= temperatura <= 15:
            apgerbi = [
                {"nosaukums": "džemperis", "veids": "augša"},
                {"nosaukums": "bikses", "veids": "apakša"},
                {"nosaukums": "sporta apavi", "veids": "apavi"}
            ]

        elif 16 <= temperatura <= 22:
            apgerbi = [
                {"nosaukums": "hoodie", "veids": "augša"},
                {"nosaukums": "vieglas bikses", "veids": "apakša"}
            ]

        else:
            apgerbi = [
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "šorti", "veids": "apakša"}
            ]

    elif laiks == "Sniegs":

        if temperatura <= -10:
            apgerbi = [
                {"nosaukums": "ļoti silta ziemas jaka", "veids": "virsdrēbes"},
                {"nosaukums": "termobikses", "veids": "apakša"},
                {"nosaukums": "ziemas zābaki", "veids": "apavi"},
                {"nosaukums": "cimdi", "veids": "aksesuāri"},
                {"nosaukums": "šalle", "veids": "aksesuāri"}
            ]

        elif -9 <= temperatura <= 0:
            apgerbi = [
                {"nosaukums": "ziemas jaka", "veids": "virsdrēbes"},
                {"nosaukums": "džemperis", "veids": "augša"},
                {"nosaukums": "ziemas bikses", "veids": "apakša"},
                {"nosaukums": "zābaki", "veids": "apavi"}
            ]

        else:
            apgerbi = [
                {"nosaukums": "silta jaka", "veids": "virsdrēbes"},
                {"nosaukums": "bikses", "veids": "apakša"},
                {"nosaukums": "ūdensizturīgi apavi", "veids": "apavi"}
            ]

    elif laiks == "Vējains":

        if temperatura <= 5:
            apgerbi = [
                {"nosaukums": "siltā jaka", "veids": "virsdrēbes"},
                {"nosaukums": "džemperis", "veids": "augša"},
                {"nosaukums": "bikses", "veids": "apakša"}
            ]

        elif 6 <= temperatura <= 15:
            apgerbi = [
                {"nosaukums": "hoodie", "veids": "augša"},
                {"nosaukums": "vējjaka", "veids": "virsdrēbes"},
                {"nosaukums": "bikses", "veids": "apakša"}
            ]

        elif 16 <= temperatura <= 22:
            apgerbi = [
                {"nosaukums": "plāna vējjaka", "veids": "virsdrēbes"},
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "vieglas bikses", "veids": "apakša"}
            ]

        else:
            apgerbi = [
                {"nosaukums": "t-krekls", "veids": "augša"},
                {"nosaukums": "šorti", "veids": "apakša"},
            ]

    return render_template("kovilkt.html", apgerbi=apgerbi)

if __name__ == "__main__":
    app.run(debug=True)

