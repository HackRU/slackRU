import requests
from stackapi import StackAPI


def scraper(message):  
	stopwords =  " a about above across after  again  against  all  almost  alone  along  already  also  although  always  among  an  and  another  any  anybody  anyone  anything  anywhere  are  area  areas  around  as  ask  asked  asking  asks  at  away  backing  backs  be  became  because  become  becomes  been  before  began  behind  being  beings  best  better  between  big  both  but  by   came  can  cannot  case  cases  certain  certainly  clear  clearly  come  could  d  did  differ  different  differently  do  does  done  down  down  downed  downing  downs  during  e  each  early  either  end  ended  ending  ends  enough  even  evenly  ever  every  everybody  everyone  everything  everywhere  f  face  faces  fact  facts  far  felt  few  find  finds  first  for  four  from  full  fully  further  furthered  furthering  furthers  g  gave  general  generally  get  gets  give  given  gives  go  going  good  goods  got   had  has  have  having  he  her  here  herself  high  high  high  higher  highest  him  himself  his  how  however  i  if  important  in  interest  interested  interesting  interests  into  is  it  its  itself  j  just  k  keep  keeps  kind  knew  know  known  knows  l  large  largely  last  later  latest  least  less  let  lets  like  likely  long  longer  longest  m  made  make  making  man  many  may  me  member  members  men  might  more  most  mostly  mr  mrs  much  must  my  myself  never  no  nobody  non  noone  not  now  nowhere    o  of  off on  once  one  only  or  our  out  over  p  per  perhaps  possible   put  puts  q  quite  r  rather  really  right  right  room  rooms  s  said  same  saw  say  says  see  seem  seemed  seeming  seems  sees  shall  she  should  since so  some  somebody  someone  something  somewhere such  sure  t than  that  the  their  them  then  there  therefore  these  they  thing  things  think  thinks  this  those  though  thought  thoughts   through  thus  to  today  together  too  took  toward  turn  turned  turning  turns  under  until  up  upon  us  use  used  uses    very   want  wanted  wanting  wants  was  way  ways  we  well  wells  went  were  what  when  where  whether  which  while  who  whole  whose  why  will  with  within  without  work  worked  working  works  would   year  years  yet  you  young  younger  youngest  your  yours" 
	msg_lwr = message.lower(); #lowercases words
	stopwords_set = set(stopwords.split(" ")) #stopwords delimintated into list
	message_list = msg_lwr.split(" ", 30) #the length of search is limited to 30 words  	
	keywords_list = [x for x in message_list if( x not in stopwords_set )]# long list of keywords

	tagStr= ";".join(keywords_list)
	print(tagStr);

	SITE = StackAPI("stackoverflow")
	questions_dict = SITE.fetch("search/advanced", tagged=tagStr, accepted=True)
#	print(type(questions_list))
	questions_list = questions_dict['items']

	abridged_list = [] #create empty list

	for this_dict in questions_list:
		if(this_dict['score'] > 5):
			abridged_list.append(this_dict)

		
	if len(abridged_list) > 10:
		abridged_list = abridged_list[:10] #slice
	print(abridged_list)
#	print(questions_list)

def main():
	st = "How do I find a Java  api"
	scraper(st)

if __name__ == "__main__":
	main()
  
