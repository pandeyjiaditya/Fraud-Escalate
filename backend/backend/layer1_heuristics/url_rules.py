import re


def check_url(text):

    flags = []

    urls = re.findall(r"https?://\S+", text)

    for url in urls:

        if any(word in url for word in ["login", "verify", "secure", "update"]):
            flags.append("suspicious_url")

        # long/random domains
        if len(url) > 30:
            flags.append("long_url")

    return flags