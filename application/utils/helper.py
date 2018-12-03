def keyword_is_isbn(keyword):
    tmp = keyword.strip().replace('-', '')
    return (len(tmp) in [10, 13]) and tmp.isdigit()

