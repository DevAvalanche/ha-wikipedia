# Wikipedia for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Brings Wikipedia's daily featured content into Home Assistant as sensors.

## Sensors

| Sensor | State | Key Attributes |
|---|---|---|
| `sensor.wikipedia_featured_article` | Article title | `title`, `description`, `extract`, `url`, `thumbnail_url` |
| `sensor.wikipedia_image_of_the_day` | Image title | `image_url`, `thumbnail_url`, `description`, `credit`, `license`, `file_page` |
| `sensor.wikipedia_on_this_day` | Event count | `date`, `events` (3 items: `year`, `text`, `url`, `thumbnail`) |
| `sensor.wikipedia_most_read` | Top article | `top_title`, `top_views`, `top_url`, `top_thumbnail`, `articles` (3 items) |
| `sensor.wikipedia_in_the_news` | Story count | `stories` (3 items: `story`, `url`, `thumbnail`) |

## Dashboard Cards

### Featured Article
```yaml
type: markdown
title: 📖 Featured Article
content: >
  {% set thumb = state_attr('sensor.wikipedia_featured_article', 'thumbnail_url') or '' %}
  {% set title = state_attr('sensor.wikipedia_featured_article', 'displaytitle') or '' %}
  {% set desc = state_attr('sensor.wikipedia_featured_article', 'description') or '' %}
  {% set extract = state_attr('sensor.wikipedia_featured_article', 'extract') or '' %}
  {% set url = state_attr('sensor.wikipedia_featured_article', 'url') or '' %}

  {% if thumb %}<img src="{{ thumb }}" style="float:right;max-width:110px;border-radius:8px;margin-left:12px;">{% endif %}
  ### {{ title }}
  *{{ desc }}*

  {{ extract[:350] }}...

  [Read on Wikipedia ↗]({{ url }})
```

### Image of the Day
```yaml
type: markdown
title: 🖼️ Image of the Day
content: >
  {% set img = state_attr('sensor.wikipedia_image_of_the_day', 'thumbnail_url') or '' %}
  {% set title = state_attr('sensor.wikipedia_image_of_the_day', 'title') or '' %}
  {% set desc = state_attr('sensor.wikipedia_image_of_the_day', 'description') or '' %}
  {% set credit = state_attr('sensor.wikipedia_image_of_the_day', 'credit') or '' %}
  {% set license = state_attr('sensor.wikipedia_image_of_the_day', 'license') or '' %}
  {% set page = state_attr('sensor.wikipedia_image_of_the_day', 'file_page') or '' %}

  {% if img %}<img src="{{ img }}" style="width:100%;border-radius:8px;margin-bottom:8px;">{% endif %}
  **{{ title }}**

  {{ desc[:250] }}

  <small>📷 {{ credit }} · {{ license }}</small>
  {% if page %}[View on Wikimedia ↗]({{ page }}){% endif %}
```

### On This Day
```yaml
type: markdown
title: 📅 On This Day
content: >
  {% set events = state_attr('sensor.wikipedia_on_this_day', 'events') %}
  {% set date = state_attr('sensor.wikipedia_on_this_day', 'date') or '' %}

  ## {{ date }}

  {% if events %}
  {% for e in events %}
  **{{ e.year }}** — {{ e.text }}
  {% if e.url %}[↗]({{ e.url }}){% endif %}

  {% endfor %}
  {% else %}
  *No events available*
  {% endif %}
```

### Most Read
```yaml
type: markdown
title: 📈 Most Read Today
content: >
  {% set articles = state_attr('sensor.wikipedia_most_read', 'articles') %}
  {% set date = state_attr('sensor.wikipedia_most_read', 'date') or '' %}

  ## {{ date }}

  {% if articles %}
  {% for a in articles %}
  {{ a.rank }}. [{{ a.title }}]({{ a.url }}) · *{{ "{:,}".format(a.views) }} views*
  {% endfor %}
  {% else %}
  *No data available*
  {% endif %}
```

### In the News
```yaml
type: markdown
title: 📰 In the News
content: >
  {% set stories = state_attr('sensor.wikipedia_in_the_news', 'stories') %}

  {% if stories %}
  {% for s in stories %}
  - {{ s.story }}{% if s.url %} [↗]({{ s.url }}){% endif %}

  {% endfor %}
  {% else %}
  *No news available*
  {% endif %}
```

## Installation

### HACS
1. HACS → Integrations → Custom Repositories → add `https://github.com/DevAvalanche/ha-wikipedia` → Integration
2. Search Wikipedia → Download → Restart HA
3. Settings → Devices & Services → Add Integration → Wikipedia

## License
MIT. Wikipedia content is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
