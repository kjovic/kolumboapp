
✈️ LangGraph AI Travel Assistant

LangGraph AI Travel Assistant je inteligentni agent izgrađen pomoću LangGraph i LangChain frameworka, sposoban za dinamično planiranje putovanja – uključujući pretragu letova i hotela – koristeći Apify scrapers.


## POSTAVLJANJE PROJEKTA ZA TULIPANE POPUT MENE I KREŠE

⸻

✅ 1. Instalacija Pythona 🐍

Prvo moraš imati instaliran Python (najčešće verziju 3.10+).

🔗 Idi na https://www.python.org/downloads/
⬇️ Skini najnoviju verziju za tvoj operativni sustav.
☑️ VAŽNO: Prilikom instalacije obavezno označi “Add Python to PATH” prije nego klikneš “Install”.

⸻

🧼 2. Kloniranje repozitorija 📦

Ako još nisi:

git clone https://github.com/ime-tvog-projekta.git
cd ime-tvog-projekta

⸻

🧪 3. Kreiranje virtualnog okruženja 🧠

Virtualno okruženje omogućava da se svi paketi instaliraju lokalno, samo za taj projekt — bez da “zagađuju” cijeli sustav.

U root folderu projekta (unutar VS Code-a, npr.) pokreni:

python -m venv .venv

Ovo će napraviti folder .venv koji sadrži sve potrebne alate.

⸻

▶️ 4. Aktivacija virtualnog okruženja ⚙️

Na Windowsu:

.venv\Scripts\activate

Na macOS/Linuxu:

source .venv/bin/activate

✅ Kad aktiviraš env, primijetit ćeš da se u terminalu ispred puta pojavi nešto poput (.venv) — to znači da si u virtualnom svijetu! 🎮

⸻

📦 5. Instalacija zavisnosti iz requirements.txt 🧾

U istom tom terminalu, dok je .venv aktivan, pokreni:

pip install -r requirements.txt

⏳ Ovo će potegnuti sve biblioteke koje su potrebne za projekt.

⸻

Naravno, Petar! Dodajem i objašnjenje za .env fajl i kako se koristi za čuvanje OpenAI API ključa. To je jako bitno, jer bez toga aplikacija neće moći komunicirati s OpenAI-jem.

⸻

🔐 6. Postavljanje .env fajla za API ključ 🗝️

Tvoj projekt koristi OpenAI API — da bi to radilo, moraš unutar projekta napraviti .env fajl koji sadrži tvoj privatni API ključ.

🛠️ Koraci:
	1.	U root folderu projekta (gdje ti je i main.py, requirements.txt, itd.), napravi novi fajl koji se zove .env (doslovno tako, s točkom ispred imena).
	2.	U taj fajl zalijepi svoj OpenAI ključ ovako:

OPENAI_API_KEY=sk-ovdje-ide-tvoj-kljuc

	3.	Sačuvaj fajl i ne dijeli ga nikome (ključ je privatan i može se zloupotrijebiti).

⸻


⸻

❗ Napomena za GIT:

Dodaj .env u .gitignore da se slučajno ne push-a na GitHub:

# u .gitignore dodaj
.env


⸻


🏁 KRAJ: Spreman si za pokretanje projekta 🎉

Sad možeš pokrenuti svoj langgraph dev u terminalu gdje si pokrenuo virtual env

🚀 Funkcionalnosti
	•	🔍 Pretraga letova (Apify Skyscanner Scraper)
	•	🏨 Pretraga hotela (Apify Booking Scraper)
	•	📅 Postavljanje datuma, broja putnika, preferencija
	•	🌐 Višejezična podrška (postavljanje jezika interakcije)
	•	🤖 LangGraph agentni tok s automatskim tool routingom
	•	🧠 Dinamičko pamćenje stanja kroz InjectedState

⸻

🧱 Arhitektura

Projekt koristi LangGraph za orkestraciju tokova između:
	•	AI agenta (booking_agent)
	•	Alata (ToolNode)

Svaki alat (tool) koristi @tool dekorator iz LangChain, i integriran je u tok grafa.

User ↔️ LangGraph ↔️ Booking Agent ↔️ Tool Node ↔️ External API (Apify)



⸻

🛠 Korišteni alati (tools)

✈️ search_flights_with_apify

Pretražuje letove putem Apify Skyscanner actor-a. Koristi origin_location, destination_location, departure_date, return_date, broj putnika itd.

✍️ set_flight_details

Postavlja početne parametre za pretragu letova (lokacije, datumi, broj putnika itd.).

📋 return_flights

Vraća rezultate pretrage letova u sažetom formatu s linkovima za booking.

⸻

🏨 search_hotels_with_apify

Pretražuje hotele pomoću Apify Booking scraper-a. Uzima u obzir lokaciju, datume, broj soba, cijene, tip smještaja i druge filtere.

✍️ set_booking_details

Postavlja sve potrebne parametre za hotel booking: lokaciju, datume, sobe, broj putnika, tip smještaja, itd.

📋 return_hotels

Vraća listu hotela s osnovnim informacijama i booking linkovima.

⸻

🌍 set_desired_language / retrieve_desired_language

Postavlja/preuzima željeni jezik interakcije (npr. “en-gb”, “hr”, itd.).

⸻

🧠 Agent (booking_agent)

Agent koristi LangChain chat model (npr. OpenAI, Anthropic, itd.) s alatima iz AGENT_TOOLS.

Logika toka:
	1.	Agent odgovara korisniku.
	2.	Ako koristi alat – prelazi na tools node.
	3.	Rezultat se vraća agentu za daljnju obradu ili kraj konverzacije.

builder = StateGraph(State, config_schema=Configuration)
builder.add_node("booking_agent", booking_agent)
builder.add_node("tools", ToolNode(AGENT_TOOLS))

builder.add_edge(START, "booking_agent")
builder.add_conditional_edges("booking_agent", route_model_output)
builder.add_edge("tools", "booking_agent")

graph = builder.compile()
graph.name = "booking-agent"



⸻

🧬 State struktura

Koristi se custom State klasa (agent/state.py) koja proširuje AgentState, s poljima za:
	•	hotels, flights
	•	selected options
	•	datumi, broj putnika, filteri
	•	user query i jezik

⸻

✅ Kako koristiti
	1.	Postavi environment variable za Apify API ključ:

export APIFY_API_KEY=your_key_here

    NAPRAVI PYTHON ENVIROMENT 

    python -m venv .venv

    # activate virtual environment
    .venv\Scripts\activate


	2.	Instaliraj dependency-je:

pip install -r requirements.txt


	3.	Pokreni LangGraph tok:
        langgraph dev 



⸻

💡 Ideje za proširenje
	•	Integracija s payment gateways (Stripe, Paypal)
	•	Dodavanje filtera za letove (samo direktni, klase, kompanije)
	•	Session tracking i povijest prethodnih planova
	•	Destinacijski savjeti s OpenAI funkcijama ili Tripadvisor API
	•	Automatski itinerar na temelju korisničkih upita

⸻

📂 Struktura projekta

agent/
│
├── tools/
│   ├── flight_tools.py
│   └── hotel_tools.py
│
├── models/
│   ├── flights.py
│   └── booking.py
│
├── state.py
├── config.py
└── graph.py (pokretanje LangGraph agenta)



⸻

🧠 Tech Stack
	•	🕸 LangGraph & LangChain
	•	🧠 OpenAI / Anthropic (modularno)
	•	🌐 Apify scrapers
	•	✅ Pydantic (validacija)
	•	🛠 ToolNode + AgentNode orchestration

⸻
