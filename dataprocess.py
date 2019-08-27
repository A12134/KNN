import operator
from collections import OrderedDict

class TweetDatabase:
    def __init__(self):
        self.db = dict()
        self.dbpattern = dict()

    def addline(self, l):
        if self.db.get(l[0]) is None:
            self.db[l[0]] = [l[1]]
            self.dbpattern[l[0]] = TweetPattern(l[0])
        else:
            self.db[l[0]].append(l[1])

    def processPattern(self):
        for user in self.db.keys():
            for i in range(self.db[user].__len__()):
                self.db[user][i] = self.db[user][i].split(" ")
                self.dbpattern[user].feedTweet(self.db[user][i])

        for user in self.dbpattern.keys():
            self.dbpattern[user].sortFrequent()
            self.dbpattern[user].getTopValue(10)

    def printdbInfo(self):
        count = 0
        for i in self.dbpattern.keys():
            count += 1
        print("user number: " + str(count))

    def getMaximumWords(self):
        words = dict()
        for user in self.dbpattern.keys():
            list = self.dbpattern[user].topList
            for w in list:
                if words.get(w) is None:
                    words[w] = 1
                else:
                    words[w] += 1

        sorted_word = sorted(words.items(), key = lambda  x:x[1], reverse=True)
        print(sorted_word)
        return sorted_word

    def prediction(self, sentence):
        # TODO normalize the sentence
        tokens = sentence.split(" ")
        tokens = { i : 0 for i in tokens }
        scoreList = dict()
        for k in self.dbpattern.keys():
            scoreList[k] = self.dbpattern[k].predictScore(tokens)

        scores = sorted(scoreList.items(), key=lambda x:x[1],reverse=True)

        return scores

class TweetPattern:

    def __init__(self,  userID):
        self.userID = userID
        self.frequentList = dict()
        self.topList = []
        self.max = 0
        self.ignoreToken = {
            "@handle":0,
            "the": 0,
            "to": 0,
            "a": 0,
            "I": 0,
            "is": 0,
            "in": 0,
            "for": 0,
            "of": 0,
            "and": 0,
            "RT": 0,
            "on": 0,
            "you": 0,
            "my": 0,
            "at": 0,
            "-":0
        }

    def predictScore(self, tokens):
        score = 0
        seenToken = dict()
        for index, w in enumerate(self.topList):
            if tokens.get(w) is not None:
                if seenToken.get(w) is None:
                    seenToken[w] = 1
                else:
                    seenToken[w] += 1
                score += (self.max/(index+1))/seenToken[w]
        return score

    def feedTweet(self, tweetSentence):
        # process string into tokens
        for token in tweetSentence:
            if self.ignoreToken.get(token) is not None:
                continue
            if self.frequentList.get(token) is None:
                self.frequentList[token] = 1
            else:
                self.frequentList[token] += 1

    def sortFrequent(self):
        sorted_dict = OrderedDict(sorted(self.frequentList.items(), key=lambda x:x[1], reverse=True))
        self.frequentList = sorted_dict
        return sorted_dict

    def getTopValue(self, maximum):
        count = 0
        retList = []
        self.max = maximum
        for word in self.frequentList:
            retList.append(word)
            count += 1
            if count >= maximum:
                break

        self.topList = retList

tdb = TweetDatabase()

def readFile(filename):
    f = open(filename, 'r', encoding='utf-8')
    data = []
    for line in f:
        l = line.split("\t")
        tdb.addline(l)

    f.close()

readFile("train_tweets.txt")
tdb.processPattern()
sw = tdb.getMaximumWords()
s = tdb.prediction("RT: @handle: RT @handle: Apple won't repair Macs if owners are smokers http://bit.ly/6Qt49l")
print("finish!")
tdb.printdbInfo()
print("debug!")

def predictFile(filename):
    f = open(filename, 'r', encoding='utf-8')
    csv = open("predict.csv", 'w', encoding='utf-8')
    csv.write("Id,Predicted\n")
    id = 1
    for line in f:
        s = tdb.prediction(line)
        csv.write(str(id) + "," + str(s[0][0]) + "\n")
        id += 1
        print("==============> " + str(id))
    f.close()
    csv.close()

predictFile("test_tweets_unlabeled.txt")
print("------------------------------------")
