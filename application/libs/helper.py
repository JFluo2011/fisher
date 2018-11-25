
def keyword_is_isbn(keywords):
    short_words = keywords.replace('-', '')
    is_isbn = False
    if (len(short_words) == 13) and (short_words.isdigit()):
        is_isbn = True
    elif ('-' in keywords) and (len(short_words) == 10) and (short_words.isdigit()):
        is_isbn = True

    return is_isbn
