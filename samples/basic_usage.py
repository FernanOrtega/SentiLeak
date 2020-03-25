from sentileak import SentiLeak

sent_analysis = SentiLeak()
text = (
    "La decisión del árbitro fue muy perjudicial para el equipo local. El partido estaba empatado para ambos "
    "equipos. Al final, el portero hizo una gran intervención que salvó a su equipo. "
)
print(text)
print(sent_analysis.compute_sentiment(text))
