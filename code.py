import requests
from bs4 import BeautifulSoup as bs
import os
import nltk
import pandas as pd
import string
import re


class Scrapper:
    def __init__(self, link):
        self.link = link

    def read_url(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(
            url=self.link, headers=headers)
        html = bs(r.text, "html.parser")
        self.text = html.findAll("h1", {"class": "entry-title"})
        self.text = str(self.text[0]).replace('<h1 class="entry-title">', '')
        self.text = self.text.replace('</h1>', '')
        self.text += " \n "
        text_content = html.findAll("div", {"class": "td-post-content"})
        self.text += str(text_content[0]).replace('</p>\n<p>', '')
        self.text = self.text.replace('</p>\n<h3><a></a><strong>', '')
        self.text = self.text.replace('</strong></h3>\n<p>', '')
        self.text = self.text.replace('</p>\n<h3><strong>', '')
        self.text = self.text.replace('</strong><strong>', '')
        self.text = self.text.replace('</pre>\n</div>', '')
        self.text = self.text.replace('<div class="td-post-content">\n<p>', '')
        self.text = self.text.replace(
            '</p>\n<pre class="wp-block-preformatted">Blackcoffer Insights 33: Suriya E, Vellore Institute of Technology',
            '')

    def clean_stopwords(self):
        """

        Creating a list of stop words from the given data

        """
        StopWords_lst = []
        for i in os.listdir("StopWords"):
            with open("StopWords/" + i) as f:
                for lines in f.readlines():
                    lines = lines.replace(' ', '')
                    lines = lines.replace('\n', '')

                    for i in lines.split("|"):
                        StopWords_lst.append(i)
        self.list_of_words = []
        l1 = nltk.word_tokenize(self.text)
        for i in l1:
            self.list_of_words.append(i.lower())
        for i in StopWords_lst:
            if i in self.list_of_words:
                self.list_of_words.remove(i)

    def positive_score(self):

        """
        creating a list of positive words and return positive score

        """

        df = pd.read_csv("LoughranMcDonald_MasterDictionary_2020.csv")

        year = [2009, 2014, 2011, -2020, 2012]
        positive = []
        for i in year:
            for j in (df[df["Positive"] == i]["Word"].values):
                positive.append(j.lower())

        self.positive_score = 0
        for i in self.list_of_words:
            if i in positive:
                self.positive_score += 1
        return self.positive_score

    def negative_score(self):

        """
              creating a list of negative words and return negative score

              """

        df = pd.read_csv("LoughranMcDonald_MasterDictionary_2020.csv")

        year = [2009, 2014, 2011, -2020, 2012]
        negative = []
        for i in year:
            for j in (df[df["Negative"] == i]["Word"].values):
                negative.append(j.lower())

        self.negative_score = 0
        for i in self.list_of_words:
            if i in negative:
                self.negative_score += 1
        return self.negative_score

    def polarity(self):
        polarity = (self.positive_score - self.negative_score) / (
                    (self.positive_score + self.negative_score) + 0.000001)
        return polarity

    def subjectivity_Score(self):
        Subjectivity_Score = (self.positive_score + self.negative_score) / ((len(self.list_of_words)) + 0.000001)
        return Subjectivity_Score

    def average_sentense_length(self):
        punch = string.punctuation
        lst = []
        for word in nltk.word_tokenize(self.text):
            if word not in punch:
                lst.append(word)
        self.total_words = len(lst)
        self.total_sentence = len(nltk.sent_tokenize(self.text))
        self.Average_Sentence_Length = self.total_words / self.total_sentence
        return self.Average_Sentence_Length

    def percentage_complex(self):
        complex_words = []
        vowels = ['a', 'e', 'i', 'o', 'u']
        for i in self.list_of_words:
            counter = 0
            for j in i:
                if j in vowels:
                    counter += 1
            if counter > 2 and i[-2:] != "es" and i[-2:] != "ed":
                complex_words.append(i)
        self.complex_words_length = len(complex_words)
        self.percentage_complex_words = self.complex_words_length / len(self.list_of_words)
        return self.percentage_complex_words

    def fog_index(self):
        Fog_Index = 0.4 * (self.percentage_complex_words + self.Average_Sentence_Length)
        return Fog_Index

    def average_number_words_per_sentence(self):
        Average_Number_of_Words_Per_Sentence = self.total_words / self.total_sentence
        return Average_Number_of_Words_Per_Sentence

    def complex_word_count(self):
        return self.complex_words_length

    def word_count(self):
        return self.total_words

    def syllabul_count_per_word(self):
        return self.complex_words_length

    def personal_pronoun(self):

        count_mentions = 0
        patterns = {"personal_pronoun": [" i ", " we ", " us ", " ours ", " my ", " I ", " We ", " Us", "Ours", "My"]}
        for i in patterns.values():
            for j in i:
                pattern = re.compile(j)
                mentions = re.findall(pattern, self.text)
                count_mentions += len(mentions)
        return count_mentions

    def average_word_length(self):
        char_count = 0
        for i in self.text:
            if i.isalnum():
                char_count += 1
        Average_Word_Length = char_count / self.total_words
        return Average_Word_Length


df = pd.read_excel("Input.xlsx", engine='openpyxl')
link_lst = [i for i in df["URL"]]
df1 = pd.read_excel('Output Data Structure.xlsx', engine='openpyxl')
i = 0
for link in link_lst:
    sc = Scrapper(link)
    sc.read_url()
    sc.clean_stopwords()
    df1.loc[i, 'POSITIVE SCORE'] = sc.positive_score()
    df1.loc[i, 'NEGATIVE SCORE'] = sc.negative_score()
    df1.loc[i, 'POLARITY SCORE'] = sc.polarity()
    df1.loc[i, 'SUBJECTIVITY SCORE'] = sc.subjectivity_Score()
    df1.loc[i, 'AVG SENTENCE LENGTH'] = sc.average_sentense_length()
    df1.loc[i, 'PERCENTAGE OF COMPLEX WORDS'] = sc.percentage_complex()
    df1.loc[i, 'FOG INDEX'] = sc.fog_index()
    df1.loc[i, 'AVG NUMBER OF WORDS PER SENTENCE'] = sc.average_number_words_per_sentence()
    df1.loc[i, 'COMPLEX WORD COUNT'] = sc.complex_word_count()
    df1.loc[i, 'WORD COUNT'] = sc.word_count()
    df1.loc[i, 'SYLLABLE PER WORD'] = sc.syllabul_count_per_word()
    df1.loc[i, 'PERSONAL PRONOUNS'] = sc.personal_pronoun()
    df1.loc[i, 'AVG WORD LENGTH'] = sc.average_word_length()
    i += 1
df1.to_csv('result.csv', columns=df1.columns,
    header=True,
    index=True,)