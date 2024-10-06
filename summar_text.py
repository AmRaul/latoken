import re

def remove_duplicates(text):
    # Убираем лишние пробелы и переносы строк
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    # Разбиваем текст на предложения
    sentences = re.split(r'[.!?]', cleaned_text)

    # Используем множество для уникальных предложений
    unique_sentences = list(dict.fromkeys(sentences))

    # Объединяем уникальные предложения обратно в текст
    return '. '.join(unique_sentences).strip()




