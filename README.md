# SentiLeak
This is a lexicon-based sentiment analysis package for Python.

For now, it only supports Spanish but it will be extended to support other languages like English, Portuguese, Catalan or French.

## Installation
SentiLeak can be installed with pip:
```
pip install SentiLeak
```


## Usage
To use this package, it is only necessary to import ``SentiLeak`` class and call the method ``compute_sentiment``.

This is an example of usage:

````bash
>>> from sentileak import SentiLeak
>>> sent_analysis = SentiLeak()
>>> text = "La decisión del árbitro fue muy perjudicial para el equipo local. El partido estaba empatado para ambos equipos. Al final, el portero hizo una gran intervención que salvó a su equipo."
>>> sent_analysis.compute_sentiment(text)
{
	'per_sentence_sentiment': [{
		'position': 0,
		'text': 'La decisión del árbitro fue muy perjudicial para el equipo local.',
		'score': -3.0
	}, {
		'position': 1,
		'text': 'El partido estaba empatado para ambos equipos.',
		'score': 0.0
	}, {
		'position': 2,
		'text': 'Al final, el portero hizo una gran intervención que salvó a su equipo.',
		'score': 3.0
	}],
	'global_sentiment': 0.0
}
````

## Contributor
The main (and the only) contributor is [FernanOrtega](https://github.com/FernanOrtega). 

This project has also the support of [Opileak](https://www.opileak.com).
