"""Constants for the Wikipedia integration."""

DOMAIN = "wikipedia"

CONF_LANGUAGE = "language"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_FEATURED_ARTICLE = "featured_article"
CONF_IMAGE_OF_DAY = "image_of_day"
CONF_ON_THIS_DAY = "on_this_day"
CONF_ON_THIS_DAY_COUNT = "on_this_day_count"
CONF_MOST_READ = "most_read"
CONF_IN_THE_NEWS = "in_the_news"
CONF_IN_THE_NEWS_COUNT = "in_the_news_count"
CONF_DID_YOU_KNOW = "did_you_know"

DEFAULT_LANGUAGE = "en"
DEFAULT_UPDATE_INTERVAL = 6
DEFAULT_ON_THIS_DAY_COUNT = 3
DEFAULT_IN_THE_NEWS_COUNT = 3

DATA_FEATURED_ARTICLE = "tfa"
DATA_IMAGE_OF_DAY = "image"
DATA_ON_THIS_DAY = "onthisday"
DATA_MOST_READ = "mostread"
DATA_IN_THE_NEWS = "news"
DATA_DID_YOU_KNOW = "dyk"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ja": "Japanese",
    "zh": "Chinese",
    "ru": "Russian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "he": "Hebrew",
    "fa": "Persian",
    "sv": "Swedish",
    "no": "Norwegian",
    "cs": "Czech",
    "hu": "Hungarian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "el": "Greek",
    "ur": "Urdu",
    "vi": "Vietnamese",
}
