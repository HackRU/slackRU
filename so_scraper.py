import requests
from stackapi import StackAPI
import json
import re

stopwords =  " a about above across after  again  against  all  almost  alone  along  already  also  although\
  always  among  an am  and  another  any  anybody  anyone  anything  anywhere  are\
  area  areas  around  as  ask  asked  asking  asks  at  away  backing  backs  be\
  became  because  become  becomes  been  before  began  behind  being  beings  best\
  better  between  big  both  but  by   came  can  cannot  case  cases  certain  certainly\
  clear  clearly  come  could  d  did  differ  different  differently  do  does  done  down\
  down  downed  downing  downs  during  e  each  early  either  end  ended  ending  ends  enough\
  even  evenly  ever  every  everybody  everyone  everything  everywhere  f  face  faces  fact  facts\
  far  felt  few  find  finds  first  for  four  from  full  fully  further  furthered  furthering\
  furthers  g  gave  general  generally  get getting  gets  give  given  gives  go  going  good  goods  got\
   had  has  have  having  he  her  here  herself  high  high  high  higher  highest  him  himself  his\
  how  however  i  if  important  in  interest  interested  interesting  interests  into  is  it  its\
  itself  j  just  k  keep  keeps  kind  knew  know  known  knows  l  large  largely  last  later  latest\
  least  less  let  lets  like  likely  long  longer  longest  m  made  make  making  man  many  may  me mean\
  member  members  men  might  more  most  mostly  mr  mrs  much  must  my  myself  never  no  nobody  non\
  noone  not  now  nowhere    o  of  off on  once  one  only  or  our  out  over  p  per  perhaps  possible\
   put  puts  q  quite  r  rather  really  right  right  room  rooms  s  said  same  saw  say  says  see  seem\
  seemed  seeming  seems  sees  shall  she  should  since so  some  somebody  someone  something  somewhere such\
  sure  t than  that  the  their  them  then  there  therefore  these  they  thing  things  think  thinks  this\
  those  though  thought  thoughts   through  thus  to  today  together  too  took  toward  turn  turned  turning\
  turns  under  until  up  upon  us  use  used  uses    very   want  wanted  wanting  wants  was  way  ways  we  well\
  wells  went  were  what  when  where  whether  which  while  who  whole  whose  why  will  with  within  without  work\
  worked  working  works  would   year  years  yet  you  young  younger  youngest  your  yours" 
stopwords_set = set([s.strip() for s in stopwords.split(" ")]) #stopwords delimintated into a list

def scraper(message):  
    message = message.lower() #lowercases words
    message_list = message.split(" ", 30) #the length of search is limited to 30 words      
    keywords_list = message_list
    # keywords_list = [x for x in message_list if x not in stopwords_set]# long list of keywords
    tagStr= " ".join(keywords_list) #keywords joined by " "
    keywords_list = [w for w in keywords_list if w not in stopwords_set]
    SITE = StackAPI('stackoverflow')
    questions_dict = SITE.fetch("search/advanced", q=tagStr,  tagged=keywords_list, sort="relevance")
    return questions_dict['items'][:10]

def main():
    st = "how do i install linux on my computer :("
    lis = scraper(st)
    print(json.dumps(lis))

if __name__ == "__main__":
    main()
  
