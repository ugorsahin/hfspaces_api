# Hugging Face Spaces API

This repository contains source code for Spaces API, a Python library to connect Hugging Face gradio spaces via websockets.

I am happy to help towards resolving the [issues](https://github.com/ugorsahin/hfspaces_api/issues).

## Setting up hfspaces_api

Basically clone the repository and run

```
pip install .
```

### Requirements
This library is developed under python 3.8.10 and uses
```
websocket-client >= 1.4.2
requests >= 2.28.1
```
## Contributing

Contributions are welcomed! 
* New efforts and features
* Bug fixes
* Streamlit support

## Quick Start

The following code should help you

```
import hfspaces_api as sp
handler = sp.SpacesAPI("ugursahin", "MovieSuggest)
```

you will get the summary of functions
```
2022-12-19 00:38:40 Function 0:
 summary:
 [{'expected datatype': 'string',
  'placeholder': 'A humble and uncomplicated samurai disbands his life as a '
                 'knight errant',
  'type': 'Textbox'},
 {'expected datatype': 'number',
  'label': 'Number of samples to show',
  'type': 'Slider',
  'value': 5},
 {'expected datatype': 'string',
  'label': 'Genre (Optional)',
  'placeholder': 'Horror, Crime',
  'type': 'Textbox'},
 {'expected datatype': 'string',
  'label': 'Country (Optional)',
  'placeholder': 'UK, France, Canada',
  'type': 'Textbox'},
 {'expected datatype': 'string',
  'label': 'Language (Optional)',
  'placeholder': 'English, Italian',
  'type': 'Textbox'}]
```

Then you can interact with the spaces via interact function

```
out = handler.interact([['A humble and uncomplicated samurai disbands his life as a knight errant', 5, "", "", ""]])
print(out)
```

The example output
```
{'data': [[[{'name': '/tmp/tmpzvhe36k4/tmpkcjd7q8o.png',
     'data': None,
     'is_file': True},
    'Shogun Assassin - 1980'],
   [{'name': '/tmp/tmpzvhe36k4/tmphl7ayf25.png',
     'data': None,
     'is_file': True},
    'Rurouni Kenshin - 1996'],
   [{'name': '/tmp/tmpzvhe36k4/tmpavax3hwq.png',
     'data': None,
     'is_file': True},
    'Samurai Headhunters - 2013'],
   [{'name': '/tmp/tmpzvhe36k4/tmp4u7vk9as.png',
     'data': None,
     'is_file': True},
    'The Blind Swordsman: Zatoichi - 2003'],
   [{'name': '/tmp/tmpzvhe36k4/tmptq1xjlrt.png',
     'data': None,
     'is_file': True},
    'Gintama - 2005']]],
 'is_generating': False,
 'duration': 0.7432782649993896,
 'average_duration': 0.7432782649993896}
```